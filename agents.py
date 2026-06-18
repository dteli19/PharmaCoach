import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from prompts import EXTRACTION_PROMPT, SCORING_PROMPT, COACHING_PROMPT

load_dotenv()


def get_llm():
    groq_key = os.getenv("GROQ_API_KEY")
    try:
        import streamlit as st
        if not groq_key:
            groq_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    return ChatGroq(
        api_key=groq_key,
        model="llama-3.3-70b-versatile",
        temperature=0
    )


def clean_json(text: str) -> dict:
    """Remove markdown code blocks and fix common JSON issues."""
    text = text.strip()
    # Remove markdown code blocks
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Find the JSON object between first { and last }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last resort: use regex to extract valid JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    
    raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}")


def run_extraction_agent(transcript: str) -> dict:
    """
    Agent 1: Extract structured call data from raw transcript.
    Returns a dictionary with HCP info, objections, behaviors, outcome.
    """
    llm = get_llm()
    prompt = PromptTemplate.from_template(EXTRACTION_PROMPT)
    chain = prompt | llm
    result = chain.invoke({"transcript": transcript})
    return clean_json(result.content)


def run_scoring_agent(call_data: dict) -> dict:
    """
    Agent 2: Score the call against SPIN selling and FAB frameworks.
    Takes structured call data from Agent 1.
    Returns scores and justifications.
    """
    llm = get_llm()
    prompt = PromptTemplate.from_template(SCORING_PROMPT)
    chain = prompt | llm
    result = chain.invoke({"call_data": json.dumps(call_data, indent=2)})
    return clean_json(result.content)


def run_coaching_agent(call_data: dict, scores: dict) -> dict:
    """
    Agent 3: Generate personalized coaching feedback.
    Takes structured call data from Agent 1 and scores from Agent 2.
    Returns strengths, improvements, objection scripts, next call strategy.
    """
    llm = get_llm()
    prompt = PromptTemplate.from_template(COACHING_PROMPT)
    chain = prompt | llm
    result = chain.invoke({
        "call_data": json.dumps(call_data, indent=2),
        "scores": json.dumps(scores, indent=2)
    })
    return clean_json(result.content)


def run_full_pipeline(transcript: str) -> tuple:
    """
    Runs all three agents in sequence.
    Returns (call_data, scores, coaching) as a tuple of three dicts.
    """
    print("Running Agent 1 — Extracting call data...")
    call_data = run_extraction_agent(transcript)

    print("Running Agent 2 — Scoring call...")
    scores = run_scoring_agent(call_data)

    print("Running Agent 3 — Generating coaching...")
    coaching = run_coaching_agent(call_data, scores)

    return call_data, scores, coaching


if __name__ == '__main__':
    with open("sample_data/sample_transcript.txt", "r") as f:
        transcript = f.read()

    call_data, scores, coaching = run_full_pipeline(transcript)

    print("\n=== AGENT 1: CALL DATA ===")
    print(json.dumps(call_data, indent=2))

    print("\n=== AGENT 2: SCORES ===")
    print(json.dumps(scores, indent=2))

    print("\n=== AGENT 3: COACHING ===")
    print(json.dumps(coaching, indent=2))