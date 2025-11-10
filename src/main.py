import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Support both "python -m src.main" and "python src/main.py"
try:  # pragma: no cover - import robustness
    from .extractors.google_ads_parser import scrape_advertiser_ads
    from .extractors.helpers import load_json_file, setup_logger
    from .outputs.exporters import export_records
except ImportError:  # pragma: no cover
    from extractors.google_ads_parser import scrape_advertiser_ads
    from extractors.helpers import load_json_file, setup_logger
    from outputs.exporters import export_records

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Google Ads Transparency Center scraper"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Path to JSON file describing advertisers to scrape.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path (JSON or CSV based on extension). "
             "If omitted, defaults to ./data/output.json",
    )
    parser.add_argument(
        "--settings",
        "-s",
        type=str,
        default=None,
        help="Optional path to settings JSON (e.g. src/config/settings.example.json).",
    )
    parser.add_argument(
        "--max-ads-per-advertiser",
        type=int,
        default=None,
        help="Optional limit on number of ads to extract per advertiser.",
    )
    return parser.parse_args(argv)

def resolve_output_path(
    cli_output: Optional[str], settings: Dict[str, Any]
) -> Path:
    if cli_output:
        return Path(cli_output).expanduser().resolve()

    output_dir = settings.get("output_dir", "data")
    output_filename = settings.get("output_filename", "output.json")
    return Path(output_dir, output_filename).expanduser().resolve()

def load_settings(path: Optional[str], logger: logging.Logger) -> Dict[str, Any]:
    if not path:
        logger.info("No settings file provided; using defaults.")
        return {}

    settings_path = Path(path).expanduser()
    if not settings_path.exists():
        logger.warning("Settings file %s not found; using defaults.", settings_path)
        return {}

    try:
        settings = load_json_file(settings_path)
        if not isinstance(settings, dict):
            logger.warning(
                "Settings file %s did not contain a JSON object; ignoring.", settings_path
            )
            return {}
        return settings
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to read settings file %s: %s", settings_path, exc)
        return {}

def normalize_input_payload(payload: Any) -> List[Dict[str, Any]]:
    """
    Normalize the user-provided input JSON into a list of advertiser descriptors.

    Supported shapes:
      - {"advertisers": [ ... ]}
      - [ ... ] (list of advertisers)
      - single advertiser object -> wrapped into a list
    """
    if isinstance(payload, dict) and "advertisers" in payload:
        advertisers = payload["advertisers"]
    elif isinstance(payload, list):
        advertisers = payload
    else:
        advertisers = [payload]

    normalized: List[Dict[str, Any]] = []
    for idx, item in enumerate(advertisers):
        if not isinstance(item, dict):
            raise ValueError(
                f"Advertiser at index {idx} must be a JSON object, got {type(item)}."
            )
        normalized.append(item)
    return normalized

def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    logger = setup_logger("google_ads_scraper")

    try:
        input_path = Path(args.input).expanduser().resolve()
        if not input_path.exists():
            logger.error("Input file %s does not exist.", input_path)
            return 1

        settings = load_settings(args.settings, logger)
        output_path = resolve_output_path(args.output, settings)
        logger.info("Using output path: %s", output_path)

        logger.info("Loading input from %s", input_path)
        raw_input_payload = load_json_file(input_path)
        advertisers = normalize_input_payload(raw_input_payload)
        logger.info("Loaded %d advertiser descriptor(s).", len(advertisers))

        all_records: List[Dict[str, Any]] = []
        for idx, advertiser in enumerate(advertisers, start=1):
            logger.info("Scraping advertiser %d/%d ...", idx, len(advertisers))
            try:
                records = scrape_advertiser_ads(
                    advertiser_descriptor=advertiser,
                    max_ads=args.max_ads_per_advertiser,
                    logger=logger,
                )
                logger.info(
                    "Advertiser %d yielded %d ad record(s).", idx, len(records)
                )
                all_records.extend(records)
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Error while scraping advertiser %d: %s", idx, exc
                )

        if not all_records:
            logger.warning("No ad records were extracted; nothing to export.")
        else:
            export_records(all_records, output_path, logger)

        logger.info("Done. Extracted %d ad record(s).", len(all_records))
        return 0
    except KeyboardInterrupt:
        logger.error("Interrupted by user.")
        return 130
    except Exception as exc:  # noqa: BLE001
        logger.exception("Fatal error: %s", exc)
        return 1

if __name__ == "__main__":
    sys.exit(main())