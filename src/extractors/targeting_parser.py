thonfrom __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class TargetingInfo:
    """
    Normalized representation of targeting categories for an ad.
    The keys are category codes and the values indicate whether the category is active.
    """
    demographics: Dict[str, bool]
    geography: Dict[str, bool]
    contextual: Dict[str, bool]
    advertiser_list: Dict[str, bool]

def _ensure_bool_map(raw: Any) -> Dict[str, bool]:
    """
    Convert an arbitrary mapping into a string->bool dictionary.
    Non-mapping inputs result in an empty dict.
    """
    if not isinstance(raw, dict):
        return {}
    result: Dict[str, bool] = {}
    for key, value in raw.items():
        result[str(key)] = bool(value)
    return result

def parse_targeting(targeting_raw: Dict[str, Any] | None) -> Optional[TargetingInfo]:
    """
    Parse the raw "targeting" structure from the Transparency Center into a TargetingInfo object.
    The expected input follows the structure shown in the README example.
    """
    if not targeting_raw:
        return None

    category = targeting_raw.get("targetingCategory", {})

    return TargetingInfo(
        demographics=_ensure_bool_map(category.get("demographics")),
        geography=_ensure_bool_map(category.get("geography")),
        contextual=_ensure_bool_map(category.get("contextual")),
        advertiser_list=_ensure_bool_map(category.get("advertiserList")),
    )