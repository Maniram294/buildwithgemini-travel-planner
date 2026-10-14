"""Verified place links, Google Maps search/directions URL constructors, and evidence metadata."""

import datetime
from typing import Any, Dict, List, Optional
import urllib.parse


def build_google_maps_search_url(place_name: str, address: Optional[str] = None) -> str:
    """Build a valid URL-encoded Google Maps search fallback URL."""
    query = f"{place_name}, {address}" if address else place_name
    encoded_query = urllib.parse.quote(query.strip())
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"


def build_google_maps_directions_url(
    destination_name: str,
    origin_name: Optional[str] = None,
    destination_address: Optional[str] = None,
    origin_address: Optional[str] = None,
    travel_mode: str = "transit",
) -> str:
    """Build a valid URL-encoded Google Maps directions URL between consecutive stops."""
    dest_str = f"{destination_name}, {destination_address}" if destination_address else destination_name
    encoded_dest = urllib.parse.quote(dest_str.strip())

    base_url = f"https://www.google.com/maps/dir/?api=1&destination={encoded_dest}"
    if origin_name:
        orig_str = f"{origin_name}, {origin_address}" if origin_address else origin_name
        base_url += f"&origin={urllib.parse.quote(orig_str.strip())}"

    mode = travel_mode.lower().strip()
    if mode in ["walking", "transit", "driving", "bicycling"]:
        base_url += f"&travelmode={mode}"

    return base_url


def validate_web_url(url: Optional[str]) -> Optional[str]:
    """Validate that a URL uses safe HTTP or HTTPS scheme and is non-empty."""
    if not url or not isinstance(url, str):
        return None
    url_clean = url.strip()
    if url_clean.startswith("https://") or url_clean.startswith("http://"):
        return url_clean
    return None


def format_evidence_record(
    entity_name: str,
    source: str,
    verification_status: str,  # "verified", "estimated", "needs_confirmation", "unavailable", "restricted"
    details: Dict[str, Any],
    limitations: Optional[str] = None,
    checked_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized evidence provenance and freshness record."""
    timestamp = checked_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "entity_name": entity_name,
        "source": source,
        "verification_status": verification_status,
        "checked_at": timestamp,
        "details": details,
        "limitations": limitations,
    }
