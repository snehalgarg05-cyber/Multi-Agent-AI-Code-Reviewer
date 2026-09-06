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
    /* Neon sky blue background with yellow shimmer animation */
    .stApp {
        background: linear-gradient(135deg, #00c8ff 0%, #0af 20%, #ffe066 40%, #00e5ff 60%, #ffd700 80%, #00bcd4 100%);
        background-size: 400% 400%;
        animation: shimmer 6s ease infinite;
    }

    @keyframes shimmer {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Overlay for readability */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background: rgba(0, 30, 60, 0.55);
        pointer-events: none;
        z-index: 0;
    }

    /* Main title */
    .main-title {
        font-size: 2.4rem; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #ffffff, #ffe066, #00e5ff, #ffffff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 20px #ffe066cc);
    }

    /* Sub text */
    .sub-text { text-align: center; color: #ffffff; font-size: 1rem; margin-bottom: 1rem; text-shadow: 0 0 10px #00e5ff; }

    /* General text */
    p, li, label { color: #ffffff !important; text-shadow: 0 0 6px #00c8ff88; }
    h1, h2, h3 { color: #ffe066 !important; text-shadow: 0 0 12px #ffe066aa; }
    h4, h5, h6 { color: #00e5ff !important; }

    .stMarkdown p { color: #f0faff !important; }
    .stMarkdown li { color: #f0faff !important; }
    .stMarkdown h2, .stMarkdown h3 { color: #ffe066 !important; }
    .stMarkdown strong { color: #ffe066 !important; }
    .stMarkdown code { background: rgba(0,0,0,0.4); color: #00e5ff !important; border-radius: 4px; padding: 2px 6px; }

    /* Input box */
    .stTextInput input {
        background: rgba(0, 20, 50, 0.7) !important;
        color: #ffffff !important;
        border: 2px solid #00e5ff !important;
        border-radius: 10px;
        box-shadow: 0 0 10px #00e5ff55;
    }
    .stTextInput input::placeholder { color: #a0e8ff !important; }
    .stTextInput label { color: #ffe066 !important; font-weight: 700; }

    /* NEON PINK BUTTON */
    .stButton > button {
        background: linear-gradient(135deg, #ff007f, #ff4da6, #ff0066) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        box-shadow: 0 0 20px #ff007faa, 0 0 40px #ff007f55 !important;
        text-shadow: 0 0 8px #ffffff !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 35px #ff007fff, 0 0 60px #ff007f88 !important;
        transform: scale(1.03) !important;
    }

    /* Download button - neon yellow */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #ffe066, #ffd700) !important;
        color: #001a33 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 0 16px #ffe066aa !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0, 20, 50, 0.6);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #00e5ff;
        box-shadow: 0 0 10px #00e5ff44;
    }
    .stTabs [data-baseweb="tab"] { color: #a0e8ff !important; font-weight: 600; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff007f, #00e5ff) !important;
        color: #ffffff !important;
        border-radius: 8px;
        box-shadow: 0 0 12px #ff007f88;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 10, 40, 0.75) !important;
        border-right: 2px solid #00e5ff;
        box-shadow: 4px 0 20px #00e5ff33;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div { color: #e0f7fa !important; }
    [data-testid="stSidebar"] h3 { color: #ffe066 !important; text-shadow: 0 0 10px #ffe066aa; }
    [data-testid="stSidebar"] code { background: rgba(0,0,0,0.4); color: #00e5ff !important; }

    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        background: rgba(0, 20, 50, 0.7) !important;
        border: 1.5px solid #00e5ff !important;
        border-radius: 8px;
        color: #ffffff !important;
    }

    /* Verdict banners */
    .approved {
        background: rgba(0, 60, 30, 0.7);
        border: 2px solid #00ff88;
        border-radius: 10px; padding: 1rem;
        box-shadow: 0 0 16px #00ff8855;
    }
    .changes {
        background: rgba(60, 0, 0, 0.7);
        border: 2px solid #ff1744;
        border-radius: 10px; padding: 1rem;
        box-shadow: 0 0 16px #ff174455;
    }
    .discuss {
        background: rgba(40, 30, 0, 0.7);
        border: 2px solid #ffe066;
        border-radius: 10px; padding: 1rem;
        box-shadow: 0 0 16px #ffe06655;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(0, 20, 50, 0.65) !important;
        border: 1px solid #00e5ff;
        border-radius: 10px; padding: 0.8rem;
        box-shadow: 0 0 10px #00e5ff33;
    }
    [data-testid="stMetricLabel"] { color: #a0e8ff !important; }
    [data-testid="stMetricValue"] { color: #ffe066 !important; text-shadow: 0 0 8px #ffe066aa; }

    /* Divider */
    hr { border-color: #00e5ff44 !important; }

    /* Log entries */
    .log-entry {
        padding: 6px 0;
        border-bottom: 1px solid rgba(0,229,255,0.15);
        font-size: 13px;
        color: #a0e8ff !important;
    }

    /* Code blocks */
    pre { background: rgba(0,0,0,0.5) !important; border: 1px solid #00e5ff; border-radius: 8px; }
    code { color: #00e5ff !important; }

    /* Progress bar */
    .stProgress > div > div { background: linear-gradient(90deg, #ff007f, #00e5ff, #ffe066) !important; }

    #MainMenu { visibility: hidden; } footer { visibility: hidden; } header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🔍 AI Code Reviewer</div>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">4 AI agents that review your code like a senior engineer</p>', unsafe_allow_html=True)

st.markdown("""
<div style='display:flex; justify-content:center; gap:8px; padding:0.8rem 0; flex-wrap:wrap;'>
<span style='background:rgba(0,20,50,0.6); border:1.5px solid #00e5ff; color:#00e5ff; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; box-shadow:0 0 10px #00e5ff66;'>🔍 Fetcher</span>
<span style='color:#ffe066; font-weight:700;'>→</span>
<span style='background:rgba(0,20,50,0.6); border:1.5px solid #00bcd4; color:#00e5ff; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; box-shadow:0 0 10px #00bcd466;'>🧠 Analyzer</span>
<span style='color:#ffe066; font-weight:700;'>→</span>
<span style='background:rgba(0,20,50,0.6); border:1.5px solid #ffe066; color:#ffe066; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; box-shadow:0 0 10px #ffe06666;'>🐛 Bug Detector</span>
<span style='color:#ffe066; font-weight:700;'>→</span>
<span style='background:rgba(0,20,50,0.6); border:1.5px solid #ff007f; color:#ff4da6; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; box-shadow:0 0 10px #ff007f66;'>✍️ Review Writer</span>
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
    st.markdown("✅ Best practices")
    st.markdown("✅ Edge cases")
    st.markdown("✅ Naming & readability")

    st.divider()
    st.markdown("### 📎 Supported URLs")
    st.markdown("• `github.com/owner/repo/pull/123`")
    st.markdown("• `github.com/owner/repo/blob/main/file.py`")
    st.markdown("• `github.com/owner/repo`")

    st.divider()
    st.markdown("### 🛠️ Built With")
    st.markdown("LangGraph · Groq · GitHub API · Streamlit")

# Input
col1, col2 = st.columns([4, 1])
with col1:
    github_url = st.text_input(
        "🔗 GitHub URL",
        placeholder="https://github.com/owner/repo/pull/123 or file URL or repo URL..."
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    review_btn = st.button("🔍 Review Code", use_container_width=True)

# Example URLs
st.markdown("""
<div style='font-size:12px; color:#a0e8ff; margin-top:-10px;'>
Examples: &nbsp;
<code style='background:rgba(0,0,0,0.4); color:#ffe066; padding:2px 6px; border-radius:4px;'>github.com/openai/openai-python/pull/1</code> &nbsp;|&nbsp;
<code style='background:rgba(0,0,0,0.4); color:#ffe066; padding:2px 6px; border-radius:4px;'>github.com/snehalgarg05-cyber/multi_agent_news_summarizer</code>
</div>
""", unsafe_allow_html=True)

# Run Review
if review_btn:
    if not github_url.strip():
        st.error("Please enter a GitHub URL first!")
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

            status.markdown("### 🐛 Agent 3: Scanning for bugs...")
            progress.progress(70)
            time.sleep(0.3)

            status.markdown("### ✍️ Agent 4: Writing review...")
            progress.progress(95)
            time.sleep(0.3)

            progress.progress(100)
            status.empty()
            progress.empty()

            st.session_state["result"] = result
            st.session_state["url"] = github_url
            st.success(f"✅ Review complete for: **{result.get('pr_title', github_url)}**")

        except Exception as e:
            progress.empty()
            status.empty()
            st.error(f"Error: {str(e)}")
            st.info("Check your GROQ_API_KEY in .env file")

# Display Results
if "result" in st.session_state:
    result = st.session_state["result"]

    st.divider()
    st.markdown(f"## 📋 Review: *{result.get('pr_title', 'Code Review')}*")

    # Verdict banner
    approval = result.get("approval_status", "needs_discussion")
    if approval == "approved":
        st.markdown(f"""<div class="approved">
        <strong style='color:#00ff88;'>✅ APPROVED</strong> — Code is ready to merge!<br>
        <small style='color:#b9fbc0;'>{result.get('summary', '')}</small></div>""", unsafe_allow_html=True)
    elif approval == "changes_requested":
        st.markdown(f"""<div class="changes">
        <strong style='color:#ff5252;'>🔄 CHANGES REQUESTED</strong> — Fix required issues before merging.<br>
        <small style='color:#ffcdd2;'>{result.get('summary', '')}</small></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="discuss">
        <strong style='color:#ffe066;'>💬 NEEDS DISCUSSION</strong> — Complex issues need team review.<br>
        <small style='color:#fff9c4;'>{result.get('summary', '')}</small></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Quality Score", result.get("overall_quality_score", "N/A"))
    with col2:
        severity = result.get("severity_level", "unknown").upper()
        color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴", "CRITICAL": "🚨"}.get(severity, "⚪")
        st.metric("🐛 Severity", f"{color} {severity}")
    with col3:
        st.metric("📁 Files Changed", len(result.get("files_changed", [])))
    with col4:
        st.metric("💻 Language", result.get("language", "Unknown"))

    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Full Review",
        "🧠 Quality Analysis",
        "🐛 Bugs & Security",
        "⚡ Key Improvements",
        "⚙️ Pipeline Log"
    ])

    with tab1:
        st.markdown("### 📝 Complete Code Review")
        st.markdown(result.get("final_review", "No review generated"))
        st.download_button(
            "⬇️ Download Review",
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
            st.error(f"⚠️ Severity Level: {severity}")
        elif severity == "MEDIUM":
            st.warning(f"⚠️ Severity Level: {severity}")
        else:
            st.success(f"✅ Severity Level: {severity or 'LOW'}")
        st.markdown(result.get("bugs_found", "No bugs report available"))

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
                f"<div class='log-entry'>{entry}</div>",
                unsafe_allow_html=True
            )

st.divider()
st.markdown(
    "<div style='text-align:center; color:#a0e8ff; font-size:13px;'>"
    "Built by <strong style='color:#ffe066; text-shadow:0 0 8px #ffe066;'>Snehal Garg</strong> &nbsp;|&nbsp; "
    "<span style='color:#e0f7fa;'>LangGraph · Groq · GitHub API · Streamlit</span> &nbsp;|&nbsp; "
    "<a href='https://github.com/snehalgarg05-cyber' style='color:#00e5ff; text-shadow:0 0 8px #00e5ff;'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)