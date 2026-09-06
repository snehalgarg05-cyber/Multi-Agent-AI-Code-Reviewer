import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langgraph.graph import StateGraph, END
from state import ReviewState
from agents.fetcher import fetcher_agent
from agents.analyzer import analyzer_agent
from agents.bug_detector import bug_detector_agent
from agents.review_writer import review_writer_agent


def should_continue(state: dict) -> str:
    """After fetcher: if fatal error, skip to writer with error message."""
    if state.get("error") and not state.get("code_diff"):
        return "error"
    return "continue"


def error_handler(state: dict) -> dict:
    log = state.get("processing_log", [])
    log.append("⚠️ Error handler: Using fallback, continuing pipeline...")
    return {
        **state,
        "code_diff": state.get("code_diff", "Could not fetch code."),
        "pr_title": state.get("pr_title", "Code Review"),
        "language": "Unknown",
        "processing_log": log,
        "error": None
    }


def build_pipeline():
    graph = StateGraph(ReviewState)

    graph.add_node("fetcher", fetcher_agent)
    graph.add_node("analyzer", analyzer_agent)
    graph.add_node("bug_detector", bug_detector_agent)
    graph.add_node("review_writer", review_writer_agent)
    graph.add_node("error_handler", error_handler)

    graph.set_entry_point("fetcher")

    graph.add_conditional_edges(
        "fetcher",
        should_continue,
        {
            "continue": "analyzer",
            "error": "error_handler"
        }
    )

    graph.add_edge("analyzer", "bug_detector")
    graph.add_edge("bug_detector", "review_writer")
    graph.add_edge("review_writer", END)
    graph.add_edge("error_handler", "analyzer")

    return graph.compile()


def run_review(github_url: str, review_focus: str = "all") -> dict:
    pipeline = build_pipeline()

    initial_state = {
        "github_url": github_url,
        "review_focus": review_focus,
        "pr_title": "",
        "pr_description": "",
        "code_diff": "",
        "files_changed": [],
        "language": "",
        "fetch_error": None,
        "code_quality_report": "",
        "complexity_issues": "",
        "style_issues": "",
        "overall_quality_score": "",
        "bugs_found": "",
        "security_issues": "",
        "edge_cases": "",
        "severity_level": "",
        "final_review": "",
        "summary": "",
        "approval_status": "",
        "key_improvements": "",
        "processing_log": [f"🚀 Starting code review for: {github_url}"],
        "error": None
    }

    result = pipeline.invoke(initial_state)
    return result
