# backend.py

import pymysql.cursors
import streamlit as st
import requests
import json
import pandas as pd
import os
import extract_mysql  # Pastikan file ini ada dan sudah versi terbaru

# ==== FUNGSI UTAMA ====

def format_schema_with_values(schema_info):
    """
    Memformat skema dan contoh data menjadi string yang mudah dibaca oleh AI.
    """
    schema_str = ""
    values_str = ""
    
    # Format Skema
    for table, details in schema_info.items():
        columns = {k: v for k, v in details.items() if k != "_values"}
        schema_str += f"Table `{table}`:\n"
        schema_str += json.dumps(columns, indent=2) + "\n\n"
        
        # Format Contoh Data (Contekan)
        if "_values" in details:
            for col_name, val_list in details["_values"].items():
                if val_list: # Hanya tambahkan jika ada isinya
                    values_str += f"- `{table}.{col_name}`: {json.dumps(val_list)}\n"
    
    return schema_str, values_str

def text_to_sql(prompt):
    """
    Mengirimkan prompt ke model AI dengan konteks skema DAN contoh data.
    """
    if not extract_mysql.tabel_info:
        return "❌ ERROR: Tidak dapat mengambil skema database. Pastikan database berjalan dan dapat diakses."

    # Dapatkan skema dan contekan dalam format string
    schema_string, values_string = format_schema_with_values(extract_mysql.tabel_info)

    url = "http://ollama:11434/api/generate"
    
    # --- PROMPT BARU YANG LEBIH CERDAS ---
    full_prompt = f"""You are an expert SQL assistant who only returns valid MySQL queries.
Given the database schema below:

{schema_string}
For string comparisons, you MUST use one of the following exact values if the user's query is similar. This is very important for correctness.
Here are some example values for key columns:
{values_string}

Convert the following question into a valid, syntactically correct MySQL query.

IMPORTANT: 
- Your response must ONLY contain the SQL code.
- Do not provide any explanation or any text other than the SQL code itself.
- Do not use quotes around column names, but always use single quotes for string values (e.g., WHERE dept_name = 'Comp. Sci.').

Question:
{prompt}

SQL:
"""
    
    data = {
        "model": "mistral",
        "prompt": full_prompt,
        "stream": False,
        "temperature": 0.0
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        sql_query = result.get("response", "").strip()
        
        # Membersihkan output dari markdown
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        
        return sql_query
        
    except requests.exceptions.RequestException as e:
        return f"❌ Error: Tidak dapat terhubung ke Ollama. Pastikan layanan 'ollama' berjalan. Detail: {e}"
    except Exception as e:
        return f"❌ Error: Terjadi kesalahan saat memproses permintaan AI. Detail: {str(e)}"

def execute_query(sql_query):
    # (Fungsi ini tidak perlu diubah, sudah benar)
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "mysecretpassword")
        db_name = os.getenv("DB_NAME", "university")

        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name, cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
        connection.close()
        return df, None
    except Exception as e:
        return None, str(e)

# ==== TAMPILAN STREAMLIT ====
# (Bagian UI ini tidak perlu diubah, sudah benar)
st.set_page_config(page_title="Text to SQL with Mistral", page_icon="🤖", layout="wide")

st.sidebar.title("Database Schema")
if not extract_mysql.tabel_info:
    st.sidebar.error("Skema database gagal dimuat. Cek log terminal untuk detail.")
else:
    schema_string, _ = format_schema_with_values(extract_mysql.tabel_info)
    st.sidebar.code(schema_string, language="json")

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

