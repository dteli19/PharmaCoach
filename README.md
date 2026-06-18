# 💊 PharmaCoach — AI Sales Call Intelligence

An AI-powered pharma sales call analyzer using **3 specialized LangChain agents** to automatically extract structured call data, score against SPIN selling and FAB objection handling frameworks, generate personalized coaching feedback, and store results in **Databricks Delta Tables** for team-level performance dashboards.

🚀 **[Live Demo](https://pharmacoach-yvbdgmwqnxsuz8jiagbox3.streamlit.app/)**

---

## 🎯 Business Problem

Pharma sales managers spend 30-45 minutes per rep manually reviewing call recordings and writing coaching notes. With teams of 20-50 reps each making 5-8 calls per day, consistent coaching at scale is operationally impossible. Most reps receive feedback once a month at best — too infrequent to meaningfully change behavior.

**PharmaCoach compresses the post-call coaching cycle from days to seconds:**

| Metric | Before | With PharmaCoach |
|--------|--------|-----------------|
| Coaching time per call | 30-45 minutes | Under 30 seconds |
| Call review coverage | ~10% of calls | 100% of calls |
| Scoring consistency | Subjective per manager | Standardized SPIN + FAB |
| Data for team insights | Manual spreadsheets | Live Databricks dashboard |

---

## 🤖 Why 3 Agents Instead of 1 Prompt

A single ChatGPT prompt produces free-form text. PharmaCoach uses three specialized agents in sequence — each optimized for one task — producing structured, parseable JSON at every step that feeds the next agent.

```
Raw Sales Call Transcript
         ↓
Agent 1 — Call Extractor
Extracts: rep name, HCP info, objection types,
clinical claims, rep behaviors, outcome, next steps
→ Structured JSON
         ↓
Agent 2 — Call Scorer
Scores: SPIN (4 dimensions), FAB objection handling,
compliance check → Scored JSON with justifications
         ↓
Agent 3 — Coaching Generator
Generates: strengths with transcript citations,
improvements with actions, word-for-word objection
scripts, next call strategy → Coaching JSON
         ↓
Streamlit UI — 4 tabs + Databricks Dashboard
```

**The output of Agent 1 feeds Agent 2. The combined output feeds Agent 3.** This chaining produces coaching grounded in the specific call — not generic advice.

---

## 📊 Scoring Frameworks

**SPIN Selling** — industry standard at GSK, Pfizer, AstraZeneca
- **S**ituation — did the rep establish context and understand current practice?
- **P**roblem — did the rep uncover specific HCP pain points?
- **I**mplication — did the rep connect the problem to patient consequences?
- **N**eed-Payoff — did the rep link the solution to the HCP's specific need?

**FAB Objection Handling**
- **F**eature — stated the relevant product feature
- **A**dvantage — explained why that feature matters
- **B**enefit — connected it to a patient or practice benefit

**Compliance Check**
- Off-label claim detection
- Clinical data substantiation verification
- Approved indication adherence

---

## 🗄️ Databricks Integration

Every analyzed call is automatically saved to a **Delta Table** in Databricks, enabling:

- **Rep leaderboard** — average SPIN score ranked across the team
- **Outcome distribution** — positive vs neutral vs negative calls
- **Objection frequency** — most common objection types across the territory
- **Compliance alerts** — automatic flagging of calls scoring below 7/10 on compliance
- **Call history table** — all analyzed calls with scores

The Team Dashboard tab pulls live from Databricks on every page load — no manual exports needed.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Orchestration | LangChain LCEL | Chains prompt → LLM for each agent |
| LLM | Groq (Llama 3.3 70B) | Powers all 3 agents, temperature=0 |
| Data Layer | Databricks Delta Tables | Persistent call results storage |
| UI | Streamlit | 4-tab interface with coaching cards |
| Output Format | JSON | Structured, CRM-ready output |
| Language | Python | Core application |
| Visualization | Plotly | Interactive dashboard charts |

---

## 📁 Project Structure

```
pharmacoach/
├── app.py                      ← Streamlit UI — 4 tabs + team dashboard
├── agents.py                   ← 3 agent functions + full pipeline
├── prompts.py                  ← Extraction, scoring, coaching prompts
├── databricks_connector.py     ← Databricks connection, save, fetch
├── sample_data/
│   ├── sample_transcript.txt   ← Sarah Mitchell — Strong call (9/10)
│   ├── transcript_2.txt        ← James Okafor — Compliance issue (4/10)
│   ├── transcript_3.txt        ← Aisha Patel — Neutral call (7/10)
│   └── transcript_4.txt        ← Sarah Mitchell — Closing call (9/10)
├── requirements.txt
├── .env                        ← API keys (not committed)
└── .gitignore
```

---

## 🧠 Code Walkthrough

### `prompts.py`
Three prompt templates using LangChain's PromptTemplate. Each instructs the LLM to return ONLY valid JSON with a specific schema — enabling reliable agent chaining. The scoring prompt encodes SPIN selling and FAB frameworks as domain-specific evaluation criteria.

### `agents.py`
Three functions using LangChain LCEL (`prompt | llm`) pattern. Each includes robust JSON parsing with fallback strategies for common LLM formatting errors and retry logic for transient failures. `run_full_pipeline()` chains all three and returns a tuple of (call_data, scores, coaching).

### `databricks_connector.py`
Connects to Databricks SQL Warehouse using `databricks-sql-connector`. `save_call_result()` inserts structured scores into the `pharma_coach.call_results` Delta Table after every analysis. `get_team_data()` fetches all historical results for the dashboard.

### `app.py`
Streamlit app with four tabs. Session state persists analysis results across re-renders. Clear button removes only the current analysis — the team dashboard remains visible. Demo transcripts available via sidebar dropdown covering strong, weak, compliant, and non-compliant call scenarios.

---

## 💬 Demo Scenarios

| Sample | Rep | Score | Key Feature Demonstrated |
|--------|-----|-------|------------------------|
| Strong Call | Sarah Mitchell | 9/10 | High SPIN scores, effective FAB, clear next steps |
| Compliance Issue | James Okafor | 4/10 | Off-label claim detection, compliance alert triggered |
| Neutral Call | Aisha Patel | 7/10 | Good data usage, no commitment secured |
| Closing Call | Sarah Mitchell | 9/10 | Patient segmentation, hub services, commitment achieved |

---

## 🗺️ Roadmap

**Batch Processing**
CSV upload with multiple transcripts — process entire team automatically and output downloadable coaching report ranked by score.

**Veeva CRM Integration**
Pull transcripts directly from Veeva via API. Push scores and next steps back to HCP record automatically. Zero manual data entry.

**Scheduled Automation**
Nightly pipeline pulls all calls from previous day, runs all three agents, emails each rep their coaching feedback and manager a team summary by 8am.

**Approved Messaging Compliance**
Cross-reference clinical claims against MLR-approved messaging library to flag deviations from approved content.

**Territory Intelligence**
Enrich coaching with HCP segment data — tier, past engagement, prescribing behavior — so advice is personalized to the specific HCP relationship.

