import streamlit as st
import json
import pandas as pd
import plotly.express as px
from agents import run_extraction_agent, run_scoring_agent, run_coaching_agent
from databricks_connector import save_call_result, get_team_data

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
    <p>Paste any sales call transcript · Get structured summary · SPIN scoring · Personalized coaching</p>
    <p style="font-size:0.8rem; color:#7fb3c8; margin-top:0.3rem;">
        Powered by 3 AI Agents · LangChain · Groq Llama 3 · Databricks Delta Tables
    </p>
</div>
""", unsafe_allow_html=True)

with open("sample_data/sample_transcript.txt", "r") as f:
    T1 = f.read()
with open("sample_data/transcript_2.txt", "r") as f:
    T2 = f.read()
with open("sample_data/transcript_3.txt", "r") as f:
    T3 = f.read()
with open("sample_data/transcript_4.txt", "r") as f:
    T4 = f.read()

with st.sidebar:
    st.markdown("### 📋 How It Works")
    st.markdown("""
**Agent 1 — Call Extractor**
Pulls rep name, HCP info, objections, behaviors, clinical claims and outcome

**Agent 2 — Call Scorer**
Scores against SPIN selling and FAB objection handling

**Agent 3 — Coaching Generator**
Generates strengths, improvements, objection scripts and next call strategy

**Databricks**
Stores every result in Delta Tables for team dashboard
""")
    st.divider()
    st.markdown("**🔧 Built with**")
    st.markdown("🔗 LangChain · ⚡ Groq Llama 3")
    st.markdown("🧠 3 Specialized AI Agents")
    st.markdown("📊 SPIN + FAB Frameworks")
    st.markdown("🗄️ Databricks Delta Tables")
    st.divider()
    st.markdown("**📂 Load a Demo Transcript**")
    sample_choice = st.selectbox(
        "Choose a sample or paste your own below:",
        [
            "— paste your own transcript —",
            "Sarah Mitchell — Strong Call (9/10)",
            "James Okafor — Compliance Issue (4/10)",
            "Aisha Patel — Neutral Call (7/10)",
            "Sarah Mitchell — Closing Call (9/10)"
        ]
    )
    st.caption("Samples show different scoring scenarios for demo purposes.")

# Load selected sample
selected_transcript = ""
if "Strong Call" in sample_choice:
    selected_transcript = T1
elif "Compliance" in sample_choice:
    selected_transcript = T2
elif "Neutral" in sample_choice:
    selected_transcript = T3
elif "Closing" in sample_choice:
    selected_transcript = T4

# Clear button
col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        for key in ["call_data", "scores", "coaching", "transcript"]:
            st.session_state.pop(key, None)
        st.session_state["clear_triggered"] = True
        st.rerun()

# Transcript text area
if st.session_state.get("clear_triggered"):
    st.session_state.pop("clear_triggered", None)
    default_transcript = ""
else:
    default_transcript = selected_transcript or st.session_state.get("transcript", "")

transcript = st.text_area(
    "Sales call transcript:",
    value=default_transcript,
    height=280,
    placeholder="Paste any sales call transcript here — rep notes, CRM entries, call recordings transcribed to text. The agent will extract the rep name automatically."
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

    with st.spinner("Agent 2 — Scoring against SPIN & FAB frameworks..."):
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

    with st.spinner("Saving to Databricks..."):
        try:
            rep_name = call_data.get("rep_name", "Unknown Rep")
            save_call_result(
                rep_name=rep_name,
                call_data=call_data,
                scores=scores,
                coaching=coaching
            )
            st.success(f"✅ Analysis complete for {rep_name} — saved to Databricks!")
        except Exception as e:
            st.success("✅ Analysis complete!")
            st.warning(f"Could not save to Databricks: {str(e)}")

# ── SHOW TABS ──
show_analysis = (
    "call_data" in st.session_state
    and "scores" in st.session_state
    and "coaching" in st.session_state
)

st.divider()

if show_analysis:
    call_data = st.session_state["call_data"]
    scores = st.session_state["scores"]
    coaching = st.session_state["coaching"]
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Call Summary", "📊 SPIN Scores", "🎯 Coaching", "🗄️ Team Dashboard"
    ])
else:
    tab4 = st.tabs(["🗄️ Team Dashboard"])[0]

if show_analysis:
    # ── TAB 1: CALL SUMMARY ──
    with tab1:
        outcome = call_data.get("outcome", "neutral")
        outcome_color = "#16a34a" if outcome == "positive" else "#ea580c" if outcome == "neutral" else "#dc2626"
        outcome_emoji = "✅" if outcome == "positive" else "⚠️" if outcome == "neutral" else "❌"

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown('<div class="info-label">Rep</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("rep_name", "N/A")}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="info-label">HCP</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("hcp_name", "N/A")}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="info-label">Specialty</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("hcp_specialty", "N/A")}</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="info-label">Location</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("hcp_location", "N/A")}</div>', unsafe_allow_html=True)
        with col5:
            st.markdown('<div class="info-label">Duration</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{call_data.get("call_duration_estimate", "N/A")}</div>', unsafe_allow_html=True)
        with col6:
            st.markdown('<div class="info-label">Outcome</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value" style="color:{outcome_color};">{outcome_emoji} {outcome.capitalize()}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        next_steps = call_data.get("next_steps", "N/A")
        st.markdown(f"""
        <div style="background:#f8fafc; border-radius:10px; padding:1rem 1.5rem;
                    margin-bottom:1rem; border:1px solid #e2e8f0;">
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
                st.markdown(
                    f'<span class="objection-tag tag-{obj_type}">{obj_type.upper()}</span> {obj.get("description", "")}',
                    unsafe_allow_html=True
                )
                st.markdown(f"*Rep response: {obj.get('rep_response', '')}*")
                st.markdown("")
            st.markdown("**✅ Rep Behaviors Observed**")
            for behavior in call_data.get("rep_behaviors", []):
                st.markdown(f"- {behavior}")

    # ── TAB 2: SPIN SCORES ──
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

    # ── TAB 3: COACHING ──
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

