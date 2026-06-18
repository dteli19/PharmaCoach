import streamlit as st
import json
from agents import run_extraction_agent, run_scoring_agent, run_coaching_agent

st.set_page_config(
    page_title="PharmaCoach — AI Sales Call Intelligence",
    page_icon="💊",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0a2342 0%, #126782 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 { font-size: 2rem; font-weight: 700; margin: 0; color: white; }
    .main-header p { font-size: 1rem; color: #a8d8ea; margin: 0.5rem 0 0 0; }
    .score-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .score-number { font-size: 2rem; font-weight: 700; color: #0a2342; }
    .score-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
    .strength-card {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    .improvement-card {
        background: #fff7ed;
        border-left: 4px solid #ea580c;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    .script-card {
        background: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    .objection-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.3rem;
    }
    .tag-safety { background: #fee2e2; color: #dc2626; }
    .tag-cost { background: #fef9c3; color: #ca8a04; }
    .tag-efficacy { background: #dbeafe; color: #2563eb; }
    .tag-competitor { background: #f3e8ff; color: #9333ea; }
    .tag-access { background: #dcfce7; color: #16a34a; }
    .info-card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    .info-label {
        font-size: 0.72rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    .info-value {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>💊 PharmaCoach — AI Sales Call Intelligence</h1>
    <p>Paste a sales call transcript · Get structured summary · SPIN scoring · Personalized coaching</p>
    <p style="font-size:0.8rem; color:#7fb3c8; margin-top:0.3rem;">
        Powered by 3 specialized AI agents · LangChain · Groq Llama 3
    </p>
</div>
""", unsafe_allow_html=True)

with open("sample_data/sample_transcript.txt", "r") as f:
    SAMPLE_TRANSCRIPT = f.read()

with st.sidebar:
    st.markdown("### 📋 How It Works")
    st.markdown("""
**Agent 1 — Call Extractor**
Pulls HCP info, objections, behaviors, clinical claims and outcome from raw transcript

**Agent 2 — Call Scorer**
Scores against SPIN selling framework and FAB objection handling methodology

**Agent 3 — Coaching Generator**
Generates strengths, improvements, word-for-word objection scripts and next call strategy
""")
    st.divider()
    st.markdown("### 💡 Best Used For")
    st.markdown("""
- Post-call coaching sessions
- Sales manager reviews
- Rep self-assessment
- Training and onboarding
""")
    st.divider()
    st.markdown("**🔧 Built with**")
    st.markdown("🔗 LangChain · ⚡ Groq Llama 3")
    st.markdown("🧠 3 Specialized AI Agents")
    st.markdown("📊 SPIN + FAB Frameworks")

col1, col2 = st.columns([1, 1])
with col1:
    use_sample = st.button("📄 Load Sample Transcript", use_container_width=True)
with col2:
    clear = st.button("🗑️ Clear", use_container_width=True)

if clear:
    st.session_state.clear()
    st.rerun()

transcript = st.text_area(
    "Paste your sales call transcript here:",
    value=SAMPLE_TRANSCRIPT if use_sample else st.session_state.get("transcript", ""),
    height=250,
    placeholder="Paste the sales call transcript here or click 'Load Sample Transcript' above..."
)

if transcript:
    st.session_state["transcript"] = transcript

analyze = st.button("🚀 Analyze Call", type="primary", use_container_width=True)

if analyze and transcript:
    with st.spinner("Agent 1 — Extracting call data..."):
        try:
            call_data = run_extraction_agent(transcript)
            st.session_state["call_data"] = call_data
        except Exception as e:
            st.error(f"Agent 1 failed: {str(e)}")
            st.stop()

    with st.spinner("Agent 2 — Scoring call against SPIN & FAB frameworks..."):
        try:
            scores = run_scoring_agent(call_data)
            st.session_state["scores"] = scores
        except Exception as e:
            st.error(f"Agent 2 failed: {str(e)}")
            st.stop()

    with st.spinner("Agent 3 — Generating personalized coaching..."):
        try:
            coaching = run_coaching_agent(call_data, scores)
            st.session_state["coaching"] = coaching
        except Exception as e:
            st.error(f"Agent 3 failed: {str(e)}")
            st.stop()

    st.success("✅ Analysis complete!")

if "call_data" in st.session_state:
    call_data = st.session_state["call_data"]
    scores = st.session_state["scores"]
    coaching = st.session_state["coaching"]

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📋 Call Summary", "📊 SPIN Scores", "🎯 Coaching"])

    with tab1:
        outcome = call_data.get("outcome", "neutral")
        outcome_color = "#16a34a" if outcome == "positive" else "#ea580c" if outcome == "neutral" else "#dc2626"
        outcome_emoji = "✅" if outcome == "positive" else "⚠️" if outcome == "neutral" else "❌"

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown('<div class="info-label">HCP</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("hcp_name", "N/A")}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="info-label">Specialty</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("hcp_specialty", "N/A")}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="info-label">Location</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("hcp_location", "N/A")}</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="info-label">Duration</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("call_duration_estimate", "N/A")}</div>', unsafe_allow_html=True)
        with col5:
            st.markdown('<div class="info-label">Outcome</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value" style="color:{outcome_color};">{outcome_emoji} {outcome.capitalize()}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        next_steps = call_data.get("next_steps", "N/A")
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Next Steps</div>
            <div style="font-size:0.95rem; color:#374151; margin-top:0.3rem;">{next_steps}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🎯 Products Discussed**")
            for p in call_data.get("products_discussed", []):
                st.markdown(f"- {p}")

            st.markdown("**🔬 Clinical Claims Made**")
            for claim in call_data.get("clinical_claims", []):
                st.markdown(f"- {claim}")

        with col2:
            st.markdown("**⚠️ Objections Raised**")
            for obj in call_data.get("objections", []):
                obj_type = obj.get("type", "cost")
                tag_class = f"tag-{obj_type}"
                st.markdown(
                    f'<span class="objection-tag {tag_class}">{obj_type.upper()}</span> {obj.get("description", "")}',
                    unsafe_allow_html=True
                )
                st.markdown(f"*Rep response: {obj.get('rep_response', '')}*")
                st.markdown("")

            st.markdown("**✅ Rep Behaviors Observed**")
            for behavior in call_data.get("rep_behaviors", []):
                st.markdown(f"- {behavior}")

    with tab2:
        overall = scores.get("overall_score", 0)
        score_color = "#16a34a" if overall >= 8 else "#ea580c" if overall >= 6 else "#dc2626"

        st.markdown(f"""
        <div style="text-align:center; padding:1.5rem; background:#f8fafc;
                    border-radius:12px; margin-bottom:1.5rem; border:1px solid #e2e8f0;">
            <div style="font-size:3.5rem; font-weight:700; color:{score_color};">{overall}/10</div>
            <div style="font-size:1rem; color:#64748b; margin-top:0.3rem;">Overall Call Score</div>
            <div style="font-size:0.9rem; color:#374151; margin-top:0.5rem; font-style:italic;">
                {scores.get("overall_justification", "")}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**📐 SPIN Selling Breakdown**")
        spin = scores.get("spin_scores", {})
        spin_cols = st.columns(4)
        for i, (dimension, label) in enumerate([
            ("situation", "Situation"),
            ("problem", "Problem"),
            ("implication", "Implication"),
            ("need_payoff", "Need-Payoff")
        ]):
            with spin_cols[i]:
                d = spin.get(dimension, {})
                score = d.get("score", 0)
                sc = "#16a34a" if score >= 8 else "#ea580c" if score >= 6 else "#dc2626"
                st.markdown(f"""
                <div class="score-card">
                    <div class="score-number" style="color:{sc};">{score}</div>
                    <div class="score-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
                st.caption(d.get("justification", ""))

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🗣️ Objection Handling (FAB)**")
            oh = scores.get("objection_handling_score", {})
            oh_score = oh.get("score", 0)
            oh_color = "#16a34a" if oh_score >= 8 else "#ea580c" if oh_score >= 6 else "#dc2626"
            st.markdown(f'<span style="font-size:1.5rem; font-weight:700; color:{oh_color};">{oh_score}/10</span>', unsafe_allow_html=True)
            st.caption(oh.get("justification", ""))
        with col2:
            st.markdown("**⚖️ Compliance Score**")
            cs = scores.get("compliance_score", {})
            cs_score = cs.get("score", 0)
            cs_color = "#16a34a" if cs_score >= 8 else "#ea580c" if cs_score >= 6 else "#dc2626"
            st.markdown(f'<span style="font-size:1.5rem; font-weight:700; color:{cs_color};">{cs_score}/10</span>', unsafe_allow_html=True)
            st.caption(cs.get("justification", ""))

    with tab3:
        priority = coaching.get("priority_message", "")
        if priority:
            st.markdown(f"""
            <div style="background:#fef3c7; border:1px solid #f59e0b;
                        border-radius:8px; padding:1rem; margin-bottom:1rem;">
                <strong>⭐ Priority Coaching Point:</strong> {priority}
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ Strengths**")
            for s in coaching.get("strengths", []):
                st.markdown(f"""
                <div class="strength-card">
                    <strong>{s.get("point", "")}</strong><br>
                    <em style="font-size:0.85rem; color:#166534;">{s.get("example", "")}</em>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("**🔧 Areas to Improve**")
            for imp in coaching.get("improvements", []):
                st.markdown(f"""
                <div class="improvement-card">
                    <strong>{imp.get("point", "")}</strong><br>
                    <em style="font-size:0.85rem; color:#9a3412;">Action: {imp.get("action", "")}</em>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**📝 Objection Handling Scripts**")
        for script in coaching.get("objection_scripts", []):
            st.markdown(f"""
            <div class="script-card">
                <strong style="color:#1d4ed8;">Objection: {script.get("objection", "")}</strong><br><br>
                <em>"{script.get("suggested_script", "")}"</em>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**🎯 Next Call Strategy**")
        st.info(coaching.get("next_call_strategy", ""))