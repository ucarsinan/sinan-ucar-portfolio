# sinan-ucar-portfolio – CLAUDE.md

## Was ist das?
Sinans persönliches KI-Portfolio-Backend. Läuft unter `sinanucar.com`.
FastAPI-Backend (4 Endpunkte) + Astro-Frontend (Showcase) — kein Produktivcode für die RealizeTogether-Plattform.

---

## Stack

```
Backend:    FastAPI + Python 3.12 · LangChain (langchain-core, -google-genai, -openai, -groq, -anthropic)
Validation: Pydantic BaseModel + with_structured_output()
Frontend:   Astro.js (frontend/ — separates Deployment)
Deploy:     Backend → Render (sinan-ucar-portfolio.onrender.com)
Dev-Env:    Google Firebase Studio (.idx/dev.nix)
Monitoring: Sentry (SENTRY_DSN via .env)
```

---

## Commands

```bash
# Backend starten (aus backend/)
source .venv/bin/activate
bash start.sh               # oder: uvicorn main:app --reload --port 8000

# Dependencies
pip install -r requirements.txt

# Modelle testen
python check_models.py
```

---

## Architektur: Multi-Provider Fallback

`invoke_resiliently()` probiert Modelle der Reihe nach:
1. `google:gemini-flash-latest`
2. `google:gemini-2.0-flash`
3. `openai:gpt-4o-mini`
4. `groq:llama-3.3-70b-versatile`

Fällt bei Quota-Error / Timeout sofort auf das nächste durch.

---

## Endpunkte (Router)

| Endpunkt | Aufgabe | Key File |
|---|---|---|
| `POST /api/chat` | CV-Assistent (Kontext: `data/cv.md`) | `main.py` |
| `POST /api/vision` | UX-Screenshot-Analyse → `VisionAnalysis` | `main.py` |
| `POST /api/analyze` | Sentiment-Analyse → `SentimentAnalysis` | `main.py` |
| `POST /api/agent` | Agent mit Tools (calculator, web_search, etc.) | `main.py` |

---

## Coding-Regeln

- **Structured Output:** immer `llm.with_structured_output(PydanticModel)` — kein manuelles JSON-Parsing
- **Fehler:** LLM-Calls in try/except, Fallback aktiv nutzen — kein silent catch ohne Logging
- **Agent:** manueller Tool-Loop (kein LangGraph) — so lassen, solange es reicht
- **CORS:** Allowlist in `main.py` pflegen — kein wildcard `*`
- **Secrets:** nur via `.env` + `python-dotenv` — nie hardcoden
- **Uploads:** max 4 MB, nur JPEG/PNG/WebP/GIF — Typ-Check vor Verarbeitung
