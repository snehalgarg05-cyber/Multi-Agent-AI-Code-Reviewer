# 🔍 AI Code Reviewer

An intelligent code review system powered by 4 specialized AI agents orchestrated with LangGraph. Paste any GitHub URL and get a professional code review in under 2 minutes.

## 🤖 Agent Pipeline

```
GitHub URL
    ↓
🔍 Fetcher Agent    → GitHub API → fetches PR diff / file / repo
    ↓
🧠 Analyzer Agent   → LLM → code quality, complexity, style (scored /10)
    ↓
🐛 Bug Detector     → LLM → bugs, security issues, edge cases
    ↓
✍️ Review Writer    → LLM → professional review + verdict
    ↓
Streamlit UI
```

## 🚀 Setup & Run

```bash
git clone https://github.com/snehalgarg05-cyber/ai-code-reviewer
cd ai-code-reviewer
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
streamlit run app.py
```

## 🔑 API Keys

| Key | Required | Where to get |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | [console.groq.com](https://console.groq.com) — Free |
| `GITHUB_TOKEN` | ❌ Optional | [github.com/settings/tokens](https://github.com/settings/tokens) — Higher rate limits |

## 📎 Supported URLs

- **PR**: `https://github.com/owner/repo/pull/123`
- **File**: `https://github.com/owner/repo/blob/main/path/to/file.py`
- **Repo**: `https://github.com/owner/repo`

## ⚡ Key Engineering Decisions

- **TypedDict ReviewState** — type-safe shared memory across all 4 agents
- **Conditional edge** after Fetcher — if GitHub API fails, pipeline continues with fallback
- **No GitHub token required** — works with public repos on free GitHub API tier
- **Modular agents** — swap any agent without touching others

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| LangGraph | Multi-agent orchestration |
| Groq GPT-OSS | LLM inference |
| GitHub REST API | Code fetching (no auth for public repos) |
| Streamlit | Web UI |
| TypedDict | Type-safe agent state |

## 👨‍💻 Author

**Snehal Garg** | VIT Bhopal | B.Tech CSE 2027
- [LinkedIn](https://linkedin.com/in/snehal-garg)
- [GitHub](https://github.com/snehalgarg05-cyber)
