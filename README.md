# Sinan.AI - Interactive AI Portfolio 🧠✨

Ein Next-Gen Portfolio, das nicht nur statische Inhalte zeigt, sondern **lebt**. 
Diese Anwendung demonstriert moderne **AI Engineering Patterns** (RAG, Multimodalität) verpackt in einer High-Performance Frontend-Architektur.

![Tech Stack](https://img.shields.io/badge/Stack-Astro_|_FastAPI_|_Gemini_Pro-blue?style=for-the-badge)

## 🚀 Features

### 1. RAG Chatbot (Retrieval Augmented Generation)
* **Technologie:** LangChain, Google Gemini Flash Lite.
* **Funktion:** Der Chatbot hat Zugriff auf meinen vollständigen Lebenslauf (PDF). Er beantwortet Fragen zu Skills, Stationen und Erfahrung kontextbezogen.
* **Engineering:** Vektorisierung ist hier nicht nötig, da der Kontext dynamisch in den Prompt injiziert wird (In-Context Learning für hohe Präzision).

### 2. Multimodal UX Audit (Computer Vision)
* **Technologie:** Gemini Flash 1.5 (Vision Capability).
* **Funktion:** Nutzer können Screenshots hochladen. Die KI analysiert Design, UX und Barrierefreiheit und gibt Code-Verbesserungsvorschläge (Tailwind CSS).
* **Frontend:** Drag & Drop Interface mit Instant-Preview.

### 3. Modern UI/UX
* **Design:** Bento-Grid Layout, Glassmorphism, Responsive Design.
* **Performance:** Astro "Islands Architecture" für minimale Ladezeiten.

## 🛠️ Tech Stack

**Frontend:**
* **Framework:** [Astro](https://astro.build/) (für statische Performance & dynamische Inseln)
* **Styling:** Tailwind CSS
* **Logic:** TypeScript, Vanilla JS

**Backend:**
* **API:** Python FastAPI
* **AI Orchestration:** LangChain (Google GenAI Integration)
* **PDF Processing:** PyPDFLoader

## 📦 Installation & Setup

Voraussetzung: Python 3.10+ und Node.js 18+

1.  **Repository klonen**
    ```bash
    git clone [https://github.com/DEIN-USERNAME/sinan-ai.git](https://github.com/DEIN-USERNAME/sinan-ai.git)
    cd sinan-ai
    ```

2.  **Backend starten**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # .env Datei erstellen mit GOOGLE_API_KEY=...
    
    ./start.sh
    ```

3.  **Frontend starten** (in neuem Terminal)
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## 👨‍💻 Über mich

Ich bin **Sinan Uçar**, Diplom-Informatiker und erfahrener Software Engineer (15+ Jahre).
Mein Fokus liegt auf der Verbindung von solider Enterprise-Architektur mit modernen AI-Lösungen.