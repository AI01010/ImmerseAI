"""
YouTube Data API tool — searches for learning videos matched to skill level.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"


def search_youtube(query: str, max_results: int = 5) -> list[dict]:
    """
    Search YouTube for educational videos matching a query.

    Args:
        query: search string e.g. "Python for beginners tutorial"
        max_results: number of results to return (default 5)

    Returns:
        List of {title, channel, url, duration, description}
    """
    api_key = os.environ.get("YOUTUBE_API_KEY", "")

    if not api_key:
        logger.warning("[YouTube] YOUTUBE_API_KEY not set — returning mock results")
        return _mock_results(query)

    try:
        # Search for videos
        search_resp = requests.get(
            YOUTUBE_SEARCH_URL,
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "videoCategoryId": "27",  # Education category
                "maxResults": max_results,
                "relevanceLanguage": "en",
                "key": api_key,
            },
            timeout=10,
        )
        search_resp.raise_for_status()
        items = search_resp.json().get("items", [])

        if not items:
            return []

        # Get video durations
        video_ids = [item["id"]["videoId"] for item in items]
        details_resp = requests.get(
            YOUTUBE_VIDEO_URL,
            params={
                "part": "contentDetails,statistics",
                "id": ",".join(video_ids),
                "key": api_key,
            },
            timeout=10,
        )
        details = {
            v["id"]: v for v in details_resp.json().get("items", [])
        }

        results = []
        for item in items:
            vid_id = item["id"]["videoId"]
            snippet = item["snippet"]
            detail = details.get(vid_id, {})
            duration = detail.get("contentDetails", {}).get("duration", "Unknown")

            results.append({
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "description": snippet.get("description", "")[:200],
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "duration": _parse_duration(duration),
                "published": snippet.get("publishedAt", "")[:10],
            })

        logger.info(f"[YouTube] Found {len(results)} results for: {query}")
        return results

    except Exception as e:
        logger.error(f"[YouTube] Search failed: {e}")
        return _mock_results(query)


def _parse_duration(iso_duration: str) -> str:
    """Convert PT1H30M15S → 1h 30m"""
    import re
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
    if not match:
        return "Unknown"
    h, m, s = match.groups()
    parts = []
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s and not h: parts.append(f"{s}s")
    return " ".join(parts) or "Unknown"


def _mock_results(query: str) -> list[dict]:
    """Fallback mock results when API key not set."""
    return [
        {
            "title": f"[Mock] {query} - Complete Tutorial",
            "channel": "Mock Channel",
            "description": f"Learn {query} from scratch in this comprehensive tutorial.",
            "url": "https://www.youtube.com/results?search_query=" + query.replace(" ", "+"),
            "duration": "45m",
            "published": "2024-01-01",
        }
    ]


# ADK FunctionTool wrapper
try:
    from google.adk.tools import FunctionTool
    search_youtube_tool = FunctionTool(func=search_youtube)
    logger.info("[YouTube] FunctionTool registered.")
except ImportError:
    search_youtube_tool = search_youtube
    logger.warning("[YouTube] ADK not found — using raw function.")
