#!/bin/bash

# 1. Sicherstellen, dass wir im richtigen Ordner sind
# (Das `dirname "$0"` sorgt dafür, dass es egal ist, von wo du das Skript aufrufst)
cd "$(dirname "$0")"

# 2. Umgebung aktivieren (WICHTIG: .venv mit Punkt!)
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  Keine virtuelle Umgebung (.venv) gefunden!"
    exit 1
fi

# 3. Server starten
echo "🚀 Starte Sinan.AI Backend..."
# --reload sorgt dafür, dass der Server neu startet, wenn du Code änderst!
uvicorn main:app --reload --port 8000 --host 0.0.0.0