from fastapi import FastAPI, File, UploadFile, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import base64
import logging
import httpx
import re
from datetime import datetime
from langchain_core.tools import tool
import sentry_sdk

# ==========================================
# 1. SETUP
# ==========================================
load_dotenv()
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "production"),
    )
app = FastAPI()

# DEBUG: Origin Logging
@app.middleware("http")
async def log_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin:
        print(f"🔔 Request from Origin: {origin}")
    response = await call_next(request)
    return response

# Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# CORS
origins = [
    "http://localhost:4321",
    "http://localhost:3000",
    "https://sinanucar.com",
    "https://www.sinanucar.com",
    "https://sinan-ucar-portfolio.onrender.com",
]
origin_regex = r"https://.*\.cloudworkstations\.dev|http://localhost:\d+"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=origin_regex,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {type(exc).__name__}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal Server Error"},
    )

# ==========================================
# 2. DATA (CV)
# ==========================================
CV_CONTEXT = ""
def load_cv():
    global CV_CONTEXT
    file_path = os.path.join("data", "cv.md")
    try:
        if not os.path.exists(file_path):
            CV_CONTEXT = "Kein Lebenslauf gefunden."
            return
        with open(file_path, "r", encoding="utf-8") as f:
            CV_CONTEXT = f.read()
        print(f"✅ CV loaded! ({len(CV_CONTEXT)} chars)")
    except Exception as e:
        print(f"❌ Error loading CV: {e}")
        CV_CONTEXT = "Error loading CV."
load_cv()

# ==========================================
# 3. AI MODELS (Resilient Fallback System)
# ==========================================
# Resilience: Separate Fallback Chains für Text vs. Vision
# Syntax: provider:model_name

# /api/chat, /api/analyze, /api/agent — Groq primär (LPU: 10-20× schneller, sehr stabil)
LLM_MODELS_TEXT = [
    "groq:llama-3.3-70b-versatile",
    "google:gemini-flash-latest",
    "openai:gpt-4o-mini",
    "google:gemini-2.0-flash",
]

# /api/vision — Groq hat kein Multimodal, Google Gemini bleibt primär
LLM_MODELS_VISION = [
    "google:gemini-flash-latest",
    "google:gemini-2.0-flash",
    "openai:gpt-4o-mini",
]

def _get_llm(model_id: str, timeout: float = 30.0):
    """Factory for different LLM providers."""
    if ":" not in model_id:
        return None
    
    provider, model_name = model_id.split(":", 1)
    
    if provider == "google":
        key = os.getenv("GOOGLE_API_KEY")
        if not key: return None
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=key, max_retries=0, request_timeout=timeout)
    
    elif provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key: return None
        return ChatOpenAI(model=model_name, api_key=key, max_retries=0, request_timeout=timeout)
    
    elif provider == "groq":
        key = os.getenv("GROQ_API_KEY")
        if not key: return None
        return ChatGroq(model=model_name, groq_api_key=key, max_retries=0, request_timeout=timeout)
    
    elif provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key: return None
        return ChatAnthropic(model=model_name, anthropic_api_key=key, max_retries=0, request_timeout=timeout)
    
    return None

async def invoke_resiliently(prompt_or_messages, input_data=None, is_vision=False, structured_class=None):
    """Tries multiple models in sequence if one fails due to Quota or Timeout."""
    last_error: Exception = Exception("Unknown error")
    timeout = 30.0 if not is_vision else 45.0
    models = LLM_MODELS_VISION if is_vision else LLM_MODELS_TEXT

    for model_id in models:
        try:
            temp_llm = _get_llm(model_id, timeout=timeout)
            if not temp_llm:
                print(f"⏩ Skipping {model_id} (No API Key or Invalid Provider)")
                continue
            
            # Handle structured output if requested
            target_llm = temp_llm
            if structured_class:
                target_llm = temp_llm.with_structured_output(structured_class)
            
            # Case 1: Prompt Template + Input Data
            if input_data is not None and hasattr(prompt_or_messages, "invoke"):
                current_prompt_template: ChatPromptTemplate = prompt_or_messages # type: ignore
                chain = current_prompt_template | target_llm
                return await chain.ainvoke(input_data)
            
            # Case 2: List of Messages or raw prompt
            return await target_llm.ainvoke(prompt_or_messages)
            
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Model {model_id} failed: {error_msg[:100]}...")
            last_error = e
            continue
    raise last_error

