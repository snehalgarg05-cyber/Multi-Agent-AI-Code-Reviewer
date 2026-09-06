import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import time
from pipeline import run_review

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Dark tech theme - different from content studio */
    .stApp { background: #0d1117; }

    .main-title {
        font-size: 2.4rem; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #00ff88, #00d4ff, #7b61ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sub-text { text-align: center; color: #8b949e; font-size: 1rem; margin-bottom: 1rem; }

    p, li { color: #c9d1d9 !important; }
    h1, h2, h3 { color: #f0f6fc !important; }
    label { color: #8b949e !important; }

    .stTextInput input {
        background: #161b22; color: #c9d1d9;
        border: 1.5px solid #00d4ff; border-radius: 8px;
        font-family: 'Fira Code', monospace;
    }
    .stTextInput label { color: #8b949e !important; }
    .stTextArea textarea {
        background: #161b22; color: #c9d1d9;
        border: 1px solid #30363d; font-family: 'Fira Code', monospace;
    }
    .stSelectbox label { color: #8b949e !important; }

    .stButton > button {
        background: linear-gradient(135deg, #00ff88, #00d4ff);
        color: #0d1117 !important; border: none;
        border-radius: 8px; font-size: 1rem; font-weight: 800;
    }
    .stButton > button:hover { opacity: 0.88; }

    .stTabs [data-baseweb="tab-list"] {
        background: #161b22; border-radius: 8px;
        padding: 4px; border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] { color: #8b949e !important; font-weight: 500; }
    .stTabs [aria-selected="true"] {
        background: #00ff8820 !important;
        color: #00ff88 !important; border-radius: 6px;
        border: 1px solid #00ff88 !important;
    }

    [data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown { color: #c9d1d9 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #f0f6fc !important; }

    .stMetric label { color: #8b949e !important; font-size: 0.82rem !important; }
    .stMetric [data-testid="metric-container"] {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 8px; padding: 0.8rem;
    }

    .stDownloadButton button {
        background: #161b22; color: #00d4ff !important;
        border: 1px solid #00d4ff; border-radius: 6px; font-weight: 600;
    }

    .stSuccess { background: #0d1f17 !important; border: 1px solid #00ff88; border-radius: 8px; color: #00ff88 !important; }
    .stError { background: #1f0d0d !important; border: 1px solid #ff4444; border-radius: 8px; color: #ff6666 !important; }
    .stInfo { background: #0d1521 !important; border: 1px solid #00d4ff; border-radius: 8px; color: #00d4ff !important; }

    .verdict-approved { background: #0d1f17; border: 1.5px solid #00ff88; border-radius: 10px; padding: 1rem; color: #00ff88; }
    .verdict-changes { background: #1f0d0d; border: 1.5px solid #ff4444; border-radius: 10px; padding: 1rem; color: #ff6666; }
    .verdict-discuss { background: #1a1600; border: 1.5px solid #ffd700; border-radius: 10px; padding: 1rem; color: #ffd700; }

    .stExpander { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }

    /* Code font for inputs */
    code { background: #161b22; color: #00ff88; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }

    #MainMenu { visibility: hidden; } footer { visibility: hidden; } header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🔍 AI Code Reviewer</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">4 AI agents that review your code like a senior engineer — bugs, security, quality, all in one click</p>', unsafe_allow_html=True)

st.markdown("""
<div style='display:flex; justify-content:center; gap:8px; padding:0.8rem 0; flex-wrap:wrap;'>
<span style='background:#001a0d; border:1.5px solid #00ff88; color:#00ff88; padding:4px 14px; border-radius:6px; font-size:12px; font-weight:700; font-family:monospace;'>🔍 Fetcher</span>
<span style='color:#30363d; font-size:1.2rem;'>→</span>
<span style='background:#001520; border:1.5px solid #00d4ff; color:#00d4ff; padding:4px 14px; border-radius:6px; font-size:12px; font-weight:700; font-family:monospace;'>🧠 Analyzer</span>
<span style='color:#30363d; font-size:1.2rem;'>→</span>
<span style='background:#1a0000; border:1.5px solid #ff4444; color:#ff6666; padding:4px 14px; border-radius:6px; font-size:12px; font-weight:700; font-family:monospace;'>🐛 Bug Detector</span>
<span style='color:#30363d; font-size:1.2rem;'>→</span>
<span style='background:#1a1400; border:1.5px solid #ffd700; color:#ffd700; padding:4px 14px; border-radius:6px; font-size:12px; font-weight:700; font-family:monospace;'>✍️ Review Writer</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    review_focus = st.selectbox("Review Focus", [
        "all", "security", "performance", "code quality"
    ], format_func=lambda x: {
        "all": "🔍 All (Recommended)",
        "security": "🔒 Security Focus",
        "performance": "⚡ Performance Focus",
        "code quality": "✨ Code Quality Focus"
    }[x])

    st.divider()
    st.markdown("### 🤖 What I Review")
    st.markdown("✅ Code quality & complexity")
    st.markdown("✅ Bugs & logic errors")
    st.markdown("✅ Security vulnerabilities")
    st.markdown("✅ Best practices (SOLID, DRY)")
    st.markdown("✅ Edge cases")
    st.markdown("✅ Naming & readability")

    st.divider()
    st.markdown("### 📎 Supported URLs")
    st.code("github.com/owner/repo/pull/123")
    st.code("github.com/owner/repo/blob/main/file.py")
    st.code("github.com/owner/repo")

    st.divider()
    st.markdown("### 🛠️ Stack")
    st.markdown("**LangGraph** · Groq · GitHub API · Streamlit")

# Input
col1, col2 = st.columns([4, 1])
with col1:
    github_url = st.text_input(
        "🔗 GitHub URL",
        placeholder="https://github.com/owner/repo/pull/123"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    review_btn = st.button("🔍 Review", use_container_width=True)

st.markdown("""
<div style='font-size:11px; color:#8b949e; margin-top:-8px;'>
Try: &nbsp;<code>github.com/snehalgarg05-cyber/Content-Creator-Multi-Agent-AI</code>
</div>
""", unsafe_allow_html=True)

# Run Review
if review_btn:
    if not github_url.strip():
        st.error("Please enter a GitHub URL!")
    else:
        progress = st.progress(0)
        status = st.empty()

        try:
            status.markdown("### 🔍 Agent 1: Fetching code from GitHub...")
            progress.progress(10)

            result = run_review(github_url.strip(), review_focus)

            status.markdown("### 🧠 Agent 2: Analyzing code quality...")
            progress.progress(40)
            time.sleep(0.3)

            status.markdown("### 🐛 Agent 3: Scanning for bugs & security issues...")
            progress.progress(70)
            time.sleep(0.3)

            status.markdown("### ✍️ Agent 4: Writing professional review...")
            progress.progress(95)
            time.sleep(0.3)

            progress.progress(100)
            status.empty()
            progress.empty()

            st.session_state["result"] = result
            st.session_state["url"] = github_url
            st.success(f"✅ Review complete: **{result.get('pr_title', github_url)}**")

        except Exception as e:
            progress.empty()
            status.empty()
            st.error(f"Error: {str(e)}")
            st.info("Check your GROQ_API_KEY in .env file")

# Display Results
if "result" in st.session_state:
    result = st.session_state["result"]

    st.divider()
    st.markdown(f"## 📋 `{result.get('pr_title', 'Code Review')}`")

    # Verdict banner
    approval = result.get("approval_status", "needs_discussion")
    if approval == "approved":
        st.markdown(f"""<div class="verdict-approved">
        <strong>✅ APPROVED</strong> — Code is ready to merge!<br>
        <small style='color:#8b949e'>{result.get('summary', '')}</small>
        </div>""", unsafe_allow_html=True)
    elif approval == "changes_requested":
        st.markdown(f"""<div class="verdict-changes">
        <strong>🔄 CHANGES REQUESTED</strong> — Fix issues before merging.<br>
        <small style='color:#8b949e'>{result.get('summary', '')}</small>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="verdict-discuss">
        <strong>💬 NEEDS DISCUSSION</strong> — Complex issues need team review.<br>
        <small style='color:#8b949e'>{result.get('summary', '')}</small>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Quality Score", result.get("overall_quality_score", "N/A"))
    with col2:
        severity = result.get("severity_level", "unknown").upper()
        icon = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴", "CRITICAL": "🚨"}.get(severity, "⚪")
        st.metric("🐛 Severity", f"{icon} {severity}")
    with col3:
        st.metric("📁 Files", len(result.get("files_changed", [])))
    with col4:
        st.metric("💻 Language", result.get("language", "Unknown"))

    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Full Review",
        "🧠 Quality",
        "🐛 Bugs & Security",
        "⚡ Improvements",
        "⚙️ Pipeline Log"
    ])

    with tab1:
        st.markdown("### 📝 Complete Code Review")
        st.markdown(result.get("final_review", "No review generated"))
        st.download_button(
            "⬇️ Download Review (.md)",
            data=result.get("final_review", ""),
            file_name="code_review.md",
            mime="text/markdown"
        )

    with tab2:
        st.markdown("### 🧠 Code Quality Analysis")
        st.markdown(result.get("code_quality_report", "No analysis available"))

    with tab3:
        st.markdown("### 🐛 Bugs & Security Report")
        severity = result.get("severity_level", "").upper()
        if severity in ["HIGH", "CRITICAL"]:
            st.error(f"⚠️ Severity: {severity}")
        elif severity == "MEDIUM":
            st.warning(f"⚠️ Severity: {severity}")
        else:
            st.success(f"✅ Severity: {severity or 'LOW'}")
        st.markdown(result.get("bugs_found", "No bug report available"))

    with tab4:
        st.markdown("### ⚡ Top Improvements")
        st.markdown(result.get("key_improvements", "No improvements listed"))
        if result.get("files_changed"):
            st.markdown("**Files Reviewed:**")
            for f in result.get("files_changed", []):
                st.markdown(f"• `{f}`")

    with tab5:
        st.markdown("### ⚙️ Agent Processing Log")
        for entry in result.get("processing_log", []):
            st.markdown(
                f"<div style='padding:5px 0; border-bottom:1px solid #21262d;"
                f"font-size:13px; color:#8b949e; font-family:monospace;'>{entry}</div>",
                unsafe_allow_html=True
            )

st.divider()
st.markdown(
    "<div style='text-align:center; color:#8b949e; font-size:12px; font-family:monospace;'>"
    "Built by <strong style='color:#00ff88'>Snehal Garg</strong> &nbsp;|&nbsp; "
    "LangGraph · Groq · GitHub API · Streamlit &nbsp;|&nbsp; "
    "<a href='https://github.com/snehalgarg05-cyber' style='color:#00d4ff; text-decoration:none;'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)