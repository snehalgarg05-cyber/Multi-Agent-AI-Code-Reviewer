import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm import get_llm


def review_writer_agent(state: dict) -> dict:
    log = state.get("processing_log", [])
    log.append("✍️ Review Writer: Writing final review...")

    try:
        llm = get_llm(temperature=0.4)

        severity = state.get("severity_level", "low")
        score = state.get("overall_quality_score", "N/A")

        messages = [
            SystemMessage(content="""You are a senior software engineer writing a professional,
constructive code review. Your tone is helpful and educational, not harsh.
You provide specific, actionable feedback that helps the developer improve.
Write like a senior engineer who genuinely wants to help."""),
            HumanMessage(content=f"""
Write a complete, professional code review based on this analysis:

PR: {state.get('pr_title', 'N/A')}
Language: {state.get('language', 'Unknown')}
Files: {', '.join(state.get('files_changed', [])) or 'N/A'}
Quality Score: {score}
Severity Level: {severity.upper()}

Quality Analysis:
{state.get('code_quality_report', '')[:2000]}

Bug & Security Report:
{state.get('bugs_found', '')[:2000]}

Write the review with these sections:

## Summary
2-3 sentences overview of the PR and overall impression.

## What's Done Well
2-3 specific positive points (always find something good).

## Issues to Address
List all issues from analysis, grouped by severity.
Format: **[SEVERITY]** Issue description + suggested fix.

## Suggestions for Improvement
2-3 optional improvements that would make the code better
but aren't blockers.

## Code Snippets / Examples
If applicable, show 1-2 short examples of how to fix key issues.

## Verdict
Based on analysis, state one of:
- APPROVED: Ready to merge
- CHANGES REQUESTED: Fix required issues before merging
- NEEDS DISCUSSION: Complex issues need team discussion

End with an encouraging, constructive closing line.
""")
        ]

        response = llm.invoke(messages)
        review = response.content

        # Determine approval status
        review_lower = review.lower()
        if "approved" in review_lower and "changes requested" not in review_lower:
            approval = "approved"
        elif "changes requested" in review_lower or "fix required" in review_lower:
            approval = "changes_requested"
        else:
            approval = "needs_discussion"

        # Generate summary
        summary_messages = [
            SystemMessage(content="Write a 2-sentence executive summary of a code review."),
            HumanMessage(content=f"PR: {state.get('pr_title')}\nScore: {score}\nVerdict: {approval}\nReview excerpt: {review[:500]}\n\nSummary:")
        ]
        summary_resp = llm.invoke(summary_messages)

        # Key improvements
        improvements_messages = [
            SystemMessage(content="Extract exactly 3 key improvement points as short bullet points from this review."),
            HumanMessage(content=f"Review:\n{review[:1000]}\n\nTop 3 improvements:")
        ]
        improvements_resp = llm.invoke(improvements_messages)

        log.append(f"✅ Review Writer: Review complete. Verdict: {approval.upper().replace('_', ' ')}")

        return {
            "final_review": review,
            "summary": summary_resp.content,
            "approval_status": approval,
            "key_improvements": improvements_resp.content,
            "processing_log": log,
        }

    except Exception as e:
        log.append(f"⚠️ Review Writer Error: {str(e)}")
        return {
            "final_review": f"Review generation failed: {str(e)}",
            "summary": "Review could not be generated.",
            "approval_status": "needs_discussion",
            "key_improvements": "Could not extract improvements.",
            "processing_log": log,
        }
