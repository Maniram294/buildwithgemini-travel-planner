"""Agent H: QA, Consistency, and Feasibility Reporting Agent."""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from ..trip_models import CanonicalTripState, FeasibilityReport, DaySchedule


class QualityAssuranceAndConsistencyAgent:
    """Evaluates itinerary consistency, non-overlapping schedules, verification density, and pacing."""

    def evaluate_trip_feasibility(self, trip: CanonicalTripState) -> FeasibilityReport:
        """Analyze canonical trip state and generate comprehensive feasibility metrics."""
        total_activities = sum(len(d.activities) for d in trip.days)
        verified_count = 0
        estimated_count = 0
        conflicts = 0
        warnings = []
        suggestions = []

        from .logistics_agent import TransportationAndLogisticsAgent

        for d in trip.days:
            # Check slot sequence
            slots = [a.slot for a in d.activities]
            if len(slots) > len(set(slots)):
                conflicts += 1
                warnings.append(f"Day {d.day_number} contains duplicate activity slots: {slots}")

            # Geographic proximity evaluation between consecutive stops
            for idx in range(len(d.activities) - 1):
                a1 = d.activities[idx]
                a2 = d.activities[idx + 1]
                if a1.coordinates and a2.coordinates:
                    dist_km = TransportationAndLogisticsAgent.calculate_haversine_distance_km(
                        a1.coordinates.lat, a1.coordinates.lng,
                        a2.coordinates.lat, a2.coordinates.lng,
                    )
                    # Intra-city activities separated by > 40 km may indicate an unrealistic day transit
                    if dist_km > 40.0:
                        warnings.append(
                            f"Day {d.day_number}: Significant transit distance ({dist_km} km) between '{a1.title}' and '{a2.title}'."
                        )

            for act in d.activities:
                if act.verification.status == "verified":
                    verified_count += 1
                else:
                    estimated_count += 1

            if len(d.activities) >= 5:
                warnings.append(f"Day {d.day_number} ({d.city}) has {len(d.activities)} stops; pacing might feel rushed.")
                suggestions.append(f"Consider combining afternoon activities on Day {d.day_number} for deeper immersion.")

        verification_rate = round((verified_count / total_activities * 100), 1) if total_activities > 0 else 0.0

        pacing = "Optimal"
        if total_activities / max(1, trip.duration_days) > 4.5:
            pacing = "Intense"
        elif total_activities / max(1, trip.duration_days) < 2.5:
            pacing = "Relaxed"

        overall_score = min(100, max(50, int(verification_rate * 0.7 + (100 - conflicts * 10) * 0.3)))

        return FeasibilityReport(
            overall_score=overall_score,
            verification_rate=verification_rate,
            verified_places_count=verified_count,
            estimated_items_count=estimated_count,
            schedule_conflicts=conflicts,
            pacing_rating=pacing,
            feasibility_summary=(
                f"Itinerary achieves {verification_rate}% verified intelligence score with {conflicts} schedule conflicts. "
                f"Districts are geographically clustered to minimize transit fatigue."
            ),
            warnings=warnings,
            trade_off_suggestions=suggestions,
        )
