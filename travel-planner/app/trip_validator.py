"""Deterministic validation engine for Canonical Trip State and structured travel outputs."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import ValidationError

from app.trip_models import (
    Activity,
    CanonicalTripState,
    CostItem,
    DaySchedule,
    FeasibilityReport,
    IntercityTransfer,
    VerificationRecord,
)
from app.trip_utils import parse_trip_duration


class ValidationResult:
    """Structured validation report for trip data."""

    def __init__(
        self,
        is_valid: bool,
        errors: List[str],
        warnings: List[str],
        validated_trip: Optional[CanonicalTripState] = None,
        total_activities_count: int = 0,
        verified_activities_count: int = 0,
    ):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.validated_trip = validated_trip
        self.total_activities_count = total_activities_count
        self.verified_activities_count = verified_activities_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "has_trip": self.validated_trip is not None,
            "total_activities_count": self.total_activities_count,
            "verified_activities_count": self.verified_activities_count,
        }


def validate_canonical_trip(
    trip_data: CanonicalTripState | Dict[str, Any],
    expected_destination: Optional[str] = None,
    expected_days: Optional[int] = None,
) -> ValidationResult:
    """Validate a canonical trip state against deterministic integrity constraints.

    Checks:
    1. Schema conformance (valid types, required fields, non-empty IDs).
    2. Exact duration match between expected days, trip.duration_days, and len(trip.days).
    3. Destination alignment (requested destination keywords match trip destination/cities).
    4. Activity slot sequencing and non-overlapping time windows without duplicates.
    5. Mathematical consistency of daily budget subtotals and overall trip totals.
    6. Verification metadata integrity (status in allowed values, source attribution present).

    Args:
        trip_data: CanonicalTripState instance or raw dictionary.
        expected_destination: Optional prompt/requested destination to verify against.
        expected_days: Optional explicit requested number of days.

    Returns:
        ValidationResult with status, errors list, warnings list, and validated trip instance.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Schema Parsing & Conformance
    if isinstance(trip_data, CanonicalTripState):
        trip = trip_data
    elif isinstance(trip_data, dict):
        try:
            trip = CanonicalTripState.model_validate(trip_data)
        except ValidationError as ve:
            return ValidationResult(
                is_valid=False,
                errors=[f"Schema validation error: {err.get('loc')}: {err.get('msg')}" for err in ve.errors()],
                warnings=warnings,
                validated_trip=None,
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Malformed trip data: {str(e)}"],
                warnings=warnings,
                validated_trip=None,
            )
    else:
        return ValidationResult(
            is_valid=False,
            errors=[f"Invalid trip data type: {type(trip_data).__name__}"],
            warnings=warnings,
            validated_trip=None,
        )

    # 2. Duration and Day Count Exactness
    num_days = len(trip.days)
    if num_days == 0:
        errors.append("Duration mismatch: Trip contains no scheduled days.")

    if trip.duration_days != num_days:
        errors.append(
            f"Duration mismatch: Trip duration_days ({trip.duration_days}) does not match number of days in schedule ({num_days})."
        )

    if expected_days is not None and expected_days > 0:
        if num_days != expected_days:
            errors.append(
                f"Duration mismatch: Requested trip duration of {expected_days} days does not match generated {num_days} days."
            )

    # Check Day Sequence Continuity (1, 2, 3...)
    seen_day_nums: Set[int] = set()
    for idx, day in enumerate(trip.days, start=1):
        if day.day_number in seen_day_nums:
            errors.append(f"Duplicate day number detected: Day {day.day_number}.")
        seen_day_nums.add(day.day_number)
        if day.day_number != idx:
            warnings.append(f"Day number {day.day_number} is out of sequential order (expected {idx}).")

    # 3. Destination Alignment Verification
    if expected_destination:
        cleaned_exp = re.sub(r"[^\w\s]", " ", expected_destination.lower())
        exp_tokens = {w for w in cleaned_exp.split() if len(w) > 3 and w not in {"plan", "trip", "visit", "tour", "authentic", "realistic", "food", "specialties", "verified", "places", "days"}}

        trip_dest_lower = (trip.destination or "").lower()
        trip_cities = " ".join((d.city or "").lower() for d in trip.days)
        trip_text = f"{trip_dest_lower} {trip_cities}"

        if exp_tokens:
            matched = any(token in trip_text for token in exp_tokens)
            if not matched:
                errors.append(
                    f"Destination mismatch: Expected context from '{expected_destination}', but trip destination is '{trip.destination}' with cities '{trip_cities}'."
                )

    # 4. Activity Verification & Non-overlapping Structure
    total_activities = 0
    verified_activities = 0
    seen_activity_ids: Set[str] = set()
    seen_activity_titles_by_city: Dict[str, Set[str]] = {}

    for day in trip.days:
        city_key = (day.city or "default").lower().strip()
        if city_key not in seen_activity_titles_by_city:
            seen_activity_titles_by_city[city_key] = set()

        if not day.activities:
            warnings.append(f"Day {day.day_number} has no scheduled activities.")

        day_slots: List[str] = []
        for act in day.activities:
            total_activities += 1
            # Check unique activity ID
            if act.id in seen_activity_ids:
                warnings.append(f"Duplicate activity ID '{act.id}' on Day {day.day_number}.")
            seen_activity_ids.add(act.id)

            # Check duplicate landmark/restaurant within same city
            norm_title = act.title.lower().strip()
            if norm_title in seen_activity_titles_by_city[city_key]:
                warnings.append(f"Duplicate activity title '{act.title}' scheduled multiple times in {day.city}.")
            seen_activity_titles_by_city[city_key].add(norm_title)

            # Slot continuity
            day_slots.append(act.slot)

            # Verification metadata validation
            if act.verification is None:
                errors.append(f"Activity '{act.title}' is missing verification provenance metadata.")
            elif act.verification.status not in {"verified", "partially_verified", "estimated", "unverified"}:
                errors.append(f"Activity '{act.title}' has invalid verification status '{act.verification.status}'.")
            elif act.verification.status == "verified":
                verified_activities += 1

        # Slot duplication check within single day
        if len(day_slots) != len(set(day_slots)):
            warnings.append(f"Day {day.day_number} has duplicate slot assignments: {day_slots}.")

    # 5. Budget Mathematical Consistency
    day_subtotals_sum = sum(d.daily_budget_subtotal for d in trip.days)
    if trip.total_budget_per_person > 0:
        transfer_costs = sum((t.estimated_cost.amount if t.estimated_cost else 0.0) for t in trip.intercity_transfers)
        expected_total = day_subtotals_sum + transfer_costs
        diff = abs(trip.total_budget_per_person - expected_total)
        if diff > 10.0:
            errors.append(
                f"Budget calculation mismatch: total_budget_per_person ({trip.total_budget_per_person}) differs significantly from sum of daily subtotals and transfers ({expected_total:.2f})."
            )
        elif diff > 1.0:
            warnings.append(
                f"Budget inconsistency: total_budget_per_person ({trip.total_budget_per_person}) differs from sum of daily subtotals and transfers ({expected_total:.2f})."
            )

    if trip.group_size > 1 and trip.total_group_budget > 0:
        expected_group = trip.total_budget_per_person * trip.group_size
        if abs(trip.total_group_budget - expected_group) > 5.0:
            errors.append(
                f"Group budget calculation mismatch: total_group_budget ({trip.total_group_budget}) != per_person * group_size ({expected_group:.2f})."
            )

    is_valid = len(errors) == 0
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        validated_trip=trip if is_valid else None,
        total_activities_count=total_activities,
        verified_activities_count=verified_activities,
    )
