from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import base64

# 1. Setup
load_dotenv()
app = FastAPI()

origins = [
    "http://localhost:4321",                      # Für lokale Entwicklung
    "http://localhost:3000",                      # Falls Astro manchmal auf 3000 läuft
    "https://sinan.realizetogether.com",          # DEINE LIVE DOMAIN (Wichtig!)
    "https://sinan-backend.onrender.com"          # Das Backend selbst
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Statt ["*"] nehmen wir die Liste
    allow_credentials=True,     # Das darf bleiben, weil wir oben exakte Domains haben
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Globale Variable für das "Gehirn" (Lebenslauf)
CV_CONTEXT = ""

def load_cv():
    """Liest das PDF aus dem data-Ordner ein."""
    global CV_CONTEXT
    file_path = os.path.join("data", "cv.pdf")

    try:
        if not os.path.exists(file_path):
            print(f"⚠️ WARNUNG: Datei unter '{file_path}' nicht gefunden!")
            CV_CONTEXT = "Kein Lebenslauf hinterlegt."
            return

        print(f"📂 Lade Lebenslauf von: {file_path} ...")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        CV_CONTEXT = "\n".join([p.page_content for p in pages])
        print(f"✅ Lebenslauf geladen! ({len(CV_CONTEXT)} Zeichen)")
        
    except Exception as e:
        print(f"❌ Fehler beim Laden des PDFs: {e}")
        CV_CONTEXT = "Fehler beim Laden des Lebenslaufs."

# Beim Starten einmal ausführen
load_cv()

# 4. AI Setup
api_key = os.getenv("GOOGLE_API_KEY")

# Modell für den Chat (Dein funktionierendes Modell)
chat_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
    google_api_key=api_key,
    max_retries=0,       
    request_timeout=10.0
)

# Modell für Vision (Dein funktionierendes Modell)
vision_llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=api_key,
    max_retries=0,
    request_timeout=20.0 
)

# --- ÄNDERUNG 1: Sprach-Feld hinzugefügt ---
class ChatRequest(BaseModel):
    message: str
    language: str = "de"  # Standard ist Deutsch

# 6. Endpunkt: CHAT
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"📩 Frage: {request.message} | Sprache: {request.language}")
    
    # --- ÄNDERUNG 2: Prompt auswählen basierend auf Sprache ---
    if request.language == "en":
        # Englischer Prompt
        prompt_template = ChatPromptTemplate.from_template("""
        You are the professional AI assistant for Sinan. 
        Use the following resume to answer questions:

        RESUME DATA:
        {cv_text}

        RULES:
        - Answer in ENGLISH.
        - Keep it short, professional, and helpful.
        - If the info is not in the resume, say honestly that you don't know.
        - Speak as an assistant ("Sinan has...", "He has...").

        USER QUESTION: 
        {user_message}
        """)
    else:
        # Deutscher Prompt (Dein Original)
        prompt_template = ChatPromptTemplate.from_template("""
        Du bist der professionelle AI-Assistent von Sinan. 
        Nutze den folgenden Lebenslauf, um Fragen zu beantworten:

        LEBENSLAUF DATEN:
        {cv_text}

        REGELN:
        - Antworte kurz, professionell und hilfreich.
        - Wenn die Info nicht im Lebenslauf steht, sag ehrlich, dass du es nicht weißt.
        - Du sprichst als Assistent ("Sinan hat...", "Er hat...").

        FRAGE DES USERS: 
        {user_message}
        """)

    # Kette bilden mit dem gewählten Prompt
    chain = prompt_template | chat_llm
    
    try:
        response = chain.invoke({
            "cv_text": CV_CONTEXT,
            "user_message": request.message
        })
        return {"reply": response.content}
        
    except Exception as e:
        error_str = str(e).lower()
        print(f"❌ Fehler: {error_str}") 
        
        if "429" in error_str or "resource_exhausted" in error_str or "timeout" in error_str or "deadline" in error_str:
            return {"reply": "⚠️ **Kurze Pause!**\nIch habe gerade zu viele Anfragen erhalten oder Google antwortet zu langsam. Bitte warte 30 Sekunden. ⏳"}
        
        return {"reply": f"Ein technisches Problem ist aufgetreten: {str(e)}"}

# 7. Endpunkt: VISION (Bilderanalyse)
@app.post("/api/vision")
async def vision_endpoint(file: UploadFile = File(...)):
    print(f"🖼️ Bild empfangen: {file.filename}")
    
    try:
        # 1. Bild einlesen und kodieren
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode("utf-8")
        
        # 2. Multimodaler Prompt
        message = HumanMessage(
            content=[
                {"type": "text", "text": """
Du bist ein Senior UX/UI Designer und Frontend-Experte. Analysiere diesen Screenshot. 

Erstelle eine Analyse im Markdown-Format:
1. **Erster Eindruck:** Was fällt sofort auf? (Positiv/Negativ)
2. **UX & Usability:** Sind Buttons erkennbar? Ist die Navigation logisch?
3. **Design & Ästhetik:** Farbwahl, Whitespace, Typografie.
4. **Verbesserungsvorschläge:** 3 konkrete Punkte für bessere Conversion oder User Experience.
5. **Bonus Code:** Gib mir einen kurzen Tailwind-CSS Code-Schnipsel, um das wichtigste Element (z.B. CTA Button) zu verbessern.
                """},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]
        )
        
        # 3. Anfrage an Vision Model
        response = vision_llm.invoke([message])
        return {"analysis": response.content}

    except Exception as e:
        print(f"❌ Vision Fehler: {e}")
        error_str = str(e).lower()
        if "429" in error_str or "resource_exhausted" in error_str:
             return {"analysis": "⚠️ **Rate Limit erreicht.** Google's Vision AI braucht eine kurze Pause. Bitte warte ca. 60 Sekunden."}
        return {"analysis": f"Fehler bei der Bildanalyse: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)