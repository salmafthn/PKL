# Dockerfile (Versi Final dengan Wait Script)

FROM python:3.9-slim

# Tetapkan direktori kerja
WORKDIR /app

# Langkah 1: Instalasi dependensi sistem (MySQL Client)
# Ini diperlukan agar kita bisa menggunakan perintah 'mysqladmin' di wait-for-db.sh
RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*

# Langkah 2: Salin dan instal dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Langkah 3: Salin semua file proyek
COPY . .

# Langkah 4: Jadikan wait-for-db.sh dapat dieksekusi
RUN chmod +x /app/wait-for-db.sh

# Langkah 5: Jalankan aplikasi menggunakan wait script
# Script ini akan menunggu 'db' siap sebelum menjalankan perintah streamlit
CMD ["/app/wait-for-db.sh", "db", "streamlit", "run", "backend.py", "--server.port=8501", "--server.address=0.0.0.0"]