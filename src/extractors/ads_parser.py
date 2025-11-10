thonfrom __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .targeting_parser import TargetingInfo, parse_targeting
from .utils_region import normalize_region_stats

@dataclass
class ImpressionRange:
    lower_bound: int
    upper_bound: int

@dataclass
class SurfaceServingStat:
    surface_code: str
    surface_name: str
    impressions: ImpressionRange

@dataclass
class RegionStat:
    region_code: str
    region_name: str
    first_shown: str
    last_shown: str
    impressions: ImpressionRange
    surface_serving_stats: List[SurfaceServingStat]

@dataclass
class AdVariation:
    click_url: Optional[str]
    cta: Optional[str]
    description: Optional[str]
    image_url: Optional[str]

@dataclass
class AdRecord:
    ad_library_url: str
    advertiser_id: str
    advertiser_name: str
    creative_id: str
    format: str
    first_shown: str
    last_shown: str
    preview_url: Optional[str]
    start_url: Optional[str]
    region_stats: List[RegionStat]
    targeting: Optional[TargetingInfo]
    variations: List[AdVariation]

    def to_flat_dicts(self) -> List[Dict[str, Any]]:
        """
        Flatten nested ad information into a list of dicts suitable for tabular exports.
        Each combination of region / surface / variation becomes a separate row.
        """
        rows: List[Dict[str, Any]] = []

        base = {
            "adLibraryUrl": self.ad_library_url,
            "advertiserId": self.advertiser_id,
            "advertiserName": self.advertiser_name,
            "creativeId": self.creative_id,
            "format": self.format,
            "firstShown": self.first_shown,
            "lastShown": self.last_shown,
            "previewUrl": self.preview_url,
            "startUrl": self.start_url,
        }

        targeting_dict: Dict[str, Any] = {}
        if self.targeting:
            targeting_dict = {
                "targetingDemographicsTrue": ",".join(sorted(k for k, v in self.targeting.demographics.items() if v)),
                "targetingGeographyTrue": ",".join(sorted(k for k, v in self.targeting.geography.items() if v)),
                "targetingContextualTrue": ",".join(sorted(k for k, v in self.targeting.contextual.items() if v)),
                "targetingAdvertiserListTrue": ",".join(
                    sorted(k for k, v in self.targeting.advertiser_list.items() if v)
                ),
            }

        # Ensure we always have at least one region and variation to produce at least one row
        regions = self.region_stats or [
            RegionStat(
                region_code="",
                region_name="",
                first_shown="",
                last_shown="",
                impressions=ImpressionRange(0, 0),
                surface_serving_stats=[],
            )
        ]
        variations = self.variations or [AdVariation(None, None, None, None)]

        for region in regions:
            region_dict = {
                "regionCode": region.region_code,
                "regionName": region.region_name,
                "regionFirstShown": region.first_shown,
                "regionLastShown": region.last_shown,
                "regionImpressionsLower": region.impressions.lower_bound,
                "regionImpressionsUpper": region.impressions.upper_bound,
            }

            surfaces = region.surface_serving_stats or [
                SurfaceServingStat(
                    surface_code="",
                    surface_name="",
                    impressions=ImpressionRange(0, 0),
                )
            ]

            for surface in surfaces:
                surface_dict = {
                    "surfaceCode": surface.surface_code,
                    "surfaceName": surface.surface_name,
                    "surfaceImpressionsLower": surface.impressions.lower_bound,
                    "surfaceImpressionsUpper": surface.impressions.upper_bound,
                }

                for variation in variations:
                    variation_dict = {
                        "variationClickUrl": variation.click_url,
                        "variationCta": variation.cta,
                        "variationDescription": variation.description,
                        "variationImageUrl": variation.image_url,
                    }

                    row: Dict[str, Any] = {}
                    row.update(base)
                    row.update(region_dict)
                    row.update(surface_dict)
                    row.update(targeting_dict)
                    row.update(variation_dict)
                    rows.append(row)

        return rows

def _parse_impression_range(impressions_raw: Dict[str, Any] | None) -> ImpressionRange:
    if not impressions_raw:
        return ImpressionRange(lower_bound=0, upper_bound=0)

    lower = impressions_raw.get("lowerBound", 0) or 0
    upper = impressions_raw.get("upperBound", 0) or 0
    try:
        lower_int = int(lower)
        upper_int = int(upper)
    except (TypeError, ValueError):
        lower_int, upper_int = 0, 0

    return ImpressionRange(lower_bound=lower_int, upper_bound=upper_int)

def _parse_surface_stats(surface_stats_raw: List[Dict[str, Any]] | None) -> List[SurfaceServingStat]:
    stats: List[SurfaceServingStat] = []
    if not surface_stats_raw:
        return stats

    for item in surface_stats_raw:
        impressions_raw = item.get("impressions", {})
        stats.append(
            SurfaceServingStat(
                surface_code=str(item.get("surfaceCode", "")),
                surface_name=str(item.get("surfaceName", "")),
                impressions=_parse_impression_range(impressions_raw),
            )
        )
    return stats

def _parse_region_stats(region_stats_raw: List[Dict[str, Any]] | None) -> List[RegionStat]:
    stats: List[RegionStat] = []
    if not region_stats_raw:
        return stats

    for item in region_stats_raw:
        impressions_raw = item.get("impressions", {})
        surface_stats_raw = item.get("surfaceServingStats", [])

        stats.append(
            RegionStat(
                region_code=str(item.get("regionCode", "")),
                region_name=str(item.get("regionName", "")),
                first_shown=str(item.get("firstShown", "")),
                last_shown=str(item.get("lastShown", "")),
                impressions=_parse_impression_range(impressions_raw),
                surface_serving_stats=_parse_surface_stats(surface_stats_raw),
            )
        )

    # Use utility function to normalize / aggregate if needed
    return normalize_region_stats(stats)

def _parse_variations(variations_raw: List[Dict[str, Any]] | None) -> List[AdVariation]:
    variations: List[AdVariation] = []
    if not variations_raw:
        return variations

    for item in variations_raw:
        variations.append(
            AdVariation(
                click_url=item.get("clickUrl"),
                cta=item.get("cta"),
                description=item.get("description"),
                image_url=item.get("imageUrl"),
            )
        )

    return variations

def parse_ads(raw_ads: List[Dict[str, Any]]) -> List[AdRecord]:
    """
    Convert a list of raw ad dictionaries (as returned from a Transparency Center export)
    into a normalized list of AdRecord instances.
    """
    parsed: List[AdRecord] = []

    for idx, raw in enumerate(raw_ads):
        try:
            ad = AdRecord(
                ad_library_url=str(raw.get("adLibraryUrl", "")),
                advertiser_id=str(raw.get("advertiserId", "")),
                advertiser_name=str(raw.get("advertiserName", "")),
                creative_id=str(raw.get("creativeId", "")),
                format=str(raw.get("format", "")),
                first_shown=str(raw.get("firstShown", "")),
                last_shown=str(raw.get("lastShown", "")),
                preview_url=raw.get("previewUrl"),
                start_url=raw.get("startUrl"),
                region_stats=_parse_region_stats(raw.get("regionStats")),
                targeting=parse_targeting(raw.get("targeting")),
                variations=_parse_variations(raw.get("variations")),
            )
            parsed.append(ad)
        except Exception as exc:  # pragma: no cover - defensive
            import logging

            logging.exception("Failed to parse ad at index %d: %s", idx, exc)

    return parsed