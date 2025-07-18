from sqlalchemy import create_engine, inspect, text
import os

# konfigurasi koneksi DB
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")
DB_NAME = os.getenv("DB_NAME", "university")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"

CONTEKAN_KOLOM = {
    'department': ['dept_name', 'building'],
    'course': ['title'],
    'instructor': ['name'],
    'student': ['name']
}

def get_schema_and_values():
    """
    Mengambil skema database DAN beberapa contoh nilai unik dari kolom-kolom penting
    untuk diberikan sebagai konteks tambahan ke model AI.
    """
    tabel_info = {}
    try:
        print("Mencoba mengambil skema dan contoh data...")
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        with engine.connect() as connection:
            tables = inspector.get_table_names()

            if not tables:
                print("Koneksi berhasil, tetapi tidak ada tabel yang ditemukan.")
                return {}

            for table_name in tables:
                columns = inspector.get_columns(table_name)
                tabel_info[table_name] = {col["name"]: str(col["type"]) for col in columns}
                
                if table_name in CONTEKAN_KOLOM:
                    tabel_info[table_name]["_values"] = {}
                    for col_name in CONTEKAN_KOLOM[table_name]:
                        query = text(f"SELECT DISTINCT `{col_name}` FROM `{table_name}` LIMIT 10;")
                        result = connection.execute(query)
                        values = [row[0] for row in result]
                        tabel_info[table_name]["_values"][col_name] = values
            
            print(f"✅ Skema dan contekan berhasil dimuat untuk tabel: {list(tabel_info.keys())}")
            return tabel_info

    except Exception as e:
        print(f"❌ CRITICAL: GAGAL MENGAMBIL SKEMA. Error: {e}")
        return {}

tabel_info = get_schema_and_values()