# ── TAB 4: TEAM DASHBOARD (always visible) ──
with tab4:
    st.markdown("### 🗄️ Team Performance Dashboard")
    st.caption("Data pulled live from Databricks Delta Tables — updates after every call analysis")

    with st.spinner("Loading team data from Databricks..."):
        columns, rows = get_team_data()

    if rows and len(rows) > 0:
        df = pd.DataFrame(rows, columns=columns)
        df['overall_score'] = pd.to_numeric(df['overall_score'], errors='coerce')
        df['compliance_score'] = pd.to_numeric(df['compliance_score'], errors='coerce')
        df['objection_handling_score'] = pd.to_numeric(df['objection_handling_score'], errors='coerce')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Calls Analyzed", len(df))
        with col2:
            st.metric("Avg Overall Score", f"{df['overall_score'].mean():.1f}/10")
        with col3:
            positive_pct = (df['outcome'] == 'positive').sum() / len(df) * 100
            st.metric("Positive Outcomes", f"{positive_pct:.0f}%")
        with col4:
            st.metric("Avg Compliance Score", f"{df['compliance_score'].mean():.1f}/10")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🏆 Rep Leaderboard**")
            leaderboard = df.groupby('rep_name').agg(
                calls=('overall_score', 'count'),
                avg_score=('overall_score', 'mean')
            ).round(1).sort_values('avg_score', ascending=False).reset_index()

            fig = px.bar(
                leaderboard, x='rep_name', y='avg_score',
                color='avg_score',
                color_continuous_scale=['#dc2626', '#ea580c', '#16a34a'],
                title='Average Score by Rep',
                labels={'rep_name': 'Rep', 'avg_score': 'Avg Score'},
                text='avg_score',
                custom_data=['calls']
            )
            fig.update_traces(
                texttemplate='%{text:.1f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Avg Score: %{y:.1f}/10<br>Calls: %{customdata[0]}<extra></extra>'
            )
            fig.update_layout(
                plot_bgcolor='white', paper_bgcolor='white',
                coloraxis_showscale=False, font_color='#1a1a2e',
                yaxis_range=[0, 11]
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("**📞 Calls Analyzed per Rep**")
            calls_cols = st.columns(len(leaderboard))
            for idx, row in leaderboard.iterrows():
                with calls_cols[idx]:
                    st.metric(row['rep_name'].split()[0], f"{int(row['calls'])} calls")

        with col2:
            st.markdown("**📊 Call Outcomes**")
            outcome_counts = df['outcome'].value_counts().reset_index()
            outcome_counts.columns = ['outcome', 'count']
            fig2 = px.pie(
                outcome_counts, values='count', names='outcome',
                color='outcome',
                color_discrete_map={
                    'positive': '#16a34a',
                    'neutral': '#ea580c',
                    'negative': '#dc2626'
                },
                title='Outcome Distribution'
            )
            fig2.update_layout(
                plot_bgcolor='white', paper_bgcolor='white',
                font_color='#1a1a2e'
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**⚠️ Common Objection Types Across Territory**")
        all_objections = []
        for obj_str in df['objection_types'].dropna():
            for obj in obj_str.split(','):
                obj = obj.strip()
                if obj:
                    all_objections.append(obj)

        if all_objections:
            obj_df = pd.Series(all_objections).value_counts().reset_index()
            obj_df.columns = ['objection_type', 'count']
            fig3 = px.bar(
                obj_df, x='objection_type', y='count',
                color='objection_type',
                title='Objection Frequency by Type',
                labels={'objection_type': 'Objection Type', 'count': 'Frequency'}
            )
            fig3.update_layout(
                plot_bgcolor='white', paper_bgcolor='white',
                showlegend=False, font_color='#1a1a2e'
            )
            st.plotly_chart(fig3, use_container_width=True)

        compliance_issues = df[df['compliance_score'] < 7]
        if len(compliance_issues) > 0:
            st.markdown("**🚨 Compliance Alerts**")
            for _, row in compliance_issues.iterrows():
                st.error(f"⚠️ {row['rep_name']} — Call with {row['hcp_name']} scored {row['compliance_score']}/10 on compliance. Priority coaching required.")

        st.markdown("**📋 All Analyzed Calls**")
        display_df = df[['rep_name', 'hcp_name', 'hcp_specialty',
                         'overall_score', 'outcome',
                         'objection_handling_score', 'compliance_score']].copy()
        display_df.columns = ['Rep', 'HCP', 'Specialty', 'Score', 'Outcome', 'Objection Score', 'Compliance']
        st.dataframe(display_df, use_container_width=True)

    else:
        st.info("No team data yet. Analyze a call above to populate the dashboard!")
        st.markdown("Once calls are analyzed you will see:")
        st.markdown("- Rep leaderboard ranked by average SPIN score")
        st.markdown("- Call outcome distribution")
        st.markdown("- Most common objection types across territory")
        st.markdown("- Compliance alerts for low-scoring calls")