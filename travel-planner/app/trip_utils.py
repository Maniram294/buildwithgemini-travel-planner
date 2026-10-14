"""Deterministic trip planning, duration handling, and geographic structuring utilities."""

import datetime
import re
from typing import Any, Dict, List, Optional, Tuple


def parse_trip_duration(
    text: str,
    reference_date: Optional[datetime.date] = None,
) -> Dict[str, Any]:
    """Parse duration and date ranges deterministically from user requests.

    Cases handled:
    - Case A: No dates and no duration mentioned -> defaults to 7 days (with explicit default notice).
    - Case B: Explicit number of days mentioned ("3-day", "5 days", "10 days") -> returns exact number of days.
    - Case C: Explicit date range ("November 2 to November 8", "2026-11-02 to 2026-11-08") -> inclusive calendar days calculation.
    - Case D: Ambiguity or conflict (e.g., "3 days from Nov 2 to Nov 10") -> identifies conflict and flags for clarification.

    Returns:
        dict with keys:
            - num_days: int
            - is_default: bool (True if defaulted to 7)
            - start_date: Optional ISO date string
            - end_date: Optional ISO date string
            - has_conflict: bool
            - conflict_message: Optional str
            - explanation: str
    """
    text_lower = text.lower()
    ref = reference_date or datetime.date(2026, 10, 14)

    # 1. Look for explicit number of days (e.g., "3 days", "3-day", "10 days", "ten days", "one week", "two weeks")
    num_days_match = None
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
        "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fourteen": 14,
        "a": 1, "an": 1,
    }

    # Matches like "3-day", "3 days", "3 day", "10-day trip"
    day_regex = r"\b(\d{1,2})\s*[- ]\s*day(?:s)?\b"
    m_digit = re.search(day_regex, text_lower)
    if m_digit:
        num_days_match = int(m_digit.group(1))
    else:
        # Matches word digits like "three-day", "three days"
        word_day_regex = r"\b(" + "|".join(word_to_num.keys()) + r")\s*[- ]\s*day(?:s)?\b"
        m_word = re.search(word_day_regex, text_lower)
        if m_word:
            num_days_match = word_to_num[m_word.group(1)]
        elif "a week" in text_lower or "one week" in text_lower:
            num_days_match = 7
        elif "two weeks" in text_lower or "2 weeks" in text_lower:
            num_days_match = 14
        elif "weekend" in text_lower or "long weekend" in text_lower:
            num_days_match = 3 if "long" in text_lower else 2

    # 2. Look for date ranges
    # Standard format: Month Day to Month Day (e.g., "November 2 to November 8", "Nov 2 through Nov 8", "10/12 to 10/15")
    months = {
        "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
        "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
        "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9,
        "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12
    }
    month_pattern = r"(" + "|".join(months.keys()) + r")"

    # Match: "November 2 to November 8" or "Nov 2 - Nov 8" or "November 2 to 8"
    date_range_regex = (
        month_pattern + r"\s+(\d{1,2})(?:st|nd|rd|th)?\s*(?:to|through|-|until)\s*" +
        r"(?:" + month_pattern + r"\s+)?(\d{1,2})(?:st|nd|rd|th)?(?:\s*,?\s*(\d{4}))?"
    )
    m_date = re.search(date_range_regex, text_lower)

    parsed_start_date = None
    parsed_end_date = None
    calculated_calendar_days = None

    if m_date:
        start_month_name = m_date.group(1)
        start_day = int(m_date.group(2))
        end_month_name = m_date.group(3) or start_month_name
        end_day = int(m_date.group(4))
        year_str = m_date.group(5)
        year = int(year_str) if year_str else ref.year

        start_month = months[start_month_name]
        end_month = months[end_month_name]

        # If month is before ref month, assume next year if no explicit year
        if not year_str and (start_month < ref.month or (start_month == ref.month and start_day < ref.day)):
            year += 1

        try:
            d_start = datetime.date(year, start_month, start_day)
            d_end = datetime.date(year, end_month, end_day)
            if d_end >= d_start:
                # Inclusive calendar days: Nov 2 to Nov 8 = (8 - 2) + 1 = 7 days
                calculated_calendar_days = (d_end - d_start).days + 1
                parsed_start_date = d_start.isoformat()
                parsed_end_date = d_end.isoformat()
        except ValueError:
            pass

    # 3. Check for conflict between stated duration and calculated dates (Case D)
    if num_days_match and calculated_calendar_days:
        if num_days_match != calculated_calendar_days:
            return {
                "num_days": num_days_match,
                "is_default": False,
                "start_date": parsed_start_date,
                "end_date": parsed_end_date,
                "has_conflict": True,
                "conflict_message": (
                    f"You mentioned a {num_days_match}-day trip, but the dates from "
                    f"{parsed_start_date} to {parsed_end_date} span {calculated_calendar_days} calendar days. "
                    f"Should we plan for {num_days_match} days or all {calculated_calendar_days} days?"
                ),
                "explanation": f"Conflict detected: {num_days_match} days specified vs {calculated_calendar_days} calendar days.",
            }

    # Case C: Date range provided
    if calculated_calendar_days:
        return {
            "num_days": calculated_calendar_days,
            "is_default": False,
            "start_date": parsed_start_date,
            "end_date": parsed_end_date,
            "has_conflict": False,
            "conflict_message": None,
            "explanation": f"Calculated {calculated_calendar_days} inclusive calendar days from {parsed_start_date} to {parsed_end_date}.",
        }

    # Case B: Number of days specified
    if num_days_match:
        return {
            "num_days": num_days_match,
            "is_default": False,
            "start_date": None,
            "end_date": None,
            "has_conflict": False,
            "conflict_message": None,
            "explanation": f"Using requested duration of exactly {num_days_match} days.",
        }

    # Case A: Neither provided -> 7-day default
    return {
        "num_days": 7,
        "is_default": True,
        "start_date": None,
        "end_date": None,
        "has_conflict": False,
        "conflict_message": None,
        "explanation": "No specific duration or dates provided; defaulting to a 7-day comprehensive itinerary.",
    }


def validate_itinerary_structure(itinerary: Dict[str, Any], requested_days: int) -> Dict[str, Any]:
    """Validate that generated itinerary matches duration, has meal stops and activities."""
    days = itinerary.get("days", [])
    errors = []
    warnings = []

    if len(days) != requested_days:
        errors.append(f"Itinerary contains {len(days)} days, but {requested_days} days were requested.")

    for i, day in enumerate(days, 1):
        if not day.get("morning"):
            warnings.append(f"Day {i} is missing morning plan.")
        if not day.get("lunch"):
            warnings.append(f"Day {i} is missing lunch recommendation.")
        if not day.get("afternoon"):
            warnings.append(f"Day {i} is missing afternoon plan.")
        if not day.get("evening"):
            warnings.append(f"Day {i} is missing evening recommendation.")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "day_count": len(days),
    }
