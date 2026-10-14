"""User-approved food passport and preferences persistence using Firestore with session-safe fallbacks."""

import datetime
from typing import Any, Dict, List, Optional
import os


class FoodPassportManager:
    """Manages traveler food passport (dishes to try, dishes tried, ratings, and notes)."""

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-03-fe98c55ba1b5")
        self._session_fallback_passport: Dict[str, Dict[str, Any]] = {}

    def _get_db(self):
        try:
            from google.cloud import firestore
            return firestore.Client(project=self.project_id)
        except Exception:
            return None

    def add_or_update_dish(
        self,
        user_id: str,
        dish_name: str,
        destination: str,
        status: str = "want_to_try",  # 'want_to_try' or 'tried'
        rating: Optional[int] = None,
        notes: Optional[str] = None,
        venue_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add or update a dish in the traveler's food passport."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        dish_id = f"{destination.lower().replace(' ', '_')}_{dish_name.lower().replace(' ', '_')}"

        record = {
            "dish_id": dish_id,
            "dish_name": dish_name,
            "destination": destination,
            "status": status,
            "rating": rating,
            "notes": notes,
            "venue_name": venue_name,
            "updated_at": now,
        }

        db = self._get_db()
        if db:
            try:
                doc_ref = db.collection("users").document(user_id).collection("food_passport").document(dish_id)
                doc_ref.set(record, merge=True)
                return {"status": "success", "storage": "firestore", "entry": record}
            except Exception as e:
                pass

        # Fallback to in-memory session
        user_key = f"{user_id}:{dish_id}"
        self._session_fallback_passport[user_key] = record
        return {"status": "success", "storage": "session_fallback", "entry": record}

    def list_passport_dishes(
        self,
        user_id: str,
        destination: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List dishes in the user's food passport."""
        db = self._get_db()
        dishes = []
        if db:
            try:
                coll = db.collection("users").document(user_id).collection("food_passport")
                query = coll
                if destination:
                    query = query.where("destination", "==", destination)
                if status:
                    query = query.where("status", "==", status)
                docs = query.stream()
                dishes = [d.to_dict() for d in docs]
                return dishes
            except Exception:
                pass

        # Fallback query
        for k, v in self._session_fallback_passport.items():
            if k.startswith(f"{user_id}:"):
                if destination and v.get("destination") != destination:
                    continue
                if status and v.get("status") != status:
                    continue
                dishes.append(v)
        return dishes

    def remove_dish(self, user_id: str, dish_name: str, destination: str) -> Dict[str, Any]:
        """Remove a dish entry from the traveler's passport."""
        dish_id = f"{destination.lower().replace(' ', '_')}_{dish_name.lower().replace(' ', '_')}"
        db = self._get_db()
        if db:
            try:
                db.collection("users").document(user_id).collection("food_passport").document(dish_id).delete()
            except Exception:
                pass

        user_key = f"{user_id}:{dish_id}"
        self._session_fallback_passport.pop(user_key, None)
        return {"status": "success", "message": f"Dish '{dish_name}' removed from your food passport."}


# Global instance
food_passport = FoodPassportManager()
