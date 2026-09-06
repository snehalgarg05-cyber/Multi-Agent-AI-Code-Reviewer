import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm import get_llm


def analyzer_agent(state: dict) -> dict:
    log = state.get("processing_log", [])
    log.append("🧠 Analyzer Agent: Analyzing code quality...")

    try:
        llm = get_llm(temperature=0.2)

        messages = [
            SystemMessage(content="""You are a senior software engineer with 10+ years of experience.
Analyze code for quality, complexity, readability, and best practices.
Be specific, constructive, and actionable. Give a score out of 10."""),
            HumanMessage(content=f"""
PR Title: {state.get('pr_title', 'N/A')}
Language: {state.get('language', 'Unknown')}
Files Changed: {', '.join(state.get('files_changed', [])) or 'N/A'}

Code Changes:
{state.get('code_diff', 'No code available')[:4000]}

Analyze and provide:

1. CODE QUALITY SCORE: X/10 (with brief justification)

2. COMPLEXITY ISSUES:
   - List any overly complex functions or logic
   - Identify if functions are doing too many things (violating SRP)
   - Note any deeply nested code

3. READABILITY & STYLE:
   - Variable/function naming
   - Code organization and structure
   - Missing comments or documentation
   - Adherence to language conventions

4. BEST PRACTICES:
   - DRY violations (repeated code)
   - SOLID principles
   - Error handling quality
   - Code modularity

Keep each section concise and actionable.
""")
        ]

        response = llm.invoke(messages)
        analysis = response.content

        # Extract score
        score = "7/10"
        for line in analysis.split('\n'):
            if 'score' in line.lower() and '/' in line:
                import re
                match = re.search(r'(\d+)/10', line)
                if match:
                    score = f"{match.group(1)}/10"
                    break

        log.append(f"✅ Analyzer: Quality score {score}")

        return {
            "code_quality_report": analysis,
            "complexity_issues": analysis,
            "style_issues": analysis,
            "overall_quality_score": score,
            "processing_log": log,
        }

    except Exception as e:
        log.append(f"⚠️ Analyzer Error: {str(e)}")
        return {
            "code_quality_report": f"Analysis failed: {str(e)}",
            "complexity_issues": "Could not analyze",
            "style_issues": "Could not analyze",
            "overall_quality_score": "N/A",
            "processing_log": log,
        }