# ==========================================
# 3.1 AGENT TOOLS
# ==========================================
@tool
def get_cv_summary() -> dict:
    """Returns a structured summary of Sinan Ucar's core competencies, skills, education,
    and professional background. Use this when asked about skills, experience, tech stack,
    or professional background."""
    return {
        "name": "Sinan Ucar",
        "title": "Senior AI Solutions Architect | Diplom-Informatiker",
        "education": {
            "degree": "Diplom-Informatik (equiv. M.Sc. Computer Science) — mit Auszeichnung",
            "university": "Technische Universität Dortmund (2000–2008)",
            "thesis": "Connectionist Systems in Natural & Artificial Intelligence and Cognitive Neuroscience",
        },
        "experience_years": "15+ years software engineering, AI focus since 2024",
        "current_role": "Senior Software Engineer @ Ceyoniq Technology GmbH (since 10/2022) + independent AI R&D",
        "ai_skills": [
            "LangChain (langchain-core, -google-genai, -openai, -groq, -anthropic)",
            "Multi-Provider LLM Fallback Architecture",
            "Structured Output via Pydantic (with_structured_output)",
            "RAG — Retrieval-Augmented Generation (ChromaDB, Vector Embeddings)",
            "Agentic Workflows (Tool-Calling, ReAct pattern, LangGraph)",
            "LLM providers: Gemini, GPT-4o, Groq (LPU), Claude",
            "Multimodal Vision APIs",
            "Sentiment Analysis & NLP pipelines",
        ],
        "backend_skills": [
            "FastAPI + Python 3.12 (async/await)",
            "Node.js / Express",
            "C# / .NET",
            "REST API Design & Data Governance",
            "Sentry Monitoring, Docker, GitLab CI/CD",
            "Playwright E2E Testing (>90% coverage)",
        ],
        "frontend_skills": [
            "Astro.js (Islands Architecture)",
            "Next.js 16 (App Router, Server Components)",
            "TypeScript",
            "Tailwind CSS",
            "Vue.js, Web Components (Lit)",
        ],
        "architecture_focus": (
            "Deterministic, production-grade AI integrations — "
            "bridging classical enterprise systems with LLM backends. "
            "Key concerns: hallucination reduction via structured output, "
            "latency optimization via Groq LPU, resilient fallback chains."
        ),
        "languages": ["German (native)", "English (professional)", "Turkish (native)"],
    }


