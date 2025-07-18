# backend.py

import pymysql.cursors
import streamlit as st
import requests
import json
import pandas as pd
import re
import extract_mysql 
import os

# ==== FUNGSI UTAMA ====

def text_to_sql(prompt):
    """
    Mengirimkan prompt ke model AI untuk diubah menjadi query SQL.
    """
    # PENTING: Cek apakah skema berhasil dimuat sebelum mengirim ke Ollama
    if not extract_mysql.tabel_info:
        return "❌ ERROR: Tidak dapat mengambil skema database. Pastikan database berjalan dan dapat diakses."

    relevant_tables = detect_relevant_tables(prompt, extract_mysql.tabel_info)
    schema_string = json.dumps(relevant_tables, indent=2)

    url = "http://ollama:11434/api/generate"
    
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
        "temperature": 0.0
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        sql_query = result.get("response", "").strip()
        
        # Membersihkan output dari markdown code block
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.split('\n\n')[0]
        if sql_query.endswith(';'):
            sql_query = sql_query[:-1]
            
        return sql_query.strip()
    except requests.exceptions.RequestException as e:
        return f"❌ Error: Tidak dapat terhubung ke Ollama. Pastikan layanan 'ollama' berjalan. Detail: {e}"
    except Exception as e:
        return f"❌ Error: Terjadi kesalahan saat memproses permintaan AI. Detail: {str(e)}"

def detect_relevant_tables(prompt, tabel_info):
    """Mendeteksi tabel yang relevan dari prompt pengguna."""
    relevant = {}
    prompt_lower = prompt.lower()
    for table, columns in tabel_info.items():
        if table.lower().replace("_", " ") in prompt_lower:
            relevant[table] = columns
    
    # Jika tidak ada tabel yang terdeteksi, kirim semua skema sebagai fallback
    if not relevant:
        return tabel_info
    return relevant

def execute_query(sql_query):
    """
    Mengeksekusi query SQL pada database dan mengembalikan hasilnya sebagai DataFrame.
    """
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "mysecretpassword")
        db_name = os.getenv("DB_NAME", "university")

        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     password=db_password,
                                     database=db_name,
                                     cursorclass=pymysql.cursors.DictCursor)
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
        connection.close()
        return df, None
    except Exception as e:
        return None, str(e)

# ==== TAMPILAN STREAMLIT ====

st.set_page_config(page_title="Text to SQL with Mistral", page_icon="🤖", layout="wide")

# --- SIDEBAR SKEMA DATABASE ---
st.sidebar.title("Database Schema")
if not extract_mysql.tabel_info:
    st.sidebar.error("Skema database gagal dimuat. Cek log terminal untuk detail.")
else:
    try:
        for table, columns in extract_mysql.tabel_info.items():
            st.sidebar.markdown(f"### {table}")
            st.sidebar.code(", ".join(columns.keys()), language="text")
    except Exception as e:
        st.sidebar.error(f"Gagal menampilkan skema: {e}")

# --- HALAMAN UTAMA APLIKASI ---
st.title("💬 Text to SQL Generator + Executor")
st.markdown("Ketik pertanyaan dalam bahasa alami (hanya bahasa Inggris), lihat SQL yang dihasilkan, dan jalankan secara langsung.")

question = st.text_area("Pertanyaan Anda:", height=150)

if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""

if st.button("🔍 Konversi ke SQL"):
    if question.strip() == "":
        st.warning("Silakan masukkan pertanyaan terlebih dahulu.")
    else:
        with st.spinner("Menghubungi model AI via Ollama..."):
            sql_result = text_to_sql(question)
        st.session_state.generated_sql = sql_result
        
if st.session_state.generated_sql:
    # Cek apakah hasilnya adalah pesan error
    if st.session_state.generated_sql.strip().startswith("❌"):
        st.error(st.session_state.generated_sql)
    else:
        st.code(st.session_state.generated_sql, language="sql")
        if st.button("Jalankan SQL"):
            with st.spinner("Mengeksekusi query..."):
                df, error = execute_query(st.session_state.generated_sql)
            if error:
                st.error(f"❌ Terjadi error saat eksekusi query: {error}")
            else:
                st.success("✅ Query berhasil dieksekusi!")
                st.dataframe(df)
