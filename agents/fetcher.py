import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.github_parser import parse_github_url, fetch_github_content, detect_language


def fetcher_agent(state: dict) -> dict:
    log = state.get("processing_log", [])
    log.append("🔍 Fetcher Agent: Fetching code from GitHub...")

    url = state.get("github_url", "").strip()

    if not url:
        log.append("❌ Fetcher: No URL provided")
        return {
            "fetch_error": "No GitHub URL provided",
            "processing_log": log,
            "error": "No URL"
        }

    try:
        parsed = parse_github_url(url)

        if parsed["type"] == "unknown":
            log.append("❌ Fetcher: Invalid GitHub URL format")
            return {
                "fetch_error": "Invalid GitHub URL. Please provide a PR, file, or repo URL.",
                "processing_log": log,
                "error": "Invalid URL"
            }

        result = fetch_github_content(parsed)

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            log.append(f"❌ Fetcher Error: {error_msg}")

            # Fallback — use URL info for review
            return {
                "pr_title": f"Code Review: {url}",
                "pr_description": "Could not fetch via API. Using URL-based review.",
                "code_diff": f"URL: {url}\nNote: API fetch failed — {error_msg}",
                "files_changed": [],
                "language": "Unknown",
                "fetch_error": error_msg,
                "processing_log": log,
                "error": None
            }

        files = result.get("files_changed", [])
        language = detect_language(files)

        log.append(f"✅ Fetcher: Got {len(files)} file(s) | Language: {language}")

        return {
            "pr_title": result.get("pr_title", ""),
            "pr_description": result.get("pr_description", ""),
            "code_diff": result.get("code_diff", ""),
            "files_changed": files,
            "language": language,
            "fetch_error": None,
            "processing_log": log,
            "error": None
        }

    except Exception as e:
        log.append(f"❌ Fetcher Exception: {str(e)}")
        return {
            "pr_title": "Code Review",
            "pr_description": "",
            "code_diff": f"Fetch failed: {str(e)}",
            "files_changed": [],
            "language": "Unknown",
            "fetch_error": str(e),
            "processing_log": log,
            "error": str(e)
        }