@tool
def get_project_details(project_name: str) -> dict:
    """Returns technical details about one of Sinan's portfolio projects.
    Use this when asked about a specific project.
    Available projects: 'Realize Together', 'Logopädie Report Agent', 'Portfolio Backend'."""
    projects = {
        "realize together": {
            "name": "RealizeTogether",
            "description": "AI-powered collaboration platform for goal setting and accountability between users.",
            "stack": ["Next.js 16 (App Router)", "Supabase (PostgreSQL + Auth + Realtime)", "FastAPI", "TypeScript"],
            "ai_technologies": [
                "LangChain multi-provider LLM orchestration",
                "Structured Output with Pydantic",
                "Multi-Provider Fallback (Groq → Gemini → OpenAI)",
            ],
            "architecture": (
                "Fullstack: Next.js frontend with Server Components by default for performance. "
                "FastAPI as dedicated AI microservice (separation of concerns). "
                "Supabase handles auth, real-time subscriptions, and PostgreSQL persistence."
            ),
            "key_decisions": [
                "Server Components by default — client boundary only where strictly necessary",
                "FastAPI as AI microservice — keeps AI complexity isolated from Next.js layer",
                "Supabase for zero-config auth and realtime — avoids building custom WebSocket infra",
                "Groq LPU as primary LLM — 10–20× faster inference than OpenAI at lower cost",
            ],
            "status": "Active development",
        },
        "logopädie report agent": {
            "name": "Logopädie Report Agent",
            "description": (
                "AI agent that automates professional therapy report generation for speech therapists. "
                "Includes audio transcription (session recordings → structured reports)."
            ),
            "stack": ["Next.js 16", "FastAPI", "Groq (Whisper API)", "LangChain", "Python 3.12"],
            "ai_technologies": [
                "Groq Whisper for ultra-fast audio transcription",
                "LLM-driven structured report generation",
                "Pydantic structured output for consistent report format",
            ],
            "architecture": (
                "Next.js frontend → FastAPI backend pipeline: "
                "audio upload → Whisper transcription → LLM report generation → structured JSON output. "
                "Async pipeline handles files up to 4MB."
            ),
            "key_decisions": [
                "Groq chosen for transcription — LPU advantage: near-instant turnaround vs. OpenAI Whisper",
                "Pydantic structured output — ensures reports are always parseable, never free-form hallucinations",
                "FastAPI async — handles concurrent therapist sessions without blocking",
                "Portfolio-grade production patterns applied to a real domain problem",
            ],
            "status": "Portfolio project — live demo available",
        },
        "portfolio backend": {
            "name": "Sinan Ucar Portfolio Backend",
            "description": "Production FastAPI backend powering sinanucar.com with 4 AI endpoints showcasing different LLM integration patterns.",
            "stack": ["FastAPI", "Python 3.12", "LangChain", "Astro.js (frontend)", "Render (deployment)", "Sentry"],
            "ai_technologies": [
                "Multi-Provider Fallback: Groq → Gemini → OpenAI (invoke_resiliently)",
                "Tool-Calling Agent (manual async loop — no LangGraph overhead)",
                "Structured Output via Pydantic for all endpoints",
                "Multimodal Vision Analysis (Gemini Flash)",
                "Sentiment Analysis with typed emotion output",
            ],
            "architecture": (
                "4 endpoints: /api/chat (CV assistant with context injection), "
                "/api/vision (UX screenshot analyzer, multimodal), "
                "/api/analyze (sentiment with structured Pydantic output), "
                "/api/agent (tool-calling agent with async manual loop). "
                "invoke_resiliently() tries providers in sequence on quota/timeout failure. "
                "Separate fallback chains: text (Groq-first) vs. vision (Gemini-first, no Groq multimodal)."
            ),
            "key_decisions": [
                "Groq as primary LLM — LPU: 10–20× faster than OpenAI, ideal for latency-sensitive portfolio demos",
                "Manual agent loop instead of LangGraph — simpler, zero graph overhead for current tool count",
                "Separate vision fallback chain — Groq has no multimodal support, Gemini Flash is primary",
                "Sentry integration — production-grade observability even for a portfolio project",
                "CORS allowlist (no wildcard) — security by default",
            ],
            "status": "Live at sinanucar.com",
        },
    }

    def _normalize(s: str) -> str:
        return s.lower().strip().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")

    key = _normalize(project_name)
    for project_key, project_data in projects.items():
        norm_key = _normalize(project_key)
        if norm_key in key or key in norm_key or any(word in key for word in norm_key.split()):
            return project_data

    return {
        "error": f"Project '{project_name}' not found.",
        "available_projects": list(projects.keys()),
    }


