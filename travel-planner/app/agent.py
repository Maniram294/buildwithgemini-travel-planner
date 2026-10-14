# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
import json
import os
from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .a2ui_utils import a2ui_callback
from .culinary_data import get_culinary_context
from .trip_utils import parse_trip_duration, validate_itinerary_structure
from .link_utils import build_google_maps_search_url, build_google_maps_directions_url, validate_web_url, format_evidence_record
from .timing_utils import evaluate_best_visit_time
from .budget_utils import calculate_trip_budget
from .events_data import find_seasonal_events
from .food_passport import food_passport
from .offline_pack import generate_offline_trip_pack
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore
from google.cloud import storage
from google import genai
from google.genai import types

MODEL = "gemini-3.8-flash"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"
FIRESTORE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-03-fe98c55ba1b5")
BUCKET_NAME = os.getenv("TRAVEL_PLANNER_BUCKET", "travel-planner-media-7dx9bu")
AGENT_ENGINE_ID = "460472171177705472"
MEMORY_BANK_ID = "460472171177705472"
SANDBOX_RESOURCE_NAME = "projects/513515792631/locations/us-east1/reasoningEngines/460472171177705472/sandboxEnvironments/2933928031464456192"


def get_firestore_client() -> firestore.Client:
    """Return a Firestore client pinned to the project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def list_destinations(travel_style: Optional[str] = None) -> List[Dict[str, Any]]:
    """List curated travel destinations from the Firestore catalog.

    Args:
        travel_style: Optional filter by style (e.g., 'cultural', 'adventure', 'foodie').

    Returns:
        A list of destination dictionaries matching the query.
    """
    db = get_firestore_client()
    collection_ref = db.collection("destinations")

    if travel_style:
        query = collection_ref.where("travel_style", "==", travel_style.lower().strip())
        docs = query.stream()
    else:
        docs = collection_ref.stream()

    destinations = [doc.to_dict() for doc in docs]
    return destinations


def get_destination_details(destination_id: str) -> Dict[str, Any]:
    """Retrieve detailed information for a specific destination by its ID.

    Args:
        destination_id: The unique identifier of the destination (e.g., 'kyoto-japan', 'tokyo-japan', 'paris-france').

    Returns:
        A dictionary containing the destination details or an error message if not found.
    """
    db = get_firestore_client()
    doc = db.collection("destinations").document(destination_id.lower().strip()).get()

    if not doc.exists:
        return {"error": f"Destination with ID '{destination_id}' was not found in the catalog."}

    return doc.to_dict()


def save_destination(
    destination_id: str,
    name: str,
    country: str,
    travel_style: str,
    budget_tier: str,
    highlights: List[str],
    best_season: str,
    estimated_daily_cost_usd: int,
    description: str,
) -> Dict[str, Any]:
    """Save or update a travel destination in the Firestore catalog.

    Args:
        destination_id: A URL-friendly identifier (e.g., 'tokyo-japan', 'paris-france').
        name: Name of the city/region (e.g., 'Tokyo').
        country: Country name (e.g., 'Japan').
        travel_style: Category such as 'adventure', 'cultural', 'foodie', or 'relaxation'.
        budget_tier: 'budget', 'moderate', or 'luxury'.
        highlights: A list of key attractions or activities.
        best_season: Ideal months or season to visit.
        estimated_daily_cost_usd: Approximate daily cost in USD per traveler.
        description: A short overview of the destination.

    Returns:
        Status dictionary confirming the save action.
    """
    db = get_firestore_client()
    data = {
        "id": destination_id.lower().strip(),
        "name": name,
        "country": country,
        "travel_style": travel_style.lower().strip(),
        "budget_tier": budget_tier.lower().strip(),
        "highlights": highlights,
        "best_season": best_season,
        "estimated_daily_cost_usd": estimated_daily_cost_usd,
        "description": description,
    }
    db.collection("destinations").document(destination_id.lower().strip()).set(data)
    return {"status": "success", "message": f"Destination '{name}' saved successfully with ID '{destination_id}'."}


def plan_trip_duration(user_request: str) -> Dict[str, Any]:
    """Analyze the user's travel request to determine the exact itinerary duration and dates.

    Rules applied:
    - Case A: If no dates and no duration are specified, defaults strictly to 7 days with explicit disclosure.
    - Case B: If specific days are mentioned (e.g. '3-day', '5 days', '10 days'), returns exactly that number of days.
    - Case C: If travel dates are provided (e.g. 'November 2 to November 8'), calculates inclusive calendar days.
    - Case D: If dates and duration conflict, flags the conflict so clarification can be asked.

    Args:
        user_request: The user's input prompt (e.g., 'Plan a trip to Kyoto' or '5 days in Tokyo').

    Returns:
        A dictionary with num_days, is_default, start_date, end_date, has_conflict, conflict_message, and explanation.
    """
    return parse_trip_duration(user_request)


def discover_authentic_cuisine(
    destination: str,
    specialty_or_dish: Optional[str] = None,
    neighborhood: Optional[str] = None,
    origin_location: Optional[str] = None,
    max_results: int = 5,
) -> Dict[str, Any]:
    """Discover authentic regional cuisine, signature dishes, local food neighborhoods, and verified eateries.

    Combines verified regional culinary heritage context with real-time Google Places API (New) data
    including verified business existence, addresses, actual ratings, review counts, price tiers, operating hours,
    direct Google Maps links, and turn-by-turn directions links from consecutive stops.

    Args:
        destination: City or region name (e.g., 'Kyoto', 'Tokyo', 'Istanbul', 'Paris').
        specialty_or_dish: Specific regional dish or food experience (e.g., 'Yudofu', 'Edomae Sushi', 'Monjayaki').
        neighborhood: Specific authentic neighborhood or food street (e.g., 'Gion', 'Tsukiji', 'Karaköy').
        origin_location: Optional previous stop name for generating a Google Maps directions link.
        max_results: Maximum number of verified places to return (1-10, default: 5).

    Returns:
        A dictionary containing regional culinary background, signature dishes to try, and verified real venues.
    """
    culinary_info = get_culinary_context(destination)
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    query_parts = []
    if specialty_or_dish:
        query_parts.append(specialty_or_dish)
    else:
        query_parts.append("authentic local cuisine regional dishes")
    if neighborhood:
        query_parts.append(neighborhood)
    query_parts.append(destination)
    text_query = " ".join(query_parts).strip()

    verified_places = []
    if api_key:
        try:
            url = "https://places.googleapis.com/v1/places:searchText"
            payload = {
                "textQuery": text_query,
                "maxResultCount": min(max(1, max_results), 10),
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": (
                        "places.displayName,places.formattedAddress,places.location,"
                        "places.rating,places.userRatingCount,places.priceLevel,"
                        "places.primaryTypeDisplayName,places.regularOpeningHours.weekdayDescriptions,"
                        "places.googleMapsUri,places.websiteUri"
                    ),
                },
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode())

            for p in data.get("places", []):
                loc = p.get("location", {})
                hours = p.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
                p_name = p.get("displayName", {}).get("text", "Eatery")
                p_addr = p.get("formattedAddress")
                maps_uri = p.get("googleMapsUri") or build_google_maps_search_url(p_name, p_addr)
                website_uri = validate_web_url(p.get("websiteUri"))
                directions_uri = build_google_maps_directions_url(
                    destination_name=p_name,
                    origin_name=origin_location,
                    destination_address=p_addr,
                )

                verified_places.append({
                    "name": p_name,
                    "address": p_addr,
                    "category": p.get("primaryTypeDisplayName", {}).get("text", "Restaurant"),
                    "rating": p.get("rating"),
                    "review_count": p.get("userRatingCount"),
                    "price_level": p.get("priceLevel"),
                    "opening_hours": hours[:3] if hours else None,
                    "google_maps_url": maps_uri,
                    "directions_url": directions_uri,
                    "official_website_url": website_uri,
                    "verification_source": "Verified Google Places API business",
                    "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                })
        except Exception as e:
            return {
                "destination": destination,
                "regional_culinary_context": culinary_info,
                "verified_places": [],
                "api_error": f"Live places lookup failed: {str(e)}",
            }

    return {
        "destination": destination,
        "search_query_used": text_query,
        "regional_culinary_context": culinary_info,
        "verified_places": verified_places,
        "verification_note": "Places verified against live Google Places API. Regional context grounded in cultural food records.",
    }


def search_destination_experiences(
    destination: str,
    experience_category: str = "cultural landmarks",
    neighborhood: Optional[str] = None,
    origin_location: Optional[str] = None,
    max_results: int = 5,
) -> Dict[str, Any]:
    """Search for real attractions, historic landmarks, traditional markets, and cultural experiences.

    Queries the Google Places API (New) for verified locations, operating hours, visitor ratings,
    direct Google Maps URLs, directions links, and official websites when available.

    Args:
        destination: City or region (e.g. 'Kyoto', 'Istanbul', 'Tokyo').
        experience_category: Category such as 'historical landmarks', 'traditional markets', 'art museums', 'parks and gardens', 'neighborhoods'.
        neighborhood: Optional district (e.g. 'Arashiyama', 'Sultanahmet', 'Yanaka').
        origin_location: Optional previous stop for transit directions.
        max_results: Maximum results to return (1-10, default: 5).

    Returns:
        A dictionary with real places, address, rating, operating hours, Google Maps URI, and directions.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}

    query_parts = [experience_category]
    if neighborhood:
        query_parts.append(neighborhood)
    query_parts.append(destination)
    text_query = " ".join(query_parts).strip()

    try:
        url = "https://places.googleapis.com/v1/places:searchText"
        payload = {
            "textQuery": text_query,
            "maxResultCount": min(max(1, max_results), 10),
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": (
                    "places.displayName,places.formattedAddress,places.location,"
                    "places.rating,places.userRatingCount,places.primaryTypeDisplayName,"
                    "places.regularOpeningHours.weekdayDescriptions,places.googleMapsUri,places.websiteUri"
                ),
            },
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())

        places = []
        for p in data.get("places", []):
            loc = p.get("location", {})
            hours = p.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
            p_name = p.get("displayName", {}).get("text", "Attraction")
            p_addr = p.get("formattedAddress")
            maps_uri = p.get("googleMapsUri") or build_google_maps_search_url(p_name, p_addr)
            website_uri = validate_web_url(p.get("websiteUri"))
            directions_uri = build_google_maps_directions_url(
                destination_name=p_name,
                origin_name=origin_location,
                destination_address=p_addr,
            )

            places.append({
                "name": p_name,
                "address": p_addr,
                "category": p.get("primaryTypeDisplayName", {}).get("text", "Attraction"),
                "rating": p.get("rating"),
                "review_count": p.get("userRatingCount"),
                "opening_hours": hours[:3] if hours else None,
                "google_maps_url": maps_uri,
                "directions_url": directions_uri,
                "official_website_url": website_uri,
                "location": {"latitude": loc.get("latitude"), "longitude": loc.get("longitude")},
                "verification_source": "Verified Google Places API location",
                "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })

        return {
            "destination": destination,
            "category": experience_category,
            "places": places,
            "count": len(places),
        }
    except Exception as e:
        return {"error": f"Failed to search experiences: {str(e)}"}


def get_best_visit_time(
    attraction_name: str,
    attraction_type: str,
    latitude: float,
    longitude: float,
    target_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Recommend an evidence-backed optimal visiting window based on astronomical sunrise/sunset and opening hours.

    Args:
        attraction_name: Name of the landmark or site.
        attraction_type: Type (e.g., 'viewpoint', 'temple', 'museum', 'market', 'waterfall').
        latitude: Latitude of the attraction.
        longitude: Longitude of the attraction.
        target_date: Travel date in ISO format (YYYY-MM-DD).

    Returns:
        Dictionary with recommended window, sunrise/sunset times, rationale, and environmental warnings.
    """
    return evaluate_best_visit_time(
        attraction_name=attraction_name,
        attraction_type=attraction_type,
        latitude=latitude,
        longitude=longitude,
        target_date=target_date,
    )


def calculate_budget_plan(
    expenses_json: str,
    group_size: int = 1,
    num_days: int = 1,
    target_currency: str = "USD",
) -> Dict[str, Any]:
    """Calculate daily, per-person, and total trip budget breakdown with clear distinction between verified and estimated costs.

    Args:
        expenses_json: JSON string representing a list of cost items (category, amount, currency, unit, is_verified, source, description).
        group_size: Number of travelers.
        num_days: Trip duration in days.
        target_currency: Currency for totals (default: 'USD').

    Returns:
        Structured budget summary with per-person and group totals.
    """
    try:
        items = json.loads(expenses_json)
        return calculate_trip_budget(
            expenses=items,
            group_size=group_size,
            num_days=num_days,
            target_currency=target_currency,
        )
    except Exception as e:
        return {"error": f"Budget calculation failed: {str(e)}"}


def get_seasonal_events(
    destination: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Discover seasonal and cultural festivals occurring in the destination during the travel window.

    Args:
        destination: City or destination name.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).

    Returns:
        Dictionary of verified cultural events with venues, descriptions, and official links.
    """
    return find_seasonal_events(destination=destination, start_date=start_date, end_date=end_date)


def manage_food_passport(
    action: str,
    user_id: str,
    dish_name: Optional[str] = None,
    destination: Optional[str] = None,
    status: Optional[str] = "want_to_try",
    rating: Optional[int] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Manage the traveler's personal food passport to track dishes to try, dishes tried, ratings, and notes.

    Args:
        action: 'add', 'list', or 'remove'.
        user_id: Unique user identifier.
        dish_name: Name of the regional dish.
        destination: Destination city or region.
        status: 'want_to_try' or 'tried'.
        rating: Optional 1-5 rating if tried.
        notes: Optional personal notes.

    Returns:
        Status and food passport records.
    """
    act = action.lower().strip()
    if act in ["add", "update"]:
        if not dish_name or not destination:
            return {"error": "dish_name and destination are required to add/update food passport."}
        return food_passport.add_or_update_dish(
            user_id=user_id,
            dish_name=dish_name,
            destination=destination,
            status=status or "want_to_try",
            rating=rating,
            notes=notes,
        )
    elif act == "list":
        dishes = food_passport.list_passport_dishes(user_id=user_id, destination=destination, status=status)
        return {"user_id": user_id, "passport_entries": dishes, "count": len(dishes)}
    elif act == "remove":
        if not dish_name or not destination:
            return {"error": "dish_name and destination are required to remove from food passport."}
        return food_passport.remove_dish(user_id=user_id, dish_name=dish_name, destination=destination)
    else:
        return {"error": f"Unknown action '{action}'. Use 'add', 'list', or 'remove'."}


def compile_offline_pack(
    trip_name: str,
    destination: str,
    duration_days: int,
    itinerary_json: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Compile and serialize a self-contained offline travel pack with local addresses, timing, and saved links.

    Args:
        trip_name: Title of the trip.
        destination: Destination name.
        duration_days: Duration in days.
        itinerary_json: JSON string of daily itinerary stops.
        start_date: Optional start date.
        end_date: Optional end date.

    Returns:
        Structured offline travel document ready for local offline storage.
    """
    try:
        days = json.loads(itinerary_json)
        return generate_offline_trip_pack(
            trip_name=trip_name,
            destination=destination,
            duration_days=duration_days,
            itinerary_days=days,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        return {"error": f"Failed to compile offline pack: {str(e)}"}


def fetch_live_weather(location: str) -> Dict[str, Any]:
    """Fetch live real-time weather and forecast conditions for any city or destination.

    Args:
        location: City or destination name (e.g., 'Kyoto', 'Reykjavik', 'Paris').

    Returns:
        A dictionary with temperature in Fahrenheit, weather condition description, wind speed, and location coordinates.
    """
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(location)}&count=1&language=en&format=json"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            geo_data = json.loads(res.read().decode())

        if not geo_data.get("results"):
            return {"error": f"Could not find geographic coordinates for location '{location}'."}

        top_match = geo_data["results"][0]
        lat = top_match["latitude"]
        lon = top_match["longitude"]
        city_name = top_match.get("name", location)
        country = top_match.get("country", "")

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
            f"&temperature_unit=fahrenheit&wind_speed_unit=mph"
        )
        req_w = urllib.request.Request(weather_url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req_w, timeout=5) as res:
            weather_data = json.loads(res.read().decode())

        current = weather_data.get("current", {})
        code = current.get("weather_code", 0)

        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
            55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm",
        }
        condition = weather_codes.get(code, "Clear/partly cloudy")

        return {
            "location": f"{city_name}, {country}".strip(", "),
            "latitude": lat,
            "longitude": lon,
            "temperature_f": current.get("temperature_2m"),
            "feels_like_f": current.get("apparent_temperature"),
            "condition": condition,
            "humidity_percent": current.get("relative_humidity_2m"),
            "wind_speed_mph": current.get("wind_speed_10m"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch live weather for '{location}': {str(e)}"}


def convert_currency(amount: float, from_currency: str = "USD", to_currency: str = "EUR") -> Dict[str, Any]:
    """Convert travel budgets and costs between international currencies using live exchange rates.

    Args:
        amount: The monetary amount to convert.
        from_currency: 3-letter currency code to convert from (e.g., 'USD', 'EUR', 'GBP', 'JPY', 'MXN').
        to_currency: 3-letter currency code to convert to (e.g., 'JPY', 'EUR', 'MXN', 'NZD', 'USD').

    Returns:
        A dictionary with the original amount, converted amount, conversion rate, and timestamp.
    """
    base = from_currency.upper().strip()
    target = to_currency.upper().strip()
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        req = urllib.request.Request(url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())

        if data.get("result") != "success":
            return {"error": f"Unable to fetch exchange rates for base currency '{base}'."}

        rates = data.get("rates", {})
        if target not in rates:
            return {"error": f"Target currency '{target}' not supported or not found."}

        rate = rates[target]
        converted_amount = round(amount * rate, 2)

        return {
            "original_amount": amount,
            "from_currency": base,
            "converted_amount": converted_amount,
            "to_currency": target,
            "exchange_rate": rate,
            "last_updated": data.get("time_last_update_utc"),
        }
    except Exception as e:
        return {"error": f"Currency conversion failed: {str(e)}"}


def geocode_address(address: str) -> Dict[str, Any]:
    """Convert an address, landmark, or location string into geographic latitude and longitude coordinates.

    Args:
        address: The address, place name, or landmark to geocode (e.g. 'Eiffel Tower, Paris' or 'Kiyomizu-dera, Kyoto').

    Returns:
        A dictionary with the formatted address, location coordinates (latitude, longitude), and place ID.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}

    try:
        encoded_address = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
        req = urllib.request.Request(url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())

        if data.get("status") != "OK" or not data.get("results"):
            return {"error": f"Geocoding failed for '{address}'. Status: {data.get('status')}"}

        result = data["results"][0]
        loc = result["geometry"]["location"]
        return {
            "formatted_address": result.get("formatted_address"),
            "location": {"latitude": loc["lat"], "longitude": loc["lng"]},
            "place_id": result.get("place_id"),
        }
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 1500.0,
    max_results: int = 5,
) -> Dict[str, Any]:
    """Find nearby places around coordinates using the Google Places API (New).

    Args:
        latitude: Latitude of the center point.
        longitude: Longitude of the center point.
        place_type: Type of place to search for (e.g., 'tourist_attraction', 'restaurant', 'museum', 'hotel', 'cafe').
        radius_meters: Search radius in meters (default: 1500 meters).
        max_results: Maximum number of places to return (1-20, default: 5).

    Returns:
        A list of nearby places with name, formatted address, and location coordinates.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set."}

    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        payload = {
            "includedTypes": [place_type.lower().strip()],
            "maxResultCount": min(max(1, max_results), 20),
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": float(radius_meters),
                }
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.googleMapsUri",
            },
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())

        places = []
        for p in data.get("places", []):
            loc = p.get("location", {})
            places.append({
                "name": p.get("displayName", {}).get("text"),
                "address": p.get("formattedAddress"),
                "rating": p.get("rating"),
                "review_count": p.get("userRatingCount"),
                "google_maps_url": p.get("googleMapsUri"),
                "location": {"latitude": loc.get("latitude"), "longitude": loc.get("longitude")},
            })

        return {"places": places, "count": len(places)}
    except Exception as e:
        return {"error": f"Nearby places search failed: {str(e)}"}


def generate_destination_image(
    prompt: str,
    tool_context: ToolContext,
    destination_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a scenic travel photograph or postcard for a destination, save it as an artifact, and upload it to Cloud Storage.

    Args:
        prompt: Description of the scene, destination, or landmark to generate (e.g. 'A tranquil sunset view of Kyoto bamboo forest').
        tool_context: Tool execution context injected by the ADK runtime.
        destination_name: Optional name of the destination for clean file naming.

    Returns:
        A dictionary containing the public Cloud Storage URL of the image, the artifact filename, and status.
    """
    try:
        client = genai.Client(
            vertexai=True,
            project=FIRESTORE_PROJECT_ID,
            location="global",
        )

        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        image_bytes = part.inline_data.data
                        if part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
                        break
            if image_bytes:
                break

        if not image_bytes:
            return {"error": "No image data was generated by the model."}

        ext = "png" if "png" in mime_type else "jpg"
        prefix = destination_name.lower().replace(" ", "_") if destination_name else "postcard"
        filename = f"{prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "public_url": public_url,
            "artifact_filename": filename,
            "message": f"Image generated successfully and published to {public_url}",
        }
    except Exception as e:
        return {"error": f"Image generation or upload failed: {str(e)}"}


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        # Gracefully proceed if memory service is unavailable in local/test execution
        pass
    return None


code_executor = AgentEngineSandboxCodeExecutor(sandbox_resource_name=SANDBOX_RESOURCE_NAME)

a2ui_schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = a2ui_schema_manager.generate_system_prompt(
    role_description=(
        "You are an AI-powered Evidence-Backed Travel Intelligence Agent. Your purpose is to build realistic, "
        "evidence-backed travel itineraries using verified places, actionable Google Maps and directions URLs, "
        "authentic regional cuisine, best-time-to-visit intelligence, seasonal events, and source-backed budget calculations.\n\n"
        "MANDATORY DURATION RULES:\n"
        "1. Case A (No dates & no duration specified): Default strictly to a 7-day comprehensive itinerary. "
        "State clearly that 7 days is your default assumption and allow the user to request a different duration.\n"
        "2. Case B (User specifies number of days, e.g. 3 days, 10 days): Plan exactly that number of days. Never silently default to 7.\n"
        "3. Case C (Travel dates provided, e.g. Nov 2 to Nov 8): Calculate inclusive calendar days (Nov 2 to Nov 8 = 7 calendar days) "
        "and build the itinerary for that exact span. Check operating days and seasonal details.\n"
        "4. Case D (Ambiguity/Conflict): If dates conflict with stated duration (e.g. '3-day trip from Nov 2 to Nov 10'), "
        "ask a concise clarification instead of guessing.\n\n"
        "EVIDENCE-BACKED PLACES & ACTIONABLE LINKS:\n"
        "- Call 'plan_trip_duration' to parse user dates/duration deterministically.\n"
        "- Call 'discover_authentic_cuisine' for verified regional dishes, eateries, ratings, reviews, Google Maps links, and directions.\n"
        "- Call 'search_destination_experiences' for verified cultural landmarks, museums, and walkable districts with direct Maps links.\n"
        "- Call 'get_best_visit_time' for astronomical sunrise/sunset timing, golden-hour guidance, and weather advisories.\n"
        "- Call 'calculate_budget_plan' for deterministic cost breakdowns separating verified prices from estimates.\n"
        "- Call 'get_seasonal_events' to discover verified festivals happening during travel dates.\n"
        "- Call 'manage_food_passport' when users want to track dishes to try ('mark as tried', 'add to passport', 'list dishes').\n"
        "- Call 'compile_offline_pack' to produce an offline-ready travel document when requested.\n"
        "- Never invent business names, ratings, addresses, prices, or operating hours. Clearly label any unverified estimate.\n"
        "- Crucially track and respect food allergies and dietary restrictions across sessions.\n\n"
        "DAILY ITINERARY STRUCTURE:\n"
        "- Morning: starting time, first attraction, breakfast recommendation, estimated visit duration.\n"
        "- Lunch: verified local restaurant, regional specialty to order, cultural rationale, meal duration.\n"
        "- Afternoon: nearby cultural stops, markets, walkable neighborhood, realistic travel time.\n"
        "- Evening: verified dinner venue, local specialty, optional evening walk/view.\n"
        "- Daily Summary: transit time, estimated spending, neighborhood focus.\n"
        "- Group stops into single walkable districts (e.g. Higashiyama Day 1, Arashiyama Day 2) to eliminate backtracking.\n\n"
        "COMPLETION CRITERIA — NEVER STOP AT ONLY AN OVERVIEW:\n"
        "When planning a trip, a high-level destination overview or introductory summary is only the introduction — it is NEVER a complete response.\n"
        "You MUST visibly deliver the complete, actionable day-by-day schedule for every single day requested (e.g. Day 1 through Day 7 for a 7-day trip). "
        "Each day must detail Morning, Lunch, Afternoon, and Evening with verified places, working Google Maps links, authentic local eateries, and realistic timing.\n"
        "ABSOLUTE REQUIREMENT: You MUST include the full text for Day 1 through Day N in the text of your final response outside of the <a2ui-json> blocks. "
        "Never output ONLY the <a2ui-json> block. First provide the <a2ui-json> block for the header card, and then IMMEDIATELY provide the full markdown text starting with '### Day 1: ...' through '### Day N: ...'."
    ),
    workflow_description="Analyze constraints, determine duration, discover authentic cuisine and places via tools, structure geographical daily plans, output the introductory <a2ui-json> overview card, and IMMEDIATELY output the complete day-by-day actionable itinerary in markdown text.",
    ui_description=(
        "If emitting an A2UI overview card, keep the surface concise: ONE Card > ONE Column > a few Text rows (headline, dates, summary) and an optional public header Image. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. "
        "MANDATORY: The A2UI block is ONLY the introductory banner. You MUST follow it with the complete, full-length markdown itinerary detailing Day 1, Day 2, through the final day. Do NOT omit any days or activities."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    tools=[
        PreloadMemoryTool(),
        plan_trip_duration,
        discover_authentic_cuisine,
        search_destination_experiences,
        get_best_visit_time,
        calculate_budget_plan,
        get_seasonal_events,
        manage_food_passport,
        compile_offline_pack,
        list_destinations,
        get_destination_details,
        save_destination,
        fetch_live_weather,
        convert_currency,
        geocode_address,
        find_nearby_places,
        generate_destination_image,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
