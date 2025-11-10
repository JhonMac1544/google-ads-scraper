import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

def setup_logger(name: str = "google_ads_scraper") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def http_get(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 20.0,
    retries: int = 3,
    backoff_factor: float = 0.5,
    logger: Optional[logging.Logger] = None,
) -> requests.Response:
    """
    Perform an HTTP GET with basic retry and backoff.

    Raises requests.HTTPError if the final attempt fails with non-2xx status.
    """
    sess = requests.Session()
    attempt = 0
    last_exc: Optional[Exception] = None

    while attempt < retries:
        attempt += 1
        try:
            if logger:
                logger.debug("GET %s (attempt %d/%d)", url, attempt, retries)
            resp = sess.get(url, params=params, headers=headers, timeout=timeout)
            if 200 <= resp.status_code < 300:
                return resp
            msg = f"GET {url} returned HTTP {resp.status_code}"
            if logger:
                logger.warning(msg)
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if logger:
                logger.warning(
                    "GET %s failed on attempt %d/%d: %s",
                    url,
                    attempt,
                    retries,
                    exc,
                )
            if attempt < retries:
                sleep_time = backoff_factor * (2 ** (attempt - 1))
                time.sleep(sleep_time)

    assert last_exc is not None
    if logger:
        logger.error("Failed to GET %s after %d attempts.", url, retries)
    raise last_exc

def load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)

def safe_get(d: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely traverse nested dictionaries.

    Example:
        safe_get(obj, "a", "b", "c", default=None) -> obj["a"]["b"]["c"] or default
    """
    cur: Any = d
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur