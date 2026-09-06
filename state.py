from typing import TypedDict, Optional, List


class ReviewState(TypedDict):
    # User input
    github_url: str
    review_focus: str        # "general" | "security" | "performance" | "all"

    # Agent 1: Fetcher
    pr_title: str
    pr_description: str
    code_diff: str
    files_changed: List[str]
    language: str
    fetch_error: Optional[str]

    # Agent 2: Analyzer
    code_quality_report: str
    complexity_issues: str
    style_issues: str
    overall_quality_score: str

    # Agent 3: Bug Detector
    bugs_found: str
    security_issues: str
    edge_cases: str
    severity_level: str      # "low" | "medium" | "high" | "critical"

    # Agent 4: Review Writer
    final_review: str
    summary: str
    approval_status: str     # "approved" | "changes_requested" | "needs_discussion"
    key_improvements: str

    # Pipeline tracking
    processing_log: List[str]
    error: Optional[str]
