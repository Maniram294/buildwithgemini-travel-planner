"""Deterministic source-backed budget calculation and currency breakdown engine."""

import datetime
from typing import Any, Dict, List, Optional


def calculate_trip_budget(
    expenses: List[Dict[str, Any]],
    group_size: int = 1,
    num_days: int = 1,
    target_currency: str = "USD",
    exchange_rates: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Calculate daily, per-person, and total trip budgets with clear source/estimate provenance.

    Args:
        expenses: List of cost items. Each item:
            - category: str ('accommodation', 'food', 'local_transport', 'intercity_transport', 'activities', 'contingency')
            - amount: float
            - currency: str (e.g. 'USD', 'JPY', 'EUR')
            - unit: str ('per_person', 'per_group', 'per_night', 'per_day', 'one_time')
            - is_verified: bool
            - source: str
            - description: str
            - day: Optional[int]
        group_size: Number of travelers (shared accommodation/rides split appropriately)
        num_days: Trip duration in days
        target_currency: Currency for totals (default: 'USD')
        exchange_rates: Map of {currency: rate_to_target}

    Returns:
        Structured budget report with category subtotals, per-person total, group total, and verification notes.
    """
    rates = exchange_rates or {target_currency: 1.0}
    rates[target_currency] = 1.0

    group = max(1, group_size)
    days = max(1, num_days)

    category_totals: Dict[str, float] = {
        "accommodation": 0.0,
        "food": 0.0,
        "local_transport": 0.0,
        "intercity_transport": 0.0,
        "activities": 0.0,
        "contingency": 0.0,
    }

    daily_totals: Dict[int, float] = {d: 0.0 for d in range(1, days + 1)}
    verified_amount = 0.0
    estimated_amount = 0.0
    processed_items = []
    unconverted_items = []

    for item in expenses:
        cat = item.get("category", "activities")
        if cat not in category_totals:
            category_totals[cat] = 0.0

        raw_amt = float(item.get("amount", 0.0))
        curr = item.get("currency", target_currency).upper().strip()
        unit = item.get("unit", "per_person")
        is_verified = bool(item.get("is_verified", False))
        source = item.get("source", "Estimated")
        desc = item.get("description", "")
        item_day = item.get("day")

        # Convert to target currency
        rate = rates.get(curr)
        if rate is None:
            unconverted_items.append(f"{raw_amt} {curr} ({desc})")
            continue

        amt_in_target = raw_amt * rate

        # Calculate total cost for the whole group across the trip
        if unit == "per_person":
            item_group_total = amt_in_target * group
        elif unit == "per_group":
            item_group_total = amt_in_target
        elif unit == "per_night":
            nights = max(1, days - 1) if days > 1 else 1
            item_group_total = amt_in_target * nights
        elif unit == "per_day":
            item_group_total = amt_in_target * days * (group if "person" in desc.lower() else 1)
        elif unit == "one_time":
            item_group_total = amt_in_target
        else:
            item_group_total = amt_in_target

        category_totals[cat] += round(item_group_total, 2)

        if item_day and 1 <= item_day <= days:
            daily_totals[item_day] += round(item_group_total, 2)

        if is_verified:
            verified_amount += item_group_total
        else:
            estimated_amount += item_group_total

        processed_items.append({
            "category": cat,
            "description": desc,
            "original_amount": raw_amt,
            "original_currency": curr,
            "converted_amount": round(item_group_total, 2),
            "target_currency": target_currency,
            "unit": unit,
            "verification_status": "verified" if is_verified else "estimated",
            "source": source,
        })

    total_group_cost = sum(category_totals.values())
    per_person_cost = total_group_cost / group

    return {
        "target_currency": target_currency,
        "group_size": group,
        "duration_days": days,
        "total_group_cost": round(total_group_cost, 2),
        "total_per_person_cost": round(per_person_cost, 2),
        "category_breakdown": {k: round(v, 2) for k, v in category_totals.items() if v > 0},
        "daily_totals": {f"Day {k}": round(v, 2) for k, v in daily_totals.items() if v > 0},
        "verification_summary": {
            "verified_costs_total": round(verified_amount, 2),
            "estimated_costs_total": round(estimated_amount, 2),
            "verified_percentage": round((verified_amount / total_group_cost * 100), 1) if total_group_cost > 0 else 0.0,
        },
        "unconverted_items": unconverted_items,
        "items": processed_items,
    }
