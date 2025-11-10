import json
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

try:  # pragma: no cover - import robustness
    from .helpers import http_get, safe_get
except ImportError:  # pragma: no cover
    from helpers import http_get, safe_get

GOOGLE_ADS_TRANSPARENCY_HOST = "adstransparency.google.com"

@dataclass
class ImpressionRange:
    lowerBound: int
    upperBound: int

@dataclass
class SurfaceServingStats:
    surfaceCode: str
    surfaceName: str
    impressions: ImpressionRange

@dataclass
class RegionStats:
    regionCode: str
    regionName: str
    firstShown: str
    lastShown: str
    impressions: ImpressionRange
    surfaceServingStats: List[SurfaceServingStats]

@dataclass
class Variation:
    clickUrl: Optional[str]
    cta: Optional[str]
    description: Optional[str]
    imageUrl: Optional[str]

@dataclass
class AdRecord:
    adLibraryUrl: str
    advertiserId: str
    advertiserName: Optional[str]
    creativeId: str
    firstShown: Optional[str]
    lastShown: Optional[str]
    format: Optional[str]
    previewUrl: Optional[str]
    regionStats: List[RegionStats]
    targeting: Dict[str, Any]
    variations: List[Variation]
    startUrl: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        def serialize(obj: Any) -> Any:
            if isinstance(obj, list):
                return [serialize(x) for x in obj]
            if isinstance(obj, ImpressionRange):
                return {
                    "lowerBound": obj.lowerBound,
                    "upperBound": obj.upperBound,
                }
            if isinstance(obj, SurfaceServingStats):
                return {
                    "surfaceCode": obj.surfaceCode,
                    "surfaceName": obj.surfaceName,
                    "impressions": serialize(obj.impressions),
                }
            if isinstance(obj, RegionStats):
                return {
                    "regionCode": obj.regionCode,
                    "regionName": obj.regionName,
                    "firstShown": obj.firstShown,
                    "lastShown": obj.lastShown,
                    "impressions": serialize(obj.impressions),
                    "surfaceServingStats": serialize(obj.surfaceServingStats),
                }
            if isinstance(obj, Variation):
                return asdict(obj)
            return obj

        base = {
            "adLibraryUrl": self.adLibraryUrl,
            "advertiserId": self.advertiserId,
            "advertiserName": self.advertiserName,
            "creativeId": self.creativeId,
            "firstShown": self.firstShown,
            "lastShown": self.lastShown,
            "format": self.format,
            "previewUrl": self.previewUrl,
            "regionStats": serialize(self.regionStats),
            "targeting": self.targeting,
            "variations": serialize(self.variations),
            "startUrl": self.startUrl,
        }
        return base

def _extract_advertiser_id_from_url(url: str) -> Optional[str]:
    """
    Try to extract an advertiser ID from a Transparency Center URL.

    Supports URLs like:
        https://adstransparency.google.com/advertiser/AR123456789
    """
    try:
        parsed = urlparse(url)
        if GOOGLE_ADS_TRANSPARENCY_HOST not in parsed.netloc:
            return None
        parts = [p for p in parsed.path.split("/") if p]
        if "advertiser" in parts:
            idx = parts.index("advertiser")
            if idx + 1 < len(parts):
                return parts[idx + 1]
    except Exception:  # noqa: BLE001
        return None
    return None

def _build_ad_library_url(advertiser_id: str, creative_id: str) -> str:
    return (
        f"https://{GOOGLE_ADS_TRANSPARENCY_HOST}/advertiser/"
        f"{advertiser_id}/creative/{creative_id}"
    )

def _parse_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip()
    # Already ISO
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return value
    except Exception:  # noqa: BLE001
        return None
    # Try some common formats
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return value

def _parse_impressions_range(
    lower: Optional[str], upper: Optional[str]
) -> ImpressionRange:
    def to_int(val: Optional[str]) -> int:
        if not val:
            return 0
        try:
            return int(val.replace(",", "").strip())
        except ValueError:
            return 0

    return ImpressionRange(lowerBound=to_int(lower), upperBound=to_int(upper))

