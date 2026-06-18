import os
from databricks import sql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    try:
        import streamlit as st
        host = st.secrets.get("DATABRICKS_HOST") or os.getenv("DATABRICKS_HOST")
        http_path = st.secrets.get("DATABRICKS_HTTP_PATH") or os.getenv("DATABRICKS_HTTP_PATH")
        token = st.secrets.get("DATABRICKS_TOKEN") or os.getenv("DATABRICKS_TOKEN")
    except Exception:
        host = os.getenv("DATABRICKS_HOST")
        http_path = os.getenv("DATABRICKS_HTTP_PATH")
        token = os.getenv("DATABRICKS_TOKEN")

    connection = sql.connect(
        server_hostname=host,
        http_path=http_path,
        access_token=token
    )
    return connection


def run_query(query: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    connection.close()
    return columns, result


def setup_table():
    """Create the coaching results table if it doesn't exist."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pharma_coach.call_results (
            id BIGINT GENERATED ALWAYS AS IDENTITY,
            rep_name STRING,
            hcp_name STRING,
            hcp_specialty STRING,
            call_date STRING,
            overall_score INT,
            spin_situation INT,
            spin_problem INT,
            spin_implication INT,
            spin_need_payoff INT,
            objection_handling_score INT,
            compliance_score INT,
            outcome STRING,
            objection_types STRING,
            priority_coaching STRING,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.close()
    connection.close()


def save_call_result(rep_name, call_data, scores, coaching):
    """Save analysis results to Databricks Delta Table."""
    objection_types = ", ".join([
        obj.get("type", "") for obj in call_data.get("objections", [])
    ])
    spin = scores.get("spin_scores", {})

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO pharma_coach.call_results
        (rep_name, hcp_name, hcp_specialty, call_date, overall_score,
         spin_situation, spin_problem, spin_implication, spin_need_payoff,
         objection_handling_score, compliance_score, outcome,
         objection_types, priority_coaching)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        rep_name,
        call_data.get("hcp_name", "Unknown"),
        call_data.get("hcp_specialty", "Unknown"),
        call_data.get("call_date", "Unknown"),
        scores.get("overall_score", 0),
        spin.get("situation", {}).get("score", 0),
        spin.get("problem", {}).get("score", 0),
        spin.get("implication", {}).get("score", 0),
        spin.get("need_payoff", {}).get("score", 0),
        scores.get("objection_handling_score", {}).get("score", 0),
        scores.get("compliance_score", {}).get("score", 0),
        call_data.get("outcome", "neutral"),
        objection_types,
        coaching.get("priority_message", "")
    ])
    cursor.close()
    connection.close()


def get_team_data():
    """Fetch all call results for the dashboard."""
    try:
        columns, rows = run_query("""
            SELECT rep_name, hcp_name, hcp_specialty, call_date,
                   overall_score, spin_situation, spin_problem,
                   spin_implication, spin_need_payoff,
                   objection_handling_score, compliance_score,
                   outcome, objection_types, priority_coaching,
                   analyzed_at
            FROM pharma_coach.call_results
            ORDER BY analyzed_at DESC
        """)
        return columns, rows
    except Exception:
        return None, None
        