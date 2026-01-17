# 1. Python Image nutzen
FROM python:3.9-slim

# 2. Arbeitsverzeichnis setzen
WORKDIR /app

# 3. System-Abhängigkeiten für PDF-Verarbeitung (falls nötig für langchain)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Restlichen Code kopieren
COPY . .

# 6. Port freigeben (Render nutzt oft PORT environment variable, Standard 8000)
EXPOSE 8000

# 7. Start-Befehl
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]