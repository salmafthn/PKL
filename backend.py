import pymysql.cursors
import streamlit as st
import requests
import json
import pandas as pd
import re
import extract_mysql 

# ==== FUNGSI UTAMA ====

def text_to_sql(prompt):
    """
    Sends a prompt to the AI model to be converted into a SQL query.
    The prompt is optimized for English and clean output.
    """
    relevant_tables = detect_relevant_tables(prompt, extract_mysql.tabel_info)
    schema_string = json.dumps(relevant_tables, indent=2)

    url = "http://localhost:11434/api/generate"
    
    # --- PROMPT DIKEMBALIKAN KE BAHASA INGGRIS ---
    data = {
        "model": "mistral",
        "prompt": f"""
        You are an expert SQL assistant who only returns valid MySQL queries.
        Given the database schema below:

        {schema_string}

        Convert the following question into a valid, syntactically correct MySQL query.

        IMPORTANT: Do not provide any explanation or any text other than the SQL code itself. Your response must ONLY contain the SQL code. Do not use quotes around column names.

        Question:
        {prompt}

        SQL:
        """,
        "stream": False,
        "temperature": 0.0 # Temperature 0 for deterministic output
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        # Output cleaning code
        sql_query = result.get("response", "").strip()
        
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
            
        sql_query = sql_query.split('\n\n')[0]

        if sql_query.endswith(';'):
            sql_query = sql_query[:-1]

        return sql_query.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

def detect_relevant_tables(prompt, tabel_info):
    """Detects relevant tables from the user's prompt."""
    relevant = {}
    prompt_lower = prompt.lower()
    for table, columns in tabel_info.items():
        if table.lower() in prompt_lower:
            relevant[table] = columns
        else:
            for col in columns.keys():
                if col.lower() in prompt_lower:
                    relevant[table] = columns
                    break
    return relevant

def run_sql(sql):
    """Executes the SQL query against the University database."""
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="2701", # Your MySQL password
            database="university",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return pd.DataFrame(results)
    except Exception as e:
        return f"❌ Query Execution Error: {str(e)}"

# ==== STREAMLIT USER INTERFACE (UI) ====

st.set_page_config(page_title="Text to SQL with Mistral", page_icon="🤖", layout="wide")

# --- DATABASE SCHEMA SIDEBAR ---
st.sidebar.title("Database Schema")
try:
    for table, columns in extract_mysql.tabel_info.items():
        st.sidebar.markdown(f"### {table}")
        st.sidebar.code(", ".join(columns.keys()), language="text")
except Exception as e:
    st.sidebar.error(f"Failed to load schema: {e}")

# --- MAIN APPLICATION PAGE ---
st.title("💬 Text to SQL Generator + Executor")
st.markdown("Type a question in natural language (english only), see the generated SQL, and run it directly.")

question = st.text_area("Your Question:", height=150)

if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""

if st.button("🔍 Convert to SQL"):
    if question.strip() == "":
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Contacting AI model via Ollama..."):
            sql_result = text_to_sql(question)
        st.session_state.generated_sql = sql_result
        
if st.session_state.generated_sql:
    st.code(st.session_state.generated_sql, language="sql")
    if st.button("Execute SQL"):
        with st.spinner("Executing query..."):
            result = run_sql(st.session_state.generated_sql)
            if isinstance(result, pd.DataFrame):
                st.success("✅ Query executed successfully!")
                st.dataframe(result)
            else:
                st.error(result)