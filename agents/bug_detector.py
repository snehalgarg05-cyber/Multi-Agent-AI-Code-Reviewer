import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm import get_llm


def bug_detector_agent(state: dict) -> dict:
    log = state.get("processing_log", [])
    log.append("🐛 Bug Detector: Scanning for bugs and security issues...")

    try:
        llm = get_llm(temperature=0.1)

        focus = state.get("review_focus", "all")
        focus_instruction = ""
        if focus == "security":
            focus_instruction = "Focus heavily on security vulnerabilities."
        elif focus == "performance":
            focus_instruction = "Focus heavily on performance bottlenecks."

        messages = [
            SystemMessage(content=f"""You are a security-focused code reviewer and bug hunter.
Your job is to find bugs, vulnerabilities, and edge cases in code.
Be thorough but specific — only flag real issues, not hypothetical ones.
{focus_instruction}"""),
            HumanMessage(content=f"""
PR Title: {state.get('pr_title', 'N/A')}
Language: {state.get('language', 'Unknown')}

Code Changes:
{state.get('code_diff', 'No code available')[:4000]}

Find and report:

1. BUGS FOUND:
   - Logic errors
   - Off-by-one errors
   - Null/None pointer issues
   - Incorrect data type handling
   - Race conditions (if applicable)
   Format: [SEVERITY: LOW/MEDIUM/HIGH] Description + Line reference if possible

2. SECURITY VULNERABILITIES:
   - SQL injection risks
   - XSS vulnerabilities
   - Hardcoded secrets or credentials
   - Insecure data handling
   - Missing input validation
   - Authentication/authorization issues
   Format: [CRITICAL/HIGH/MEDIUM/LOW] Description

3. EDGE CASES NOT HANDLED:
   - Empty input handling
   - Large data handling
   - Network failure handling
   - Concurrent access issues

4. OVERALL SEVERITY: LOW / MEDIUM / HIGH / CRITICAL
   (based on the worst issue found)

If no issues found in a category, write "None found — looks good!"
""")
        ]

        response = llm.invoke(messages)
        bug_report = response.content

        # Determine severity
        severity = "low"
        report_lower = bug_report.lower()
        if "critical" in report_lower:
            severity = "critical"
        elif "high" in report_lower:
            severity = "high"
        elif "medium" in report_lower:
            severity = "medium"

        log.append(f"✅ Bug Detector: Scan complete. Severity: {severity.upper()}")

        return {
            "bugs_found": bug_report,
            "security_issues": bug_report,
            "edge_cases": bug_report,
            "severity_level": severity,
            "processing_log": log,
        }

    except Exception as e:
        log.append(f"⚠️ Bug Detector Error: {str(e)}")
        return {
            "bugs_found": f"Bug scan failed: {str(e)}",
            "security_issues": "Could not scan",
            "edge_cases": "Could not scan",
            "severity_level": "unknown",
            "processing_log": log,
        }
