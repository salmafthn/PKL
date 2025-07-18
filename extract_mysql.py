# extract_mysql.py (Versi Sederhana Final)

from sqlalchemy import create_engine, inspect
import os

# Ambil kredensial dari environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")
DB_NAME = os.getenv("DB_NAME", "university")

# Buat connection string
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"

tabel_info = {}
try:
    print("Mencoba mengambil skema database...")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if not tables:
        print("Koneksi berhasil, tetapi tidak ada tabel yang ditemukan di database.")
    else:
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            tabel_info[table_name] = {col["name"]: str(col["type"]) for col in columns}
        print(f"✅ Skema berhasil dimuat untuk tabel: {list(tabel_info.keys())}")

except Exception as e:
    print(f"❌ CRITICAL: GAGAL MENGAMBIL SKEMA. Error: {e}")