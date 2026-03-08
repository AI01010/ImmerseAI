"""
ImmerseAI - Root Orchestrator Agent

Architecture:
- OrchestratorAgent (root): coordinates all specialists, synthesizes final roadmap
  - before_agent_callback: loads user profile from MongoDB
- SequentialAgent (LearningCrew): runs 3 specialists in sequence
  - ProfileAgent:     user skill level + learning history from MongoDB
  - CurriculumAgent:  fetches relevant YouTube videos + resources
  - LogicAgent:       s(CASP) prerequisite checking + gap detection
- Tools: mongodb_tool, youtube_tool, scasp_tool
"""

import os
import logging
import httpx

from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext

from agent.agents.profile_agent import profile_agent
from agent.agents.curriculum_agent import curriculum_agent
from agent.agents.logic_agent import logic_agent
from agent.tools.mongodb_tool import get_user_profile_tool
from agent.tools.youtube_tool import search_youtube_tool
from agent.tools.scasp_tool import check_prerequisites_tool

logger = logging.getLogger(__name__)


# =============================================================================
# BEFORE AGENT CALLBACK — load user context into shared state
# =============================================================================

async def setup_user_context(callback_context: CallbackContext) -> None:
    """
    Runs once when agent starts.
    Loads user profile + learning history from MongoDB into shared state.
    """
    user_id = os.environ.get("USER_ID", "demo_user")
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "")

    logger.info(f"[Callback] Loading context for user: {user_id}")

    callback_context.state["user_id"] = user_id
    callback_context.state["project_id"] = project_id

    # Default state — will be overwritten by ProfileAgent
    callback_context.state["skill_level"] = "beginner"
    callback_context.state["learning_goal"] = "Not specified"
    callback_context.state["learning_history"] = []
    callback_context.state["completed_topics"] = []

    return None


# =============================================================================
# LEARNING CREW (PARALLEL)
# =============================================================================

learning_crew = SequentialAgent(
    name="LearningCrew",
    description="Runs ProfileAgent, CurriculumAgent, and LogicAgent in sequence.",
    sub_agents=[profile_agent, curriculum_agent, logic_agent],
)


# =============================================================================
# ROOT ORCHESTRATOR
# =============================================================================

root_agent = Agent(
    name="ImmerseAI",
    model="gemini-2.5-flash",
    description="Personalized multi-agent learning advisor that builds custom learning roadmaps.",
    instruction="""You are ImmerseAI — a personalized learning advisor that builds custom learning roadmaps.

## User Context
- User ID: {user_id}
- Skill Level: {skill_level}
- Learning Goal: {learning_goal}

---

## WORKFLOW

### STEP 1 — DELEGATE TO LEARNING CREW
Send to LearningCrew to analyze the user in parallel:
- ProfileAgent → current skills, learning history, gaps
- CurriculumAgent → relevant YouTube videos + resources for their level
- LogicAgent → prerequisite checks, knowledge gaps, recommended sequence

### STEP 2 — COLLECT REPORTS
Wait for all three specialists:
- **PROFILE ANALYSIS**: skill level, completed topics, weak areas
- **CURRICULUM ANALYSIS**: top resources matched to user level
- **LOGIC ANALYSIS**: prerequisite gaps, recommended learning order

### STEP 3 — SYNTHESIZE ROADMAP
Produce a structured personalized learning plan:

**LEARNING ROADMAP for {user_id}**

**Current Level:** [from ProfileAgent]
**Goal:** [user's stated goal]
**Estimated Time:** [weeks/hours]

**Phase 1 — Foundations** (if gaps detected by LogicAgent)
- Topic 1: [why this first, prereq reasoning]
- Topic 2: ...

**Phase 2 — Core Skills**
- Topic 3: ...

**Phase 3 — Advanced / Projects**
- Topic N: ...

**Recommended Resources** (from CurriculumAgent)
- 📺 [Video title] — [why relevant] — [YouTube link]
- 📄 [Article/course] — [why relevant]

**Knowledge Gaps to Address First:**
- [Gap 1 from LogicAgent]

**Next Immediate Action:**
→ [Single most important next step]

---

## RULES
- Always personalize to the user's exact skill level
- Never recommend advanced topics before prerequisites are met (trust LogicAgent)
- Keep recommendations concrete and actionable
- Include actual YouTube links when available
- End with one clear next action
""",
    sub_agents=[learning_crew],
    tools=[get_user_profile_tool, search_youtube_tool, check_prerequisites_tool],
    before_agent_callback=setup_user_context,
)
