"""
CurriculumAgent — fetches and ranks learning resources via YouTube Data API.
"""

import logging
from google.adk.agents import Agent

logger = logging.getLogger(__name__)

try:
    from agent.tools.youtube_tool import search_youtube_tool
    _tools = [search_youtube_tool]
    logger.info("[CurriculumAgent] YouTube tool loaded.")
except Exception as e:
    _tools = []
    logger.warning(f"[CurriculumAgent] YouTube tool not available: {e}")


curriculum_agent = Agent(
    name="CurriculumAgent",
    description="Finds and ranks the best learning resources matched to user's skill level and goal.",
    model="gemini-2.0-flash",
    instruction="""You are a Curriculum Specialist that finds the best learning resources.

## YOUR INPUT
- User Skill Level: {skill_level}
- Learning Goal: {learning_goal}
- Completed Topics: {completed_topics}

## YOUR TASK

### Step 1 — Search for Resources
Call `search_youtube` with queries tailored to the user's level. Examples:
- "{learning_goal} for beginners tutorial"
- "{learning_goal} intermediate projects"
- "{learning_goal} crash course"

Run 2-3 searches with different queries to get diverse results.

### Step 2 — Rank and Filter
From results, select the top 5 most relevant videos:
- Match difficulty to skill level
- Prefer concise, high-quality tutorials
- Skip duplicates or overly long videos (>2hrs) for beginners
- Prioritize channels with proven educational content

### Step 3 — Report

CURRICULUM ANALYSIS:
- Top Resources:
  1. [Title] — [Channel] — [Duration] — [URL] — [Why relevant]
  2. ...
  3. ...
  4. ...
  5. ...
- Recommended Learning Path Order: [1 → 3 → 2 → ...]
- Estimated Total Learning Time: [X hours]
- Confidence: [0-100]%
""",
    tools=_tools,
)
