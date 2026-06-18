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
        temperature=0,
        max_tokens=1024
    )


def clean_json(text: str) -> dict:
    """Remove markdown code blocks and fix common JSON issues from LLM."""
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
    
    # Extract JSON between first { and last }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Fix common LLM JSON errors
    # Remove trailing commas before } or ]
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    
    # Fix unquoted numeric values in nested objects
    text = re.sub(r':\s*(\d+)\s*,', r': \1,', text)
    text = re.sub(r':\s*(\d+)\s*}', r': \1}', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Last resort — use regex to find largest JSON object
    matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if matches:
        largest = max(matches, key=len)
        try:
            return json.loads(largest)
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Could not parse JSON: {text[:300]}")



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
    Includes retry logic for JSON parsing failures.
    """
    llm = get_llm()
    prompt = PromptTemplate.from_template(SCORING_PROMPT)
    chain = prompt | llm
    
    for attempt in range(3):
        try:
            result = chain.invoke({"call_data": json.dumps(call_data, indent=2)})
            return clean_json(result.content)
        except (ValueError, Exception) as e:
            if attempt == 2:
                raise ValueError(f"Agent 2 failed after 3 attempts: {str(e)}")
            print(f"Agent 2 attempt {attempt+1} failed, retrying...")


def run_coaching_agent(call_data: dict, scores: dict) -> dict:
    """
    Agent 3: Generate personalized coaching feedback.
    Uses higher max_tokens to handle longer coaching responses.
    """
    groq_key = os.getenv("GROQ_API_KEY")
    try:
        import streamlit as st
        if not groq_key:
            groq_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

    llm = ChatGroq(
        api_key=groq_key,
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=2048
    )

    prompt = PromptTemplate.from_template(COACHING_PROMPT)
    chain = prompt | llm

    for attempt in range(3):
        try:
            result = chain.invoke({
                "call_data": json.dumps(call_data, indent=2),
                "scores": json.dumps(scores, indent=2)
            })
            return clean_json(result.content)
        except (ValueError, Exception) as e:
            if attempt == 2:
                raise ValueError(f"Agent 3 failed after 3 attempts: {str(e)}")
            print(f"Agent 3 attempt {attempt+1} failed, retrying...")


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