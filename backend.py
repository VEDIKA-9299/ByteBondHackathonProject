# backend.py (Complete code with Q&A functionality + TXT/DOCX support)
import os
import json
import pytesseract
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import fitz  # PyMuPDF
from PIL import Image
import tempfile
from dotenv import load_dotenv
import asyncio
import uuid
from docx import Document  # ADDED for DOCX support

# ----------------- Config / Setup -----------------
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if not os.path.exists(tesseract_path):
    raise RuntimeError(
        f"Tesseract OCR executable not found at: {tesseract_path}. "
        "Please install Tesseract or update the path."
    )
pytesseract.pytesseract.tesseract_cmd = tesseract_path

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = "" 
    print("Warning: GOOGLE_API_KEY not found; using placeholder. Replace before production.")
genai.configure(api_key=api_key)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)

# --- In-memory cache to store document text for Q&A ---
document_cache = {}

PROMPT_TEMPLATE = """
You are an expert legal assistant. Analyze the following legal document and return ONLY valid JSON using EXACTLY these top-level keys:

- "summary": (string) a concise summary of the document's purpose and key points.
- "extracted_terms": (array of objects) key legal terms and clauses with detailed explanations. Each object should have:
  {
    "term": "clause name or legal term",
    "content": "the actual clause text (if found)",
    "explanation": "detailed explanation in simple language",
    "importance": "High|Medium|Low",
    "risk_level": "High|Medium|Low|None"
  }
- "explanation": (string) overall explanation of the document's key aspects in simple language.
- "gaps": (array of objects) potential missing clauses, ambiguities, or risks. Each object should have:
  {
    "issue": "description of the gap or risk",
    "explanation": "why this is important",
    "recommendation": "suggested action or clause to add",
    "severity": "High|Medium|Low"
  }
- "verdict": (string) either "Red Flag" or "No Major Red Flags".
- "document_type": (string) type of legal document (e.g., "Employment Contract", "NDA", "Service Agreement").
- "key_obligations": (array of strings) main obligations for each party.
- "termination_clauses": (array of strings) how the agreement can be terminated.
- "dispute_resolution": (string) how disputes are handled according to the document.

IMPORTANT:
1) Respond with ONLY valid JSON and nothing else.
2) "verdict" must be a top-level key.
3) If you cannot find certain information, use empty arrays or "Not specified".
4) For extracted_terms and gaps, provide detailed, actionable explanations.
5) Focus on practical implications and risks for a layperson.
"""

# ----------------- Utility functions -----------------
def repair_json(response_text: str) -> dict:
    if not response_text:
        return {"error": "Empty response from model", "raw": ""}

    try:
        parsed = json.loads(response_text)
        return normalize_response(parsed)
    except json.JSONDecodeError:
        pass

    try:
        start = response_text.index("{")
        end = response_text.rindex("}") + 1
        candidate = response_text[start:end]
        parsed = json.loads(candidate)
        return normalize_response(parsed)
    except Exception:
        pass

    return {"error": "Invalid JSON from model", "raw": response_text}

def normalize_response(parsed: dict) -> dict:
    out = {}
    out["summary"] = parsed.get("summary", "—")
    out["explanation"] = parsed.get("explanation", "—")
    out["document_type"] = parsed.get("document_type", "Unknown")
    out["dispute_resolution"] = parsed.get("dispute_resolution", "Not specified")

    terms = parsed.get("extracted_terms", [])
    normalized_terms = []
    if isinstance(terms, list):
        for term in terms:
            if isinstance(term, dict):
                normalized_terms.append({
                    "term": term.get("term", "Unknown term"),
                    "content": term.get("content", ""),
                    "explanation": term.get("explanation", "No explanation provided"),
                    "importance": term.get("importance", "Medium"),
                    "risk_level": term.get("risk_level", "None")
                })
            elif isinstance(term, str):
                normalized_terms.append({
                    "term": term,
                    "content": "",
                    "explanation": "Basic term identified",
                    "importance": "Medium",
                    "risk_level": "None"
                })
    out["extracted_terms"] = normalized_terms

    gaps = parsed.get("gaps", [])
    normalized_gaps = []
    if isinstance(gaps, list):
        for gap in gaps:
            if isinstance(gap, dict):
                normalized_gaps.append({
                    "issue": gap.get("issue", "Unknown issue"),
                    "explanation": gap.get("explanation", "No explanation provided"),
                    "recommendation": gap.get("recommendation", "No recommendation provided"),
                    "severity": gap.get("severity", "Medium")
                })
            elif isinstance(gap, str):
                normalized_gaps.append({
                    "issue": gap,
                    "explanation": "Potential issue identified",
                    "recommendation": "Review with legal counsel",
                    "severity": "Medium"
                })
    out["gaps"] = normalized_gaps

    out["key_obligations"] = parsed.get("key_obligations", [])
    out["termination_clauses"] = parsed.get("termination_clauses", [])

    verdict = parsed.get("verdict")
    if isinstance(verdict, str):
        out["verdict"] = verdict
    else:
        out["verdict"] = "Red Flag" if out["gaps"] else "No Major Red Flags"

    return out

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def ocr_pdf_bytes(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            mode = "RGB" if pix.n < 4 else "RGBA"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img)
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        doc = Document(tmp.name)
        text = "\n".join([para.text for para in doc.paragraphs])
    return text

# ----------------- Endpoints -----------------
@app.get("/")
async def root():
    return {"message": "Legal Analyzer Backend is running!", "status": "OK", "endpoints": ["/analyze", "/docs"]}

@app.get("/test")
async def test_connection():
    return {"message": "Backend connection successful!", "version": "1.0"}

@app.post("/analyze")
async def analyze_full_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename = file.filename or "document"
    suffix = filename.split(".")[-1].lower()
    if suffix not in ("pdf", "png", "jpg", "jpeg", "txt", "docx"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF, image, TXT, or DOCX.")

    file_bytes = await file.read()
    extracted_text = ""

    if suffix == "pdf":
        extracted_text = extract_text_from_pdf_bytes(file_bytes)
        if not extracted_text.strip():
            extracted_text = ocr_pdf_bytes(file_bytes)
    elif suffix in ("png", "jpg", "jpeg"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            img = Image.open(tmp.name)
            extracted_text = pytesseract.image_to_string(img)
    elif suffix == "txt":
        extracted_text = file_bytes.decode("utf-8")
    elif suffix == "docx":
        extracted_text = extract_text_from_docx_bytes(file_bytes)

    if not extracted_text.strip():
        return {
            "summary": "No text could be extracted from the uploaded file.",
            "extracted_terms": [],
            "explanation": "No text extracted to analyze.",
            "gaps": [],
            "verdict": "No Major Red Flags",
            "document_type": "Unknown",
            "key_obligations": [],
            "termination_clauses": [],
            "dispute_resolution": "Not specified"
        }

    MAX_CHARS = 120000
    text_to_send = extracted_text if len(extracted_text) <= MAX_CHARS else (extracted_text[:80000] + "\n\n...TRUNCATED...\n\n" + extracted_text[-40000:])
    prompt = PROMPT_TEMPLATE + "\n\nDocument:\n" + text_to_send

    try:
        generation_config = GenerationConfig(response_mime_type="application/json")
        response = await model.generate_content_async(prompt, generation_config=generation_config)
        raw = response.text or ""
        parsed = repair_json(raw)

        if "error" in parsed:
            return {
                "summary": parsed.get("raw", "")[:800],
                "extracted_terms": [],
                "explanation": "Model returned malformed JSON; see raw for details.",
                "gaps": [],
                "verdict": "Unknown",
                "document_type": "Unknown",
                "key_obligations": [],
                "termination_clauses": [],
                "dispute_resolution": "Not specified",
                "raw": parsed.get("raw")
            }

        document_id = str(uuid.uuid4())
        document_cache[document_id] = extracted_text
        parsed["document_id"] = document_id

        return parsed
    except Exception as e:
        return {
            "summary": "Model call failed",
            "extracted_terms": [],
            "explanation": f"Model call failed: {str(e)}",
            "gaps": [],
            "verdict": "Unknown",
            "document_type": "Unknown",
            "key_obligations": [],
            "termination_clauses": [],
            "dispute_resolution": "Not specified"
        }

# ----------------- Clause Explanation & Q&A Endpoints (unchanged) -----------------
@app.post("/explain-clause")
async def explain_specific_clause(clause_text: str):
    prompt = f"""
    Explain this legal clause in simple, everyday language. Include:
    1. What it means in practical terms
    2. Why it's important
    3. Potential risks or benefits
    4. What someone should watch out for

    Clause: {clause_text}

    Respond in clear, conversational language as if explaining to a friend.
    """
    try:
        response = await model.generate_content_async(prompt)
        return {"explanation": response.text}
    except Exception as e:
        return {"explanation": f"Error explaining clause: {str(e)}"}

@app.post("/qna")
async def question_and_answer(data: dict = Body(...)):
    document_id = data.get("document_id")
    question = data.get("question")

    if not document_id or not question:
        raise HTTPException(status_code=400, detail="document_id and question are required.")

    document_text = document_cache.get(document_id)
    if not document_text:
        raise HTTPException(status_code=404, detail="Document not found or session expired.")

    prompt = f"""
    You are a helpful legal assistant. Your task is to answer the user's question based ONLY on the provided legal document text. Do not use any external knowledge. If the answer cannot be found in the document, you MUST state that clearly.

    *Legal Document Text:*
    ---
    {document_text}
    ---

    *User's Question:*
    "{question}"

    *Your Answer:*
    """
    try:
        response = await model.generate_content_async(prompt)
        return {"answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

@app.post("/suggest-questions")
async def suggest_questions(data: dict = Body(...)):
    document_id = data.get("document_id")
    if not document_id:
        raise HTTPException(status_code=400, detail="document_id is required.")

    document_text = document_cache.get(document_id)
    if not document_text:
        raise HTTPException(status_code=404, detail="Document not found or session expired.")

    prompt = f"""
    Based on the following legal document, generate a list of 3 to 5 insightful and relevant questions that a user might want to ask. These questions should focus on key obligations, risks, termination conditions, or ambiguous terms.

    *Legal Document Text (first 4000 characters):*
    ---
    {document_text[:4000]}
    ---

    Return your answer as a valid JSON object with a single key "questions" which is an array of strings.
    Example: {{"questions": ["What is the governing law?", "What are the termination conditions?"]}}
    """
    try:
        generation_config = GenerationConfig(response_mime_type="application/json")
        response = await model.generate_content_async(prompt, generation_config=generation_config)

        parsed_json = json.loads(response.text)
        if "questions" in parsed_json and isinstance(parsed_json["questions"], list):
            return parsed_json
        else:
            return {"questions": ["Could not generate suggestions."]}
    except Exception as e:
        print(f"Error suggesting questions: {e}")
        return {"questions": ["What is the main purpose of this document?", "Who are the parties involved?"]}
