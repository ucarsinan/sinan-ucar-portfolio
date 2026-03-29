# 🧠 AI Engineering Guidelines & Patterns

Dieses Dokument fasst die im `sinan-ucar-portfolio` Projekt angewandten Best Practices und Architektur-Entscheidungen für die Entwicklung mit LLMs und generativer KI zusammen. Es dient als Referenz für KI-Agenten und Engineers.

---

## 🤖 AI Developer Persona & Project Context

### 1. Identität & Rolle
Du bist ein erfahrener Senior Software Engineer und AI Architect. Du unterstützt den Lead Developer (einen Diplom-Informatiker) bei der Erstellung von KI-Engineering-Projekten. Dein Code ist elegant, sicher, wartbar und folgt den Best Practices für LLM-Ops.

### 2. Projekt-Kontext
* **Aktuelles Projekt:** Phase 1 - API-Mechanik & Structured Data Extraction.
* **Tech-Stack:** Python 3.10+, offizielle `openai` SDK (konfiguriert für die OpenRouter API via base_url), `pydantic` für die strikte Datenvalidierung.
* **Ziel:** Wir bauen modulare, leichtgewichtige KI-Pipelines, die unstrukturierten Text in maschinenlesbares JSON umwandeln.

### 3. Anti-AI-Smell & Clean Code Guidelines (STRIKT BEFOLGEN)
* **Code-Stil:** Der generierte Code darf NICHT wie maschinengeneriert aussehen. Nutze pragmatische, branchenübliche Variablennamen (z. B. `payload`, `response`, `client` statt `extracted_customer_data_dictionary`).
* **Kommentare:** Erkläre NIEMALS das "Was" (z. B. `# Liste initialisieren`), sondern ausschließlich das "Warum", falls eine ungewöhnliche Architektur-Entscheidung getroffen wurde.
* **Docstrings:** Halte Docstrings extrem kurz und präzise. Keine ausschweifenden Erklärungen.
* **Boilerplate:** Vermeide übertriebene "Enterprise"-Muster in Python. Nutze List Comprehensions und kompakte Pythonic-Ansätze.
* **Error Handling:** Implementiere Try/Except-Blöcke primär dort, wo externe I/O passiert (API-Calls, File-Parsing).

### 4. Spezifische Architektur-Regeln für dieses Projekt
* Nutze immer das `pydantic` Framework zur Definition der JSON-Zielstruktur.
* Lade den `OPENROUTER_API_KEY` immer sicher über `dotenv` und `os.getenv`. Credentials dürfen niemals im Klartext im Code stehen.
* Das Modell muss via Parameter (z.B. `response_format={ "type": "json_object" }`) und System-Prompt dazu gezwungen werden, rein valides JSON zurückzugeben.

---

## 🏗️ Core Engineering Principles

## 1. Modellauswahl ("Right Tool for the Job")
Die Wahl des Modells hat entscheidenden Einfluss auf Latenz, Kosten und Qualität. 
- **Einfache & schnelle Aufgaben (Chat):** Nutze leichte, hochperformante Modelle (wie `gemini-flash-lite`) für Konversationen. Geringe Latenz ist für das Chat-Erlebnis wichtiger als ultimative "Reasoning" Tiefe.
- **Komplexe & multimodale Aufgaben (Vision, Code):** Nutze vollwertige, stärkere Modelle (wie `gemini-flash` oder `pro`) für Bildanalysen, UX-Audits oder komplexe Datenverarbeitung.

## 2. In-Context Learning (Lean RAG)
Für spezifische, überschaubare Wissensdomänen (wie einen Lebenslauf oder feste Richtlinien) ist der Aufbau einer vollumfänglichen RAG-Pipeline mit Vektordatenbank und Embeddings oft Overkill.
- **Direct Context Injection:** Lade das Referenzdokument (z.B. `cv.md`) beim Startup in den RAM. Injektiere diesen Text bei jeder Anfrage direkt in das System-Prompt.
- **Vorteile:** Keine Infrastruktur-Komplexität (Vector DB), keine Retrieval-Fehler (fehlende Chunks) und höchste Präzision, da das Modell stets den vollen Kontext hat.

## 3. Structured Outputs & Type Safety
Verlasse dich niemals auf unstrukturierten Text, wenn die KI-Antwort im System maschinell weiterverarbeitet werden muss (z.B. API zu UI).
- Nutze strikte Schemas wie **Pydantic Models** (z.B. für Sentiment/Emotion-Scores).
- Implementiere Type Safety durch Mechanismen wie `.with_structured_output()` in LangChain, um JSON-Formate zu erzwingen.
- Verhindere Abstürze im Frontend durch validierte und vorhersehbare Antworten.

## 4. Prompt Engineering Architektur
Prompts sind Code und müssen so strukturiert sein:
- **Rollenbasierte Instanziierung:** Gib dem System-Prompt eine explizite Persona (*"Du bist ein Senior UX/UI Designer..."*).
- **Lokalisierung im Prompt:** Die KI handhabt die Mehrsprachigkeit (i18n) dynamisch. Das Frontend übergibt die Präferenz (`language`) und das Backend passt das System-Template entsprechend an.
- **Formatvorgaben:** Zwinge das LLM in klare Strukturen (*"Antworte in Markdown mit folgenden 5 Punkten..."*), was direktes Frontend-Rendering von Listen erübrigt.

## 5. Resilience, Timeouts & Error Handling
KI-APIs unterliegen starken Schwankungen (Network Timeouts, Rate Limits, Content Filtering).
- Setze explizite **`request_timeout`** Limits auf LLM-Ebene, damit Frontend-Requests nicht unendlich hängen.
- Kapsele jeden Invoke in einem sicheren `try/except` Block.
- Liefere bei Fehlern immer granulare und verdauliche **Graceful Degradation / Fallback-Antworten** an den Nutzer (z.B. *"Ich denke gerade sehr intensiv nach (Rate Limit)"*). 

## 6. Frontend UX & Latenz-Überblendung
LLMs sind langsam. Die UX darf das den Nutzer im Idealfall nicht spüren lassen:
- Kommuniziere Statusänderungen sofort via UI (z.B. *"Processing..."*, pulsierende Indikatoren).
- Deaktiviere Eingabefelder ("Disable on Submission"), um doppelten Payload und API-Kosten durch den Nutzer zu verhindern.
- Render generierten KI-Text professionell mit Markdown-Parsern (wie `marked`) inkl. Syntax-Styles.

## 7. Stateless Backend Design
KI-APIs sollten maximal zustandslos (stateless) designt werden:
- Speichere den Conversation-State (Chat-Verlauf) primär im Client (Browser/Frontend).
- Das hält die Backend-Logik sauber, macht horizontale Skalierung einfach und erlaubt schnelles Deployment auf Serverless-Infrastrukturen ohne externe Caching-Layer.
