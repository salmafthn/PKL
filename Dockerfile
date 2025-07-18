FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/wait-for-db.sh

CMD ["/app/wait-for-db.sh", "db", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]