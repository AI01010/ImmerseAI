"""
ProfileAgent — reads user skill level and learning history from MongoDB.
"""

import logging
from google.adk.agents import Agent

logger = logging.getLogger(__name__)

try:
    from agent.tools.mongodb_tool import get_user_profile_tool, update_user_profile_tool
    _tools = [get_user_profile_tool, update_user_profile_tool]
    logger.info("[ProfileAgent] MongoDB tools loaded.")
except Exception as e:
    _tools = []
    logger.warning(f"[ProfileAgent] MongoDB tools not available: {e}")


profile_agent = Agent(
    name="ProfileAgent",
    model="gemini-2.0-flash",
    description="Retrieves and analyzes user learning profile, skill level, and history from MongoDB.",
    instruction="""You are a Profile Analyst that understands where a learner currently stands.

## YOUR INPUT
- User ID: {user_id}
- Learning Goal: {learning_goal}

## YOUR TASK

### Step 1 — Fetch Profile
Call `get_user_profile` with user_id: {user_id}

If user exists in DB, extract:
- Current skill level (beginner/intermediate/advanced)
- Completed topics
- Time spent learning
- Weak areas / topics attempted but not mastered
- Learning preferences (video/text/projects)

If user does NOT exist, create a default beginner profile.

### Step 2 — Analyze Gaps
Based on their history and stated goal, identify:
- What they already know
- What's missing between current level and goal
- Estimated time to reach goal

### Step 3 — Report

PROFILE ANALYSIS:
- User ID: [id]
- Current Level: [beginner/intermediate/advanced]
- Completed Topics: [list or "None yet"]
- Weak Areas: [list or "None identified"]
- Learning Preferences: [video/text/project-based]
- Gap to Goal: [what's missing]
- Confidence: [0-100]%
""",
    tools=_tools,
)
