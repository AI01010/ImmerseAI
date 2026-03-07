"""
s(CASP) Logic Engine Tool

Uses s(CASP) (stable model semantics with Constraint Answer Set Programming)
for explainable prerequisite checking and learning sequence optimization.

s(CASP) gives us:
- Formal proof trees: WHY a prerequisite is needed
- Negation as failure: "don't recommend X because Y is not met"
- Explainable reasoning: every decision has a logical justification

If s(CASP) binary not available, falls back to Python rule engine.
"""

import os
import json
import logging
import subprocess
import tempfile

logger = logging.getLogger(__name__)

# =============================================================================
# PREREQUISITE KNOWLEDGE GRAPH
# Knowledge base: topic → list of prerequisites
# =============================================================================

PREREQUISITES = {
    # Programming
    "python advanced": ["python basics", "functions", "oop"],
    "machine learning": ["python basics", "numpy", "statistics", "linear algebra"],
    "deep learning": ["machine learning", "calculus", "linear algebra", "python advanced"],
    "neural networks": ["deep learning", "backpropagation"],
    "nlp": ["deep learning", "python advanced", "statistics"],
    "data structures": ["python basics"],
    "algorithms": ["data structures", "math basics"],
    "system design": ["algorithms", "databases", "networking basics"],

    # Web Dev
    "react": ["javascript", "html", "css"],
    "next.js": ["react", "node.js"],
    "node.js": ["javascript"],
    "databases": ["sql basics"],
    "backend development": ["node.js", "databases"],
    "full stack": ["react", "backend development"],

    # Finance / Crypto
    "crypto trading": ["personal finance basics", "blockchain basics"],
    "blockchain development": ["crypto trading", "solidity basics"],
    "options trading": ["stock trading basics", "statistics"],
    "real estate investing": ["personal finance basics", "mortgage basics"],

    # Music
    "music production advanced": ["music theory", "daw basics"],
    "mixing and mastering": ["music production advanced"],

    # General
    "statistics": ["math basics"],
    "linear algebra": ["math basics"],
    "calculus": ["algebra"],
}

# Topics with no prerequisites
BEGINNER_TOPICS = {
    "python basics", "javascript", "html", "css", "math basics",
    "algebra", "personal finance basics", "blockchain basics",
    "music theory", "daw basics", "sql basics", "stock trading basics",
    "networking basics", "mortgage basics",
}


# =============================================================================
# SCASP ENGINE
# =============================================================================

SCASP_PROGRAM_TEMPLATE = """
% ImmerseAI Prerequisite Checker
% s(CASP) rules for learning path validation

% Facts: completed topics
{completed_facts}

% Knowledge base: prerequisite rules
{prereq_rules}

% Query: what prerequisites are missing for the goal?
missing_prereq(Goal, Missing) :-
    requires(Goal, Missing),
    not completed(Missing).

% Query: is goal reachable?
goal_reachable(Goal) :-
    not missing_prereq(Goal, _).

:- not goal_reachable({goal}).
"""


def check_prerequisites(goal: str, completed: list[str], level: str = "beginner") -> dict:
    """
    Check prerequisites for a learning goal using logic rules.

    Args:
        goal: the learning goal e.g. "machine learning"
        completed: list of already completed topics
        level: current skill level

    Returns:
        dict with met_prerequisites, missing_prerequisites, explanation, sequence
    """
    goal_lower = goal.lower().strip()
    completed_lower = [c.lower().strip() for c in completed]

    # Add level-based implicit knowledge
    if level == "intermediate":
        completed_lower += ["python basics", "math basics", "algebra"]
    elif level == "advanced":
        completed_lower += list(BEGINNER_TOPICS)

    # Find direct prerequisites
    direct_prereqs = PREREQUISITES.get(goal_lower, [])

    met = []
    missing = []
    explanations = []

    for prereq in direct_prereqs:
        if prereq in completed_lower or prereq in BEGINNER_TOPICS and level != "beginner":
            met.append(prereq)
        else:
            missing.append(prereq)
            # Build explanation
            why = _why_needed(prereq, goal_lower)
            explanations.append(f"'{prereq}' → needed because: {why}")

    # Try s(CASP) binary if available
    scasp_result = _try_scasp(goal_lower, completed_lower, direct_prereqs)

    return {
        "goal": goal,
        "level": level,
        "met_prerequisites": met,
        "missing_prerequisites": missing,
        "explanations": explanations,
        "goal_reachable": len(missing) == 0,
        "scasp_used": scasp_result is not None,
        "scasp_proof": scasp_result,
        "engine": "s(CASP)" if scasp_result else "Python rule engine",
    }


def get_learning_sequence(goal: str, completed: list[str], level: str = "beginner") -> dict:
    """
    Get the optimal learning sequence to reach a goal.

    Args:
        goal: target learning goal
        completed: already mastered topics
        level: current skill level

    Returns:
        dict with ordered sequence and time estimates
    """
    goal_lower = goal.lower().strip()
    completed_lower = [c.lower().strip() for c in completed]

    sequence = []
    visited = set(completed_lower)

    def _add_topic(topic: str, depth: int = 0):
        if topic in visited or depth > 10:
            return
        prereqs = PREREQUISITES.get(topic, [])
        for prereq in prereqs:
            if prereq not in visited:
                _add_topic(prereq, depth + 1)
        if topic not in visited:
            sequence.append({
                "topic": topic,
                "reason": _why_needed(topic, goal_lower),
                "estimated_hours": _estimate_hours(topic),
            })
            visited.add(topic)

    _add_topic(goal_lower)

    total_hours = sum(s["estimated_hours"] for s in sequence)

    return {
        "goal": goal,
        "sequence": sequence,
        "total_estimated_hours": total_hours,
        "total_estimated_weeks": round(total_hours / 5, 1),  # ~5hrs/week
    }


def _why_needed(prereq: str, goal: str) -> str:
    reasons = {
        "python basics": "foundation for all Python-based ML/AI work",
        "math basics": "required for understanding algorithms and statistics",
        "statistics": "essential for evaluating model performance",
        "linear algebra": "vectors and matrices are the language of ML",
        "calculus": "needed to understand gradient descent and backprop",
        "machine learning": "foundation before specializing in deep learning",
        "javascript": "required for all browser-based React development",
        "data structures": "needed to write efficient algorithms",
    }
    return reasons.get(prereq, f"foundational knowledge required for {goal}")


def _estimate_hours(topic: str) -> int:
    estimates = {
        "python basics": 20, "javascript": 25, "html": 10, "css": 15,
        "math basics": 15, "statistics": 30, "linear algebra": 25,
        "calculus": 30, "machine learning": 60, "deep learning": 80,
        "react": 40, "node.js": 30, "databases": 25, "sql basics": 15,
    }
    return estimates.get(topic, 20)


def _try_scasp(goal: str, completed: list[str], prereqs: list[str]):
    """Attempt to run actual s(CASP) binary if installed."""
    try:
        scasp_bin = os.environ.get("SCASP_BIN", "scasp")
        result = subprocess.run([scasp_bin, "--version"],
                                capture_output=True, timeout=2)
        if result.returncode != 0:
            return None

        completed_facts = "\n".join([f"completed({c})." for c in completed])
        prereq_rules = "\n".join([
            f"requires({goal}, {p})." for p in prereqs
        ])

        program = SCASP_PROGRAM_TEMPLATE.format(
            completed_facts=completed_facts,
            prereq_rules=prereq_rules,
            goal=goal,
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pl', delete=False) as f:
            f.write(program)
            fname = f.name

        result = subprocess.run(
            [scasp_bin, fname],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout if result.returncode == 0 else None

    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


# ADK FunctionTool wrappers
try:
    from google.adk.tools import FunctionTool
    check_prerequisites_tool = FunctionTool(func=check_prerequisites)
    get_learning_sequence_tool = FunctionTool(func=get_learning_sequence)
    logger.info("[s(CASP)] FunctionTools registered.")
except ImportError:
    check_prerequisites_tool = check_prerequisites
    get_learning_sequence_tool = get_learning_sequence
    logger.warning("[s(CASP)] ADK not found — using raw functions.")
