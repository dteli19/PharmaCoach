# 💊 PharmaCoach — AI Sales Call Intelligence

An AI-powered pharma sales call analyzer that uses **3 specialized LangChain agents** to automatically extract structured call data, score against SPIN selling and FAB objection handling frameworks, and generate personalized coaching feedback — in seconds.

🚀 **[Live Demo](https://pharmacoach-yvbdgmwqnxsuz8jiagbox3.streamlit.app/)**

---

## 🎯 Business Problem

Pharma sales managers spend 30-45 minutes per rep manually reviewing call recordings and writing coaching notes. With teams of 20-50 reps each making 5-8 calls per day, this is operationally impossible at scale. Most reps receive coaching once a month at best — too infrequent to change behavior.

PharmaCoach compresses the post-call coaching cycle from days to seconds, enabling:
- **Immediate feedback** after every call
- **Consistent scoring** across all reps on the same framework
- **Structured output** that feeds directly into CRM systems like Veeva
- **Manager time savings** of an estimated 80% on routine call reviews

---

## 🤖 Why 3 Agents Instead of 1 Prompt

A single ChatGPT prompt produces free-form text. PharmaCoach uses three specialized agents in sequence — each optimized for one task — producing structured, parseable JSON at every step.

```
Raw Transcript
      ↓
Agent 1 — Call Extractor
Extracts: HCP info, objections (typed), clinical claims,
rep behaviors, outcome, next steps → structured JSON
      ↓
Agent 2 — Call Scorer  
Scores: SPIN selling (4 dimensions), FAB objection handling,
compliance check → scored JSON with justifications
      ↓
Agent 3 — Coaching Generator
Generates: strengths with examples, improvements with actions,
word-for-word objection scripts, next call strategy → coaching JSON
      ↓
Streamlit UI renders all three outputs in tabbed interface
```

The output of Agent 1 feeds Agent 2. The combined output of both feeds Agent 3. This chaining produces coaching that is grounded in the specific call data — not generic advice.

---

## 📊 Scoring Frameworks

**SPIN Selling** (industry standard at GSK, Pfizer, AstraZeneca)
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

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Orchestration | LangChain LCEL | Chains prompt → LLM for each agent |
| LLM | Groq (Llama 3.3 70B) | Powers all 3 agents, temperature=0 |
| UI | Streamlit | Tabbed interface with coaching cards |
| Output Format | JSON | Structured, CRM-ready output |
| Language | Python | Core application |

---

## 📁 Project Structure

```
pharmacoach/
├── app.py                    ← Streamlit UI with 3 output tabs
├── agents.py                 ← 3 agent functions + full pipeline
├── prompts.py                ← Extraction, scoring, coaching prompts
├── sample_data/
│   └── sample_transcript.txt ← Demo: Cardivex sales call
├── requirements.txt
├── .env                      ← API keys (not committed)
└── .gitignore
```

---

## 🧠 Code Walkthrough

### `prompts.py`
Three prompt templates using LangChain's PromptTemplate. Each prompt instructs the LLM to return ONLY valid JSON with a specific schema. This structured output approach is what enables agent chaining — Agent 2 can reliably parse Agent 1's output because the schema is enforced.

### `agents.py`
Three functions using LangChain LCEL (`prompt | llm`) pattern. Each function includes robust JSON parsing with fallback strategies for common LLM formatting errors. The `run_full_pipeline()` function chains all three agents and returns a tuple of (call_data, scores, coaching).

### `app.py`
Streamlit app with session_state persistence so results survive re-renders. Three tabs display call summary, SPIN scores with color-coded cards, and coaching with color-differentiated strength/improvement/script cards.

---

## 🚀 Setup and Run

```bash
git clone https://github.com/dteli19/pharmacoach.git
cd pharmacoach
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```
GROQ_API_KEY=your_groq_key_here
```

Run:
```bash
streamlit run app.py
```

---

## 💬 Example Output

**Input:** Raw sales call transcript (rep + HCP dialogue)

**Agent 1 Output:** Structured JSON with HCP details, 2 typed objections, 3 clinical claims, 4 rep behaviors, positive outcome, next steps

**Agent 2 Output:** SPIN scores 8-9/10, FAB 9/10, Compliance 10/10, Overall 9/10 with justifications

**Agent 3 Output:** 3 strengths with transcript citations, 2 improvements with actions, word-for-word scripts for each objection, next call strategy

---

## 🗺️ Roadmap

**Batch Processing**
Accept CSV upload with multiple transcripts — process all reps automatically and output a downloadable coaching report ranked by score.

**Veeva CRM Integration**
Pull call transcripts directly from Veeva via API. Push coaching scores and next steps back to the HCP record automatically. Zero manual data entry for reps.

**Scheduled Automation**
Nightly pipeline pulls all calls from the previous day, runs all three agents, emails each rep their coaching feedback and manager a team summary by 8am.

**Approved Messaging Compliance**
Cross-reference clinical claims against MLR-approved messaging library to flag any claims that deviate from approved content — critical for regulatory compliance.

**Territory Intelligence**
Enrich coaching with HCP segment data (tier, past engagement, prescribing behavior) so coaching advice is personalized to the specific HCP relationship, not just the call.
