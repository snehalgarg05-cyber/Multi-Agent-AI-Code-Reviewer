import re
import urllib.request
import json
import os


def parse_github_url(url: str) -> dict:
    """
    Parse GitHub URL and extract owner, repo, PR number or file info.
    Supports:
    - PR: https://github.com/owner/repo/pull/123
    - File: https://github.com/owner/repo/blob/branch/path/to/file.py
    - Repo: https://github.com/owner/repo
    """
    url = url.strip().rstrip('/')

    # PR URL
    pr_pattern = r'github\.com/([^/]+)/([^/]+)/pull/(\d+)'
    pr_match = re.search(pr_pattern, url)
    if pr_match:
        return {
            "type": "pr",
            "owner": pr_match.group(1),
            "repo": pr_match.group(2),
            "pr_number": int(pr_match.group(3))
        }

    # File URL
    file_pattern = r'github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)'
    file_match = re.search(file_pattern, url)
    if file_match:
        return {
            "type": "file",
            "owner": file_match.group(1),
            "repo": file_match.group(2),
            "branch": file_match.group(3),
            "path": file_match.group(4)
        }

    # Repo URL
    repo_pattern = r'github\.com/([^/]+)/([^/]+)$'
    repo_match = re.search(repo_pattern, url)
    if repo_match:
        return {
            "type": "repo",
            "owner": repo_match.group(1),
            "repo": repo_match.group(2)
        }

    return {"type": "unknown"}


def fetch_github_content(parsed: dict) -> dict:
    """Fetch content from GitHub API (no auth needed for public repos)."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CodeReviewerAI/1.0"
    }

    token = os.getenv("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        if parsed["type"] == "pr":
            owner, repo, pr_num = parsed["owner"], parsed["repo"], parsed["pr_number"]

            # Fetch PR details
            pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}"
            req = urllib.request.Request(pr_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                pr_data = json.loads(resp.read())

            # Fetch PR diff
            diff_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/files"
            req = urllib.request.Request(diff_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                files_data = json.loads(resp.read())

            # Build diff string
            diff_content = ""
            files_changed = []
            for f in files_data[:10]:  # max 10 files
                fname = f.get("filename", "")
                files_changed.append(fname)
                patch = f.get("patch", "")
                if patch:
                    diff_content += f"\n--- {fname} ---\n{patch}\n"

            return {
                "success": True,
                "pr_title": pr_data.get("title", ""),
                "pr_description": pr_data.get("body", "") or "No description provided.",
                "code_diff": diff_content[:8000],  # limit size
                "files_changed": files_changed,
            }

        elif parsed["type"] == "file":
            owner, repo = parsed["owner"], parsed["repo"]
            path = parsed["path"]
            branch = parsed.get("branch", "main")

            file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
            req = urllib.request.Request(file_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                file_data = json.loads(resp.read())

            import base64
            content = base64.b64decode(file_data.get("content", "")).decode("utf-8", errors="replace")

            return {
                "success": True,
                "pr_title": f"File Review: {path}",
                "pr_description": f"Reviewing file: {path} from {owner}/{repo}",
                "code_diff": content[:8000],
                "files_changed": [path],
            }

        elif parsed["type"] == "repo":
            owner, repo = parsed["owner"], parsed["repo"]

            # Get repo info and README
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            req = urllib.request.Request(repo_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                repo_data = json.loads(resp.read())

            # Get recent commits
            commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=3"
            req = urllib.request.Request(commits_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                commits_data = json.loads(resp.read())

            commit_info = "\n".join([
                f"- {c['commit']['message'][:80]}"
                for c in commits_data[:3]
            ])

            return {
                "success": True,
                "pr_title": f"Repository Review: {owner}/{repo}",
                "pr_description": repo_data.get("description", "No description") + f"\n\nRecent commits:\n{commit_info}",
                "code_diff": f"Repository: {owner}/{repo}\nLanguage: {repo_data.get('language', 'Unknown')}\nStars: {repo_data.get('stargazers_count', 0)}\nForks: {repo_data.get('forks_count', 0)}",
                "files_changed": [],
            }

    except Exception as e:
        return {"success": False, "error": str(e)}

    return {"success": False, "error": "Unsupported URL type"}


def detect_language(files: list) -> str:
    """Detect primary programming language from file extensions."""
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".java": "Java", ".cpp": "C++", ".c": "C", ".go": "Go",
        ".rs": "Rust", ".rb": "Ruby", ".php": "PHP", ".cs": "C#",
        ".kt": "Kotlin", ".swift": "Swift", ".r": "R",
    }
    counts = {}
    for f in files:
        for ext, lang in ext_map.items():
            if f.endswith(ext):
                counts[lang] = counts.get(lang, 0) + 1
    if counts:
        return max(counts, key=counts.get)
    return "Unknown"
