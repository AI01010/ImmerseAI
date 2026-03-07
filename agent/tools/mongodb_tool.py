"""
MongoDB Atlas tool — user profile + learning history storage.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Lazy import motor (async MongoDB) to avoid startup crash if not installed
_client = None

def _get_db():
    global _client
    try:
        from pymongo import MongoClient
        if _client is None:
            uri = os.environ.get("MONGODB_URI", "")
            if not uri:
                raise ValueError("MONGODB_URI not set")
            _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        db_name = os.environ.get("MONGODB_DB", "immerse_ai")
        return _client[db_name]
    except Exception as e:
        logger.error(f"[MongoDB] Connection failed: {e}")
        return None


def get_user_profile(user_id: str) -> dict:
    """
    Fetch user learning profile from MongoDB.

    Args:
        user_id: unique user identifier

    Returns:
        dict with skill_level, completed_topics, learning_history, preferences
    """
    db = _get_db()
    if db is None:
        return _default_profile(user_id)

    try:
        user = db.users.find_one({"user_id": user_id})
        if user:
            user.pop("_id", None)
            logger.info(f"[MongoDB] Found profile for: {user_id}")
            return user
        else:
            logger.info(f"[MongoDB] No profile found for {user_id} — returning defaults")
            return _default_profile(user_id)
    except Exception as e:
        logger.error(f"[MongoDB] Error fetching profile: {e}")
        return _default_profile(user_id)


def update_user_profile(user_id: str, updates: dict) -> dict:
    """
    Update user profile in MongoDB (upsert).

    Args:
        user_id: unique user identifier
        updates: dict of fields to update

    Returns:
        Updated profile
    """
    db = _get_db()
    if db is None:
        return {"error": "MongoDB not available", "user_id": user_id}

    try:
        updates["updated_at"] = datetime.utcnow().isoformat()
        db.users.update_one(
            {"user_id": user_id},
            {"$set": updates},
            upsert=True
        )
        logger.info(f"[MongoDB] Updated profile for: {user_id}")
        return {"success": True, "user_id": user_id, "updated": list(updates.keys())}
    except Exception as e:
        logger.error(f"[MongoDB] Error updating profile: {e}")
        return {"error": str(e)}


def _default_profile(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "skill_level": "beginner",
        "learning_goal": "",
        "completed_topics": [],
        "learning_history": [],
        "weak_areas": [],
        "preferences": "video",
        "total_time_minutes": 0,
        "created_at": datetime.utcnow().isoformat(),
    }


# ADK FunctionTool wrappers
try:
    from google.adk.tools import FunctionTool
    get_user_profile_tool = FunctionTool(func=get_user_profile)
    update_user_profile_tool = FunctionTool(func=update_user_profile)
    logger.info("[MongoDB] FunctionTools registered.")
except ImportError:
    get_user_profile_tool = get_user_profile
    update_user_profile_tool = update_user_profile
    logger.warning("[MongoDB] ADK not found — using raw functions.")
