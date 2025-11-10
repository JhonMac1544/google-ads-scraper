import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

def _detect_format_from_extension(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".csv":
        return "csv"
    return "json"

def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def export_to_json(
    records: Iterable[Dict[str, Any]],
    output_path: Path,
    logger: Optional[logging.Logger] = None,
) -> None:
    _ensure_parent_dir(output_path)
    data = list(records)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if logger:
        logger.info("Wrote %d record(s) to JSON file %s", len(data), output_path)

def _flatten_record_for_csv(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten nested structures for CSV by JSON-encoding complex values.
    """
    flat: Dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, (str, int, float)) or value is None:
            flat[key] = value
        else:
            flat[key] = json.dumps(value, ensure_ascii=False)
    return flat

def export_to_csv(
    records: Iterable[Dict[str, Any]],
    output_path: Path,
    logger: Optional[logging.Logger] = None,
) -> None:
    _ensure_parent_dir(output_path)
    data: List[Dict[str, Any]] = []
    for rec in records:
        data.append(_flatten_record_for_csv(rec))

    if not data:
        # Still create an empty file with no header
        output_path.touch()
        if logger:
            logger.warning("No records to export; created empty CSV %s", output_path)
        return

    fieldnames = sorted({k for rec in data for k in rec.keys()})
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    if logger:
        logger.info("Wrote %d record(s) to CSV file %s", len(data), output_path)

def export_records(
    records: Iterable[Dict[str, Any]],
    output_path: Path,
    logger: Optional[logging.Logger] = None,
) -> None:
    fmt = _detect_format_from_extension(output_path)
    if fmt == "csv":
        export_to_csv(records, output_path, logger)
    else:
        export_to_json(records, output_path, logger)