def _parse_html_creative_blocks(
    html: str,
    advertiser_id: str,
    start_url: Optional[str],
    logger: Optional[logging.Logger],
) -> List[AdRecord]:
    """
    Parse the Transparency Center HTML response into AdRecord objects.

    This parser is intentionally defensive and uses data-* attributes that
    commonly appear in ad gallery markup. It will gracefully skip elements
    that don't provide enough information.
    """
    soup = BeautifulSoup(html, "html.parser")
    records: List[AdRecord] = []

    creative_blocks = soup.select("[data-creative-id]")
    if logger:
        logger.info("Found %d creative block(s) in HTML.", len(creative_blocks))

    for block in creative_blocks:
        creative_id = block.get("data-creative-id")
        if not creative_id:
            continue

        advertiser_name = block.get("data-advertiser-name")
        ad_format = block.get("data-format") or block.get("data-ad-format")
        preview_url = block.get("data-preview-url") or block.get("data-image-url")
        first_shown = _parse_date(block.get("data-first-shown"))
        last_shown = _parse_date(block.get("data-last-shown"))

        # Region stats: assume nested elements with data-region-code, etc.
        region_stats: List[RegionStats] = []
        for region in block.select("[data-region-code]"):
            region_code = region.get("data-region-code") or ""
            region_name = region.get("data-region-name") or region_code
            region_first = _parse_date(region.get("data-first-shown") or first_shown)
            region_last = _parse_date(region.get("data-last-shown") or last_shown)

            impressions_lower = region.get("data-impressions-lower")
            impressions_upper = region.get("data-impressions-upper")
            impressions = _parse_impressions_range(impressions_lower, impressions_upper)

            surfaces: List[SurfaceServingStats] = []
            for surface in region.select("[data-surface-code]"):
                s_code = surface.get("data-surface-code") or ""
                s_name = surface.get("data-surface-name") or s_code
                s_lower = surface.get("data-impressions-lower")
                s_upper = surface.get("data-impressions-upper")
                surfaces.append(
                    SurfaceServingStats(
                        surfaceCode=s_code,
                        surfaceName=s_name,
                        impressions=_parse_impressions_range(s_lower, s_upper),
                    )
                )

            region_stats.append(
                RegionStats(
                    regionCode=region_code,
                    regionName=region_name,
                    firstShown=region_first or "",
                    lastShown=region_last or "",
                    impressions=impressions,
                    surfaceServingStats=surfaces,
                )
            )

        # Targeting: try to parse any JSON payload embedded in data-targeting or a child script.
        targeting: Dict[str, Any] = {}
        targeting_attr = block.get("data-targeting-json")
        if targeting_attr:
            try:
                targeting = json.loads(targeting_attr)
            except json.JSONDecodeError:
                targeting = {}
        else:
            targeting_script = block.find("script", attrs={"type": "application/json"})
            if targeting_script and targeting_script.string:
                try:
                    targeting = json.loads(targeting_script.string)
                except json.JSONDecodeError:
                    targeting = {}

        # Variations: assume child elements with data-click-url etc.
        variations: List[Variation] = []
        for var in block.select("[data-variation]"):
            variations.append(
                Variation(
                    clickUrl=var.get("data-click-url"),
                    cta=var.get("data-cta"),
                    description=var.get("data-description"),
                    imageUrl=var.get("data-image-url") or preview_url,
                )
            )

        record = AdRecord(
            adLibraryUrl=_build_ad_library_url(advertiser_id, creative_id),
            advertiserId=advertiser_id,
            advertiserName=advertiser_name,
            creativeId=creative_id,
            firstShown=first_shown,
            lastShown=last_shown,
            format=ad_format,
            previewUrl=preview_url,
            regionStats=region_stats,
            targeting=targeting,
            variations=variations,
            startUrl=start_url,
        )
        records.append(record)

    return records

def _guess_gallery_url(advertiser_id: str) -> str:
    # This function guesses a gallery URL for a given advertiser.
    # Transparency Center URLs can change; this function is intentionally generic.
    return f"https://{GOOGLE_ADS_TRANSPARENCY_HOST}/advertiser/{advertiser_id}"

def scrape_advertiser_ads(
    advertiser_descriptor: Dict[str, Any],
    *,
    max_ads: Optional[int] = None,
    logger: Optional[logging.Logger] = None,
) -> List[Dict[str, Any]]:
    """
    Scrape ads for a single advertiser descriptor.

    The descriptor may contain:
      - "advertiserId": explicit advertiser ID
      - "startUrl": URL pointing to the Ads Transparency Center
      - "htmlSnapshot": raw HTML (used for offline parsing/testing)

    Returns a list of ad dictionaries ready for export.
    """
    if not isinstance(advertiser_descriptor, dict):
        raise ValueError("advertiser_descriptor must be a dictionary.")

    start_url: Optional[str] = advertiser_descriptor.get("startUrl")

    advertiser_id = advertiser_descriptor.get("advertiserId")
    if not advertiser_id and start_url:
        advertiser_id = _extract_advertiser_id_from_url(start_url)

    if not advertiser_id:
        raise ValueError(
            "Advertiser descriptor must include 'advertiserId' or a "
            "Transparency Center 'startUrl'."
        )

    if logger:
        logger.info(
            "Scraping advertiser %s (startUrl=%s)", advertiser_id, start_url or "N/A"
        )

    # Offline / test path: parse provided HTML snapshot
    html_snapshot = advertiser_descriptor.get("htmlSnapshot")
    if html_snapshot:
        if logger:
            logger.info("Using provided HTML snapshot for advertiser %s.", advertiser_id)
        records = _parse_html_creative_blocks(html_snapshot, advertiser_id, start_url, logger)
    else:
        # Online path: fetch gallery HTML.
        gallery_url = start_url or _guess_gallery_url(advertiser_id)
        if logger:
            logger.info("Fetching gallery HTML from %s", gallery_url)
        resp = http_get(gallery_url, logger=logger)
        resp.encoding = resp.encoding or "utf-8"
        records = _parse_html_creative_blocks(resp.text, advertiser_id, gallery_url, logger)

    if max_ads is not None and max_ads >= 0:
        records = records[:max_ads]

    return [rec.to_dict() for rec in records]

def parse_ads_from_raw_api_payload(
    payload: Dict[str, Any],
    *,
    advertiser_id: str,
    start_url: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Optional helper for callers that already have a structured JSON payload
    from an internal or cached API or data source.

    This function expects a payload-like:
      {
        "creatives": [
          {
            "creativeId": "...",
            "advertiserName": "...",
            "firstShown": "2023-07-04",
            "lastShown": "2024-05-17",
            "format": "IMAGE",
            "previewUrl": "...",
            "regionStats": [...],
            "targeting": {...},
            "variations": [...]
          }
        ]
      }
    """
    creatives = safe_get(payload, "creatives", default=[])
    records: List[AdRecord] = []

    for c in creatives:
        creative_id = c.get("creativeId")
        if not creative_id:
            continue

        region_stats: List[RegionStats] = []
        for r in c.get("regionStats", []):
            impressions_payload = r.get("impressions") or {}
            impressions = _parse_impressions_range(
                str(impressions_payload.get("lowerBound")),
                str(impressions_payload.get("upperBound")),
            )

            surfaces: List[SurfaceServingStats] = []
            for s in r.get("surfaceServingStats", []):
                s_imp = s.get("impressions") or {}
                surfaces.append(
                    SurfaceServingStats(
                        surfaceCode=s.get("surfaceCode", ""),
                        surfaceName=s.get("surfaceName", s.get("surfaceCode", "")),
                        impressions=_parse_impressions_range(
                            str(s_imp.get("lowerBound")),
                            str(s_imp.get("upperBound")),
                        ),
                    )
                )

            region_stats.append(
                RegionStats(
                    regionCode=r.get("regionCode", ""),
                    regionName=r.get("regionName", r.get("regionCode", "")),
                    firstShown=_parse_date(r.get("firstShown")),
                    lastShown=_parse_date(r.get("lastShown")),
                    impressions=impressions,
                    surfaceServingStats=surfaces,
                )
            )

        variations: List[Variation] = []
        for v in c.get("variations", []):
            variations.append(
                Variation(
                    clickUrl=v.get("clickUrl"),
                    cta=v.get("cta"),
                    description=v.get("description"),
                    imageUrl=v.get("imageUrl"),
                )
            )

        record = AdRecord(
            adLibraryUrl=_build_ad_library_url(advertiser_id, creative_id),
            advertiserId=advertiser_id,
            advertiserName=c.get("advertiserName"),
            creativeId=creative_id,
            firstShown=_parse_date(c.get("firstShown")),
            lastShown=_parse_date(c.get("lastShown")),
            format=c.get("format"),
            previewUrl=c.get("previewUrl"),
            regionStats=region_stats,
            targeting=c.get("targeting") or {},
            variations=variations,
            startUrl=start_url,
        )
        records.append(record)

    return [r.to_dict() for r in records]