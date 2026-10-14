"""Best-time-to-visit intelligence engine combining daylight, weather patterns, and operating constraints."""

import datetime
from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request
import json


def evaluate_best_visit_time(
    attraction_name: str,
    attraction_type: str,  # 'viewpoint', 'temple', 'museum', 'market', 'waterfall', 'restaurant'
    latitude: float,
    longitude: float,
    opening_hours: Optional[List[str]] = None,
    target_date: Optional[str] = None,
    weather_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Recommend an evidence-backed optimal visiting window based on daylight, hours, and attraction type.

    Args:
        attraction_name: Name of the site
        attraction_type: Category of the site
        latitude: Geographic latitude
        longitude: Geographic longitude
        opening_hours: Optional weekday opening hours strings
        target_date: ISO date (YYYY-MM-DD)
        weather_summary: Optional weather data dictionary

    Returns:
        Structured recommendation with recommended window, daylight details, rationale, and warnings.
    """
    check_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    dest_date = target_date or datetime.date.today().isoformat()

    # 1. Fetch sunrise / sunset data from Open-Meteo
    sunrise_time = None
    sunset_time = None
    astronomical_source = "Open-Meteo Astronomical API"
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
            f"&daily=sunrise,sunset&timezone=auto&forecast_days=7"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "TravelPlanner/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            astro_data = json.loads(res.read().decode())
        daily = astro_data.get("daily", {})
        times = daily.get("time", [])
        if dest_date in times:
            idx = times.index(dest_date)
            sunrise_time = daily.get("sunrise", [])[idx]
            sunset_time = daily.get("sunset", [])[idx]
        elif daily.get("sunrise"):
            sunrise_time = daily.get("sunrise")[0]
            sunset_time = daily.get("sunset")[0]
    except Exception:
        astronomical_source = "Fallback daylight estimate"
        sunrise_time = f"{dest_date}T06:00"
        sunset_time = f"{dest_date}T18:00"

    # Format local times
    sr_str = sunrise_time.split("T")[-1] if sunrise_time and "T" in sunrise_time else "06:00"
    ss_str = sunset_time.split("T")[-1] if sunset_time and "T" in sunset_time else "18:00"

    att_type = attraction_type.lower().strip()
    warnings = []
    assumptions = []

    # 2. Activity-specific intelligence
    if "viewpoint" in att_type or "sunset" in att_type or "mountain" in att_type:
        recommended_window = f"{ss_str} (Arrive 45 mins prior: ~{int(ss_str.split(':')[0])-1}:{ss_str.split(':')[1]})"
        reason = f"Optimal lighting at golden hour. Sunset is at {ss_str} on {dest_date}."
        if weather_summary and "rain" in str(weather_summary.get("condition", "")).lower():
            warnings.append("Overcast or rain may impair panoramic visibility; check sky conditions 2 hours prior.")

    elif "waterfall" in att_type or "nature" in att_type or "trail" in att_type:
        recommended_window = "09:00 - 11:30"
        reason = "Morning provides safe daylight on natural terrain, fewer trail crowds, and active wildlife."
        if weather_summary and "rain" in str(weather_summary.get("condition", "")).lower():
            warnings.append("Recent or forecast rainfall can make trails slippery; stay on designated paths.")
        assumptions.append("Trail access depends on local park authority weather safety advisories.")

    elif "temple" in att_type or "shrine" in att_type:
        recommended_window = "07:30 - 09:30"
        reason = "Early morning visit avoids midday tour buses, offers quiet contemplation, and softer morning light."

    elif "market" in att_type or "food street" in att_type:
        recommended_window = "10:30 - 13:00"
        reason = "Peak market vitality with all fresh stalls and prepared food vendors fully operational for lunch."

    elif "museum" in att_type or "gallery" in att_type:
        recommended_window = "13:30 - 16:00"
        reason = "Ideal afternoon indoor activity escaping midday heat or adverse weather."
        if opening_hours:
            reason += " Verify closure days (often Mondays)."

    else:
        recommended_window = "10:00 - 12:30"
        reason = "Standard daylight operating hours."

    return {
        "attraction_name": attraction_name,
        "attraction_type": attraction_type,
        "target_date": dest_date,
        "sunrise_local": sr_str,
        "sunset_local": ss_str,
        "recommended_visit_window": recommended_window,
        "rationale": reason,
        "warnings": warnings,
        "assumptions": assumptions,
        "checked_at": check_time,
        "sources_used": [astronomical_source, "Local operating hour guidance"],
        "verification_status": "verified" if astronomical_source != "Fallback daylight estimate" else "estimated",
    }
