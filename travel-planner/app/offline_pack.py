"""Offline trip pack serialization generating a self-contained offline travel document."""

import datetime
from typing import Any, Dict, List, Optional
import json


def generate_offline_trip_pack(
    trip_name: str,
    destination: str,
    duration_days: int,
    itinerary_days: List[Dict[str, Any]],
    budget_summary: Optional[Dict[str, Any]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    essential_contacts: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Compile a complete, offline-ready travel pack with full addresses, map links, and timing.

    Note: Offline pack contains direct links and local addresses. Links require data connection
    when opening outside the offline viewer, which is explicitly noted in limitations.
    """
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    pack = {
        "offline_pack_version": "1.0",
        "trip_name": trip_name,
        "destination": destination,
        "duration_days": duration_days,
        "dates": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "synchronized_at": now,
        "connectivity_notice": (
            "This offline trip pack is fully viewable without internet connection. "
            "Opening external Google Maps directions, official website links, or live transit updates "
            "will require active data connection."
        ),
        "emergency_contacts": essential_contacts or {
            "emergency_police": "110 (Japan) / 112 (EU/Global) / 911 (US)",
            "medical_ambulance": "119 (Japan) / 112 (EU/Global)",
            "embassy_contact": "Consult your local consular service",
        },
        "budget_summary": budget_summary or {},
        "days": itinerary_days,
    }
    return pack
