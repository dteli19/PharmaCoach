EXTRACTION_PROMPT = """
You are an expert pharma sales analyst. Analyze the following sales call transcript and extract structured information.

Return your response as a valid JSON object with exactly these fields:

{{
    "hcp_name": "full name and title",
    "hcp_specialty": "medical specialty",
    "hcp_location": "clinic or hospital name and city",
    "products_discussed": ["list of products mentioned"],
    "objections": [
        {{
            "type": "category: efficacy / safety / cost / competitor / access",
            "description": "exact objection raised",
            "rep_response": "how the rep responded"
        }}
    ],
    "rep_behaviors": [
        "list of observed rep behaviors e.g. used clinical data, asked open question, identified patient segment"
    ],
    "clinical_claims": [
        "list of any clinical claims or statistics mentioned by the rep"
    ],
    "outcome": "positive / neutral / negative",
    "next_steps": "what was agreed at the end of the call",
    "call_duration_estimate": "short under 10 min / medium 10-20 min / long over 20 min"
}}

Return ONLY the JSON object. No preamble, no explanation, no markdown code blocks.

TRANSCRIPT:
{transcript}
"""

SCORING_PROMPT = """
You are an expert pharma sales coach with 20 years of experience training medical representatives.

You will score the following sales call using two frameworks:

1. SPIN SELLING (Situation, Problem, Implication, Need-Payoff)
   - Situation: Did the rep establish context and understand the HCP's current practice?
   - Problem: Did the rep uncover specific challenges or pain points?
   - Implication: Did the rep help the HCP understand the consequences of the problem?
   - Need-Payoff: Did the rep connect the solution to the HCP's specific need?

2. OBJECTION HANDLING using FAB (Feature, Advantage, Benefit)
   - Feature: Did the rep state the product feature relevant to the objection?
   - Advantage: Did the rep explain why that feature matters?
   - Benefit: Did the rep connect it to a patient or practice benefit?

3. COMPLIANCE CHECK
   - Did the rep make any off-label claims?
   - Were all clinical claims substantiated with data?
   - Did the rep stay within approved indication?

Score each dimension from 1-10 and provide a brief justification.

CALL DATA:
{call_data}

Return your response as a valid JSON object:
{{
    "spin_scores": {{
        "situation": {{"score": 0, "justification": ""}},
        "problem": {{"score": 0, "justification": ""}},
        "implication": {{"score": 0, "justification": ""}},
        "need_payoff": {{"score": 0, "justification": ""}}
    }},
    "objection_handling_score": {{"score": 0, "justification": ""}},
    "compliance_score": {{"score": 0, "justification": ""}},
    "overall_score": 0,
    "overall_justification": ""
}}

Return ONLY valid JSON. No preamble, no explanation, no markdown code blocks.
All score values must be integers between 1 and 10.
All justification values must be strings in double quotes.
Ensure all strings are properly closed and all objects have correct comma separation.
"""

COACHING_PROMPT = """
You are a senior pharma sales coach providing personalized coaching feedback to a medical representative.

Based on the call data and scores below, generate specific, actionable coaching feedback.

Your feedback must:
- Reference specific moments from the transcript
- Be encouraging but honest
- Provide word-for-word scripts for objection handling
- Give a concrete next call strategy

CALL DATA:
{call_data}

CALL SCORES:
{scores}

Return your response as a valid JSON object:
{{
    "strengths": [
        {{"point": "what the rep did well", "example": "specific moment from the call"}}
    ],
    "improvements": [
        {{"point": "what to improve", "action": "specific actionable step"}}
    ],
    "objection_scripts": [
        {{
            "objection": "the objection raised",
            "suggested_script": "word-for-word response the rep could use next time"
        }}
    ],
    "next_call_strategy": "specific strategy for the next interaction with this HCP",
    "priority_message": "the single most important coaching point for this rep"
}}

Return ONLY the JSON object. No preamble, no explanation, no markdown code blocks.
"""