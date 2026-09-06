import re
import urllib.request
import json
import os
import base64


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


def make_request(url: str, headers: dict) -> dict:
    """Helper to make GitHub API requests."""
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def get_all_files(owner: str, repo: str, headers: dict, path: str = "", branch: str = "main") -> list:
    """
    Recursively fetch all file paths from a GitHub repo using the Git Trees API.
    Returns a flat list of file paths.
    """
    # Use git trees API with recursive=1 - single call, gets everything
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        data = make_request(tree_url, headers)
        all_files = [
            item["path"] for item in data.get("tree", [])
            if item["type"] == "blob"
        ]
        return all_files
    except Exception:
        # Fallback: try 'master' branch
        try:
            tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
            data = make_request(tree_url, headers)
            all_files = [
                item["path"] for item in data.get("tree", [])
                if item["type"] == "blob"
            ]
            return all_files
        except Exception:
            return []


def is_code_file(path: str) -> bool:
    """Check if a file is a reviewable code file."""
    code_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c",
        ".h", ".go", ".rs", ".rb", ".php", ".cs", ".kt", ".swift",
        ".r", ".scala", ".sh", ".sql", ".html", ".css", ".vue",
        ".ipynb", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini"
    }
    skip_paths = {
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", "vendor", "migrations"
    }
    # Skip if in ignored folder
    for skip in skip_paths:
        if skip in path:
            return False
    # Check extension
    ext = os.path.splitext(path)[1].lower()
    return ext in code_extensions


def fetch_file_content(owner: str, repo: str, path: str, branch: str, headers: dict) -> str:
    """Fetch content of a single file."""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        data = make_request(url, headers)
        if data.get("encoding") == "base64":
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return content
        return ""
    except Exception:
        return ""


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
            pr_data = make_request(pr_url, headers)

            # Fetch PR files
            diff_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/files"
            files_data = make_request(diff_url, headers)

            diff_content = ""
            files_changed = []
            for f in files_data[:15]:
                fname = f.get("filename", "")
                files_changed.append(fname)
                patch = f.get("patch", "")
                if patch:
                    diff_content += f"\n--- {fname} ---\n{patch}\n"

            return {
                "success": True,
                "pr_title": pr_data.get("title", ""),
                "pr_description": pr_data.get("body", "") or "No description provided.",
                "code_diff": diff_content[:8000],
                "files_changed": files_changed,
            }

        elif parsed["type"] == "file":
            owner, repo = parsed["owner"], parsed["repo"]
            path = parsed["path"]
            branch = parsed.get("branch", "main")

            file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
            file_data = make_request(file_url, headers)
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

            # Get repo info
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            repo_data = make_request(repo_url, headers)

            # Get default branch
            default_branch = repo_data.get("default_branch", "main")

            # Get ALL files recursively
            all_files = get_all_files(owner, repo, headers, branch=default_branch)

            # Filter to only code files
            code_files = [f for f in all_files if is_code_file(f)]

            # Fetch content of each file (max 20 files, 500 chars each to stay within LLM limit)
            diff_content = ""
            files_fetched = []
            char_budget = 7500  # keep under 8000 total

            for fpath in code_files[:20]:
                if len(diff_content) >= char_budget:
                    break
                content = fetch_file_content(owner, repo, fpath, default_branch, headers)
                if content.strip():
                    snippet = content[:400]  # first 400 chars per file
                    diff_content += f"\n{'='*50}\n📄 FILE: {fpath}\n{'='*50}\n{snippet}\n"
                    files_fetched.append(fpath)

            if not diff_content:
                diff_content = f"Repository: {owner}/{repo}\nNo readable code files found."

            # Add repo metadata at top
            meta = (
                f"Repository: {owner}/{repo}\n"
                f"Language: {repo_data.get('language', 'Unknown')}\n"
                f"Stars: {repo_data.get('stargazers_count', 0)}\n"
                f"Total code files found: {len(code_files)}\n"
                f"Files reviewed: {len(files_fetched)}\n\n"
            )

            return {
                "success": True,
                "pr_title": f"Repository Review: {owner}/{repo}",
                "pr_description": (repo_data.get("description") or "No description") + f"\n\nReviewing {len(files_fetched)} files from the repository.",
                "code_diff": (meta + diff_content)[:8000],
                "files_changed": files_fetched,
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