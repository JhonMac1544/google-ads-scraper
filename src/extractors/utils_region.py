thonfrom __future__ import annotations

from typing import Any, Dict, Iterable, List

def normalize_region_stats(region_stats: Iterable[Any]) -> List[Any]:
    """
    Normalize and aggregate regional statistics.

    This function:
    - Groups regions by (region_code, region_name).
    - Sums impression ranges across entries for the same region.
    - Concatenates surface stats and merges surfaces with the same code.

    The function operates in-place on the region objects that are passed in,
    but also returns a new list containing the aggregated regions.
    """
    by_key: Dict[tuple[str, str], Any] = {}

    for region in region_stats:
        key = (getattr(region, "region_code", ""), getattr(region, "region_name", ""))
        existing = by_key.get(key)

        if existing is None:
            by_key[key] = region
        else:
            impressions = getattr(region, "impressions", None)
            existing_impressions = getattr(existing, "impressions", None)

            if impressions and existing_impressions:
                existing_impressions.lower_bound += getattr(impressions, "lower_bound", 0)
                existing_impressions.upper_bound += getattr(impressions, "upper_bound", 0)

            # Prefer earliest first_shown and latest last_shown
            region_first = getattr(region, "first_shown", "")
            region_last = getattr(region, "last_shown", "")
            existing_first = getattr(existing, "first_shown", "")
            existing_last = getattr(existing, "last_shown", "")

            if region_first and (not existing_first or region_first < existing_first):
                existing.first_shown = region_first
            if region_last and (not existing_last or region_last > existing_last):
                existing.last_shown = region_last

            # Merge surfaces
            existing_surfaces = list(getattr(existing, "surface_serving_stats", []) or [])
            new_surfaces = list(getattr(region, "surface_serving_stats", []) or [])
            existing_surfaces.extend(new_surfaces)
            existing.surface_serving_stats = existing_surfaces

    # Merge surfaces with the same surface_code inside each region
    for region in by_key.values():
        merged_surfaces: Dict[str, Any] = {}
        for surface in getattr(region, "surface_serving_stats", []) or []:
            code = getattr(surface, "surface_code", "")
            existing_surface = merged_surfaces.get(code)
            if existing_surface is None:
                merged_surfaces[code] = surface
            else:
                impressions = getattr(surface, "impressions", None)
                existing_impressions = getattr(existing_surface, "impressions", None)
                if impressions and existing_impressions:
                    existing_impressions.lower_bound += getattr(impressions, "lower_bound", 0)
                    existing_impressions.upper_bound += getattr(impressions, "upper_bound", 0)

        region.surface_serving_stats = list(merged_surfaces.values())

    # Return a stable order
    return sorted(by_key.values(), key=lambda r: (getattr(r, "region_code", ""), getattr(r, "region_name", "")))