@tool
def get_availability() -> dict:
    """Returns Sinan Ucar's current availability, preferred roles, work model preferences,
    and how to get in touch. Use this when asked about hiring, availability, job search,
    or work preferences."""
    return {
        "availability": "Available with 3-month notice period (Kündigungsfrist)",
        "notice_period_months": 3,
        "open_to_roles": [
            "AI Engineer",
            "Senior AI Solutions Architect",
            "Backend Engineer with AI/LLM focus",
            "Technical Lead (AI-first teams)",
        ],
        "not_interested_in": "Pure frontend-only or non-AI/non-backend roles",
        "work_model": "Remote preferred — hybrid possible for right opportunity",
        "location": "Germany",
        "preferred_tech_stack": ["Python", "FastAPI", "LangChain / LangGraph", "Next.js", "TypeScript"],
        "domain_interests": [
            "Enterprise AI integration",
            "Agentic systems & RAG pipelines",
            "LLM governance & deterministic AI",
            "Developer tooling with AI",
        ],
        "contact": "sinanucar.com/kontakt or info@sinanucar.com",
        "linkedin": "linkedin.com/in/infosinanucar",
    }


@tool
async def web_search(query: str) -> str:
    """Searches the web using DuckDuckGo and returns a summary of top results. Use this to find current information about any topic."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1", "no_redirect": "1"}
            )
            data = resp.json()

        results = []
        if data.get("AbstractText"):
            results.append(f"📌 {data['AbstractText']} (Quelle: {data.get('AbstractSource', '')})")
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"• {topic['Text']}")

        return "\n".join(results) if results else "Keine Ergebnisse gefunden."
    except Exception as e:
        return f"Web-Suche fehlgeschlagen: {str(e)}"

@tool
async def fetch_webpage(url: str) -> str:
    """Fetches the text content of a webpage. Use this to read the full content of a URL found in web search results."""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:3000]
    except Exception as e:
        return f"Fehler beim Abrufen der Seite: {str(e)}"

import ast as _ast

def _safe_eval_node(node: _ast.expr) -> float | int:
    """Recursively evaluates a safe arithmetic AST node. Raises ValueError for disallowed constructs."""
    if isinstance(node, _ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Ungültiger Typ: {type(node.value).__name__}")
    if isinstance(node, _ast.UnaryOp) and isinstance(node.op, _ast.USub):
        return -_safe_eval_node(node.operand)
    if isinstance(node, _ast.BinOp):
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        ops = {
            _ast.Add: lambda a, b: a + b,
            _ast.Sub: lambda a, b: a - b,
            _ast.Mult: lambda a, b: a * b,
            _ast.Div: lambda a, b: a / b,
            _ast.Pow: lambda a, b: a ** b,
            _ast.Mod: lambda a, b: a % b,
        }
        op_type = type(node.op)
        if op_type not in ops:
            raise ValueError(f"Ungültiger Operator: {op_type.__name__}")
        return ops[op_type](left, right)
    raise ValueError(f"Ungültiger Ausdruck: {type(node).__name__}")


@tool
def calculator(expression: str) -> str:
    """Evaluates a safe arithmetic expression (e.g. '2 + 3 * 4'). Supports +, -, *, /, **, %.
    Only numeric literals and arithmetic operators are allowed — no function calls or imports."""
    try:
        tree = _ast.parse(expression.strip(), mode="eval")
        result = _safe_eval_node(tree.body)
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except ZeroDivisionError:
        return "Fehler: Division durch Null"
    except Exception as e:
        return f"Fehler: {e}"


_PORTFOLIO_PROJECTS = [
    {
        "name": "RealizeTogether",
        "stack": ["Next.js 16", "Supabase", "FastAPI", "TypeScript", "LangChain"],
        "description": "AI-powered collaboration platform for goal setting and accountability.",
    },
    {
        "name": "Logopädie Report Agent",
        "stack": ["Next.js 16", "FastAPI", "Groq", "Whisper", "LangChain", "Python"],
        "description": "AI agent for automated therapy report generation for speech therapists.",
    },
    {
        "name": "Portfolio Backend",
        "stack": ["FastAPI", "Python", "LangChain", "Astro.js", "Sentry"],
        "description": "Production FastAPI backend powering sinanucar.com with 4 AI endpoints.",
    },
]


@tool
def search_projects(query: str) -> str:
    """Searches Sinan's portfolio projects by keyword. Returns matching project names and descriptions."""
    q = query.lower()
    matches = [
        p for p in _PORTFOLIO_PROJECTS
        if q in p["name"].lower()
        or q in p["description"].lower()
        or any(q in s.lower() for s in p["stack"])
    ]
    if not matches:
        return "Keine passenden Projekte gefunden."
    return "\n".join(
        f"{p['name']}: {p['description']} (Stack: {', '.join(p['stack'])})"
        for p in matches
    )


