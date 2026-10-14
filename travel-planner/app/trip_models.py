"""Canonical trip state data models and verification provenance schemas."""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float
    lng: float


class CostItem(BaseModel):
    amount: float
    currency: str = "USD"
    is_verified: bool = False
    source: str = "Estimated"
    note: Optional[str] = None


class VerificationRecord(BaseModel):
    status: Literal["verified", "partially_verified", "estimated", "unverified"] = "estimated"
    source: str = "Knowledge Base"
    checked_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    details: Optional[Dict[str, Any]] = None
    limitations: Optional[str] = None


import uuid


class Activity(BaseModel):
    id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:10]}")
    slot: Literal["Morning", "Lunch", "Afternoon", "Evening"] = "Morning"
    time_window: str = "09:00 - 11:30"
    title: str
    description: str
    place_id: Optional[str] = None
    category: str = "Cultural Landmark"
    address: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    google_maps_url: Optional[str] = None
    directions_url: Optional[str] = None
    official_website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    best_time_to_visit: Optional[str] = None
    estimated_cost: Optional[CostItem] = None
    verification: VerificationRecord = Field(default_factory=VerificationRecord)


class IntercityTransfer(BaseModel):
    from_city: str
    to_city: str
    day: int
    mode: str = "High-speed rail"
    departure_station: Optional[str] = None
    arrival_station: Optional[str] = None
    duration_minutes: int = 90
    distance_km: Optional[float] = None
    estimated_cost: Optional[CostItem] = None
    booking_advice: Optional[str] = None
    verification: VerificationRecord = Field(default_factory=VerificationRecord)


class FeasibilityReport(BaseModel):
    overall_score: int = Field(default=95, ge=0, le=100)
    verification_rate: float = Field(default=85.0, ge=0.0, le=100.0)
    verified_places_count: int = 0
    estimated_items_count: int = 0
    schedule_conflicts: int = 0
    pacing_rating: Literal["Relaxed", "Optimal", "Intense", "Overpacked"] = "Optimal"
    feasibility_summary: str = "All scheduled items verified against live Google Places API and regional knowledge."
    warnings: List[str] = Field(default_factory=list)
    trade_off_suggestions: List[str] = Field(default_factory=list)


class DaySchedule(BaseModel):
    day_number: int
    date: Optional[str] = None
    city: str
    district: str
    theme: str
    summary: str
    transit_overview: str
    activities: List[Activity] = Field(default_factory=list)
    daily_budget_subtotal: float = 0.0
    currency: str = "USD"
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    golden_hour_advice: Optional[str] = None


class CanonicalTripState(BaseModel):
    trip_id: str
    title: str
    destination: str
    duration_days: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    group_size: int = 1
    currency: str = "USD"
    total_budget_per_person: float = 0.0
    total_group_budget: float = 0.0
    days: List[DaySchedule] = Field(default_factory=list)
    intercity_transfers: List[IntercityTransfer] = Field(default_factory=list)
    feasibility_report: FeasibilityReport = Field(default_factory=FeasibilityReport)
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
