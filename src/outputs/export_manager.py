thonfrom __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Iterable, List

from extractors.ads_parser import AdRecord

class ExportManager:
    """
    Responsible for exporting parsed ad records into different output formats.
    """

    def __init__(self, ads: Iterable[AdRecord]) -> None:
        self._ads: List[AdRecord] = list(ads)

    def _rows(self) -> List[dict]:
        rows: List[dict] = []
        for ad in self._ads:
            rows.extend(ad.to_flat_dicts())
        logging.debug("Prepared %d flattened rows for export.", len(rows))
        return rows

    def export_json(self, path: Path) -> None:
        rows = self._rows()
        with path.open("w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        logging.info("Exported %d rows to JSON at %s", len(rows), path)

    def export_csv(self, path: Path) -> None:
        rows = self._rows()
        if not rows:
            logging.warning("No rows to export to CSV.")
            with path.open("w", encoding="utf-8", newline="") as f:
                f.write("")
            return

        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        logging.info("Exported %d rows to CSV at %s", len(rows), path)

    def export_xml(self, path: Path) -> None:
        from xml.etree.ElementTree import Element, SubElement, ElementTree

        rows = self._rows()
        root = Element("ads")

        for row in rows:
            ad_el = SubElement(root, "ad")
            for key, value in row.items():
                child = SubElement(ad_el, key)
                child.text = "" if value is None else str(value)

        tree = ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)
        logging.info("Exported %d rows to XML at %s", len(rows), path)

    def export_html(self, path: Path) -> None:
        rows = self._rows()
        if not rows:
            html = "<html><body><p>No data available.</p></body></html>"
            with path.open("w", encoding="utf-8") as f:
                f.write(html)
            logging.info("Exported empty HTML table to %s", path)
            return

        headers = list(rows[0].keys())

        def _escape(value: str) -> str:
            return (
                value.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )

        html_parts = [
            "<html>",
            "<head><meta charset='utf-8'><title>Google Ads Export</title></head>",
            "<body>",
            "<table border='1' cellspacing='0' cellpadding='4'>",
            "<thead><tr>",
        ]
        for header in headers:
            html_parts.append(f"<th>{_escape(str(header))}</th>")
        html_parts.append("</tr></thead><tbody>")

        for row in rows:
            html_parts.append("<tr>")
            for header in headers:
                value = row.get(header, "")
                html_parts.append(f"<td>{_escape('' if value is None else str(value))}</td>")
            html_parts.append("</tr>")

        html_parts.extend(["</tbody></table>", "</body>", "</html>"])

        with path.open("w", encoding="utf-8") as f:
            f.write("".join(html_parts))

        logging.info("Exported %d rows to HTML at %s", len(rows), path)