@tool
def get_current_time() -> str:
    """Returns the current date and time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [get_cv_summary, get_project_details, get_availability, web_search, fetch_webpage, calculator, search_projects, get_current_time]

# ==========================================
# 4. DATA MODELS
# ==========================================
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    language: Literal["de", "en"] = "de"

class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=5000)

class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    language: Literal["de", "en"] = "de"
    history: list[HistoryMessage] = Field(default_factory=list, max_length=20)

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    language: Literal["de", "en"] = "de"

class ChatAnswer(BaseModel):
    reply: str = Field(
        description=(
            "Answer about Sinan Ucar based strictly on the provided CV. "
            "Never claim to be Sinan. Never invent facts not present in the CV."
        )
    )

class SentimentAnalysis(BaseModel):
    score: float = Field(description="Score -1.0 to 1.0")
    # Wir behalten die internen IDs (freude, wut...), mappen aber die Ausgabe im Frontend
    emotion: Literal['freude', 'wut', 'trauer', 'neutral', 'angst'] = Field(description="Primary emotion key")
    suggestion: str = Field(description="Short suggestion for improvement")

class VisionAnalysis(BaseModel):
    impression: Literal['positive', 'negative', 'neutral'] = Field(description="First impression of the design")
    usability_score: int = Field(description="Score from 1 to 10 for usability")
    design_feedback: str = Field(description="Feedback on colors, whitespace, typography")
    improvements: list[str] = Field(description="Exactly 3 concrete actionable improvements")
    tailwind_code: Optional[str] = Field(description="A short Tailwind CSS snippet if applicable, else empty string")

# ==========================================
# 5. ENDPOINTS
# ==========================================

# --- CHAT ---
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"📩 Chat: {request.message} | Lang: {request.language}")
    
    if request.language == "en":
        template = (
            "You are an AI portfolio assistant for Sinan Ucar's website. "
            "IMPORTANT: You are NOT Sinan Ucar. You are an AI assistant that knows his resume. "
            "If asked who you are, say: 'I am Sinan's AI assistant. Ask me about his experience, skills, or projects.' "
            "Answer ONLY based on the resume below. NEVER invent facts, dates, or details not present in the resume. "
            "If information is not in the resume, say so explicitly.\n\n"
            "Resume:\n{cv_text}\n\n"
            "Question: {user_message}\n\n"
            "Answer (English, concise, professional):"
        )
    else:
        template = (
            "Du bist ein KI-Portfolio-Assistent auf Sinans Website. "
            "WICHTIG: Du BIST NICHT Sinan Ucar. Du bist ein KI-System, das seinen Lebenslauf kennt. "
            "Wenn gefragt 'Wer bist du?', antworte: 'Ich bin Sinans KI-Assistent. Frag mich nach seiner Erfahrung, seinen Skills oder Projekten.' "
            "Antworte AUSSCHLIESSLICH auf Basis des folgenden Lebenslaufs. Erfinde NIEMALS Fakten, Daten oder Details, die nicht im Lebenslauf stehen. "
            "Falls eine Information nicht im Lebenslauf enthalten ist, sage das explizit.\n\n"
            "Lebenslauf:\n{cv_text}\n\n"
            "Frage: {user_message}\n\n"
            "Antwort (Deutsch, kurz, professionell):"
        )

    chain = ChatPromptTemplate.from_template(template)
    try:
        start_time = datetime.now()
        res = await invoke_resiliently(chain, {"cv_text": str(CV_CONTEXT), "user_message": request.message}, structured_class=ChatAnswer)
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✅ AI Response in {duration:.2f}s")
        reply = res.reply if isinstance(res, ChatAnswer) else getattr(res, 'content', str(res))
        return {"reply": reply}
    except Exception as e:
        if "429" in str(e):
            return {"reply": "Quota Error: Alle KI-Modelle haben ihr Tageslimit erreicht. Bitte versuche es später wieder! (API Quota Exhausted)"}
        return {"reply": "Error/Fehler: " + str(e)}

_MAX_UPLOAD_SIZE = 4 * 1024 * 1024  # 4 MB
_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# --- VISION ---
@app.post("/api/vision")
async def vision_endpoint(file: UploadFile = File(...), language: str = Form("de")):
    print(f"🖼️ Vision: {file.filename} | Lang: {language}")

    if file.content_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Ungültiger Dateityp. Erlaubt: JPEG, PNG, WebP, GIF.")

    try:
        contents = await file.read()

        if len(contents) > _MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="Datei zu groß. Maximale Größe: 4 MB.")

        image_b64 = base64.b64encode(contents).decode("utf-8")
        
        # PROMPT UMSCHALTEN
        if language == "en":
            prompt_text = """
            You are a Senior UX/UI Designer. Analyze this screenshot and return structured JSON.
            1. 'impression': Your first impression (positive, negative, neutral).
            2. 'usability_score': Score from 1 to 10.
            3. 'design_feedback': General feedback on design elements.
            4. 'improvements': 3 concrete points to improve.
            5. 'tailwind_code': A short Tailwind CSS snippet if applicable.
            """
        else:
            prompt_text = """
            Du bist ein Senior UX/UI Designer. Analysiere diesen Screenshot und antworte strikt in JSON.
            1. 'impression': Dein erster Eindruck (positive, negative, neutral) - der Wert MUSS auf Englisch sein!
            2. 'usability_score': Punktzahl von 1 bis 10.
            3. 'design_feedback': Feedback zu Design-Elementen (auf Deutsch).
            4. 'improvements': 3 konkrete Verbesserungsvorschläge (auf Deutsch).
            5. 'tailwind_code': Ein kurzes Tailwind CSS Snippet (falls anwendbar).
            """

        message = HumanMessage(content=[
            {"type": "text", "text": prompt_text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ])
        
        response = await invoke_resiliently([message], is_vision=True, structured_class=VisionAnalysis)
        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Vision Error: {e}")
        return {"error": str(e)}

# --- SENTIMENT ---
@app.post("/api/analyze")
async def analyze_sentiment(request: AnalyzeRequest):
    display_text = str(request.text)
    print(f"📊 Sentiment ({request.language}): {display_text[:30]}...")
    
    # SYSTEM PROMPT UMSCHALTEN
    if request.language == "en":
        sys_prompt = "You are a sentiment analysis expert. Analyze the text. The 'suggestion' field MUST be in English. For 'emotion', strictly select the best fitting key from the allowed list (even if they are German words)."
    else:
        sys_prompt = "Du bist ein Experte für Sentiment-Analyse. Analysiere den Text und gib JSON zurück. Das Feld 'suggestion' soll auf Deutsch sein."

    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_prompt),
        ("human", "Text: {text}")
    ])
    
    try:
        result = await invoke_resiliently(prompt, {"text": request.text}, structured_class=SentimentAnalysis)
        return result
    except Exception as e:
        print(f"❌ Analyze Error: {e}")
        return {"error": str(e)}

# --- AGENT ---
@app.post("/api/agent")
async def agent_endpoint(request: AgentRequest):
    print(f"🤖 Agent Request (Async Loop): {request.message} | History: {len(request.history)} msgs")
    try:
        start_time = datetime.now()

        system_content = (
            "Du bist Sinans KI-Portfolio-Assistent auf sinanucar.com. "
            "IDENTITÄT: Du BIST NICHT Sinan Ucar. Du bist ein KI-System, das Informationen ÜBER Sinan bereitstellt. "
            "Wenn gefragt 'Wer bist du?' oder 'Bist du Sinan?', antworte IMMER: "
            "'Ich bin Sinans KI-Assistent. Ich beantworte Fragen über seine Berufserfahrung, Skills und Projekte.' "
            "HALLUZINATIONS-SCHUTZ: Erfinde NIEMALS Fakten, Daten, Gehälter, Kontaktdaten oder Details. "
            "Nutze ausschließlich die Tool-Ergebnisse und die unten genannten Kernfakten. "
            f"Antworte in der Sprache: {request.language}. "
            "Kernfakten (fest, unveränderlich): "
            "Name: Sinan Ucar | "
            "Aktuelle Stelle: Senior Software Engineer @ Ceyoniq Technology GmbH (seit 10/2022) + eigenständige KI-Projekte | "
            "Abschluss: Diplom-Informatik, TU Dortmund | "
            "Erfahrung: 15+ Jahre Software Engineering, KI-Fokus seit 2024. "
            "Nutze Tools still im Hintergrund — erwähne sie NIEMALS in der Antwort: "
            "- get_cv_summary() → vollständige Skills, Tech-Stack, Ausbildung, Berufserfahrung "
            "- get_project_details(project_name) → Projekte: Realize Together, Logopädie Report Agent, Portfolio Backend "
            "- get_availability() → Verfügbarkeit, bevorzugte Rollen, Wechselbereitschaft, Kontakt "
            "- web_search(query) → aktuelle externe Informationen "
            "Antworte präzise, professionell und ohne jegliche technische Metakommentare."
        )
        messages: list = [{"role": "system", "content": system_content}]
        for h in request.history:
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": request.message})
        
        # Helper for Agent Tool Binding (since we have to bind tools to each model in the fallback)
        async def agent_invoke(msgs: list):
            last_err: Exception = Exception("Agent fallback failed")
            for model_id in LLM_MODELS_TEXT:
                try:
                    llm = _get_llm(model_id, timeout=45.0)
                    if not llm: continue
                    
                    llm_with_tools = llm.bind_tools(tools)
                    return await llm_with_tools.ainvoke(msgs)
                except Exception as ex:
                    err_msg = str(ex)
                    print(f"⚠️ Agent Model {model_id} failed: {err_msg[:50]}...")
                    last_err = ex
            raise last_err

        # 1. LLM Reasoning
        print("🔄 Step 1: LLM reasoning...")
        ai_msg = await agent_invoke(messages)
        messages.append(ai_msg)

        # Sicherer Zugriff auf Tool-Calls (LangChain Returns können variieren)
        tool_calls = getattr(ai_msg, 'tool_calls', [])
        if not tool_calls and isinstance(ai_msg, dict):
            tool_calls = ai_msg.get('tool_calls', [])

        # 2. Tool EXECUTION
        if tool_calls:
            print(f"🛠️ Executing {len(tool_calls)} Tool Calls...")
            for tool_call in tool_calls:
                selected_tool = next((t for t in tools if t.name == tool_call["name"]), None)
                if selected_tool:
                    print(f"  -> Action: {tool_call['name']}")
                    tool_output = await selected_tool.ainvoke(tool_call["args"])
                    messages.append({
                        "role": "tool",
                        "content": str(tool_output),
                        "tool_call_id": tool_call["id"]
                    })
            
            # 3. Finaler Call
            print("🔄 Step 2: Final response with tool data...")
            # We need the fallback here too
            final_res = await agent_invoke(messages)
            reply = getattr(final_res, 'content', str(final_res))
            return {"reply": reply}
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✅ Agent Response in {duration:.2f}s")
        reply = getattr(ai_msg, 'content', str(ai_msg))
        return {"reply": reply}
        
    except Exception as e:
        print(f"❌ Agent Error: {e}")
        return {"reply": f"Sorry, mein System hängt gerade: {str(e)}"}

# --- HEALTH (Render health check) ---
@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "realizetogether-ai"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)