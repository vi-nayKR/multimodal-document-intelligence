import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from config import settings
from src.parser.document_loader import document_loader
from src.parser.layout_analyzer import layout_analyzer
from src.extractor.vision_extractor import vision_extractor
from src.table_engine.reconstructor import table_reconstructor
from src.verifier.grounding_shield import grounding_shield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="High-Throughput Multimodal Document Intelligence & Vision AI Extraction Engine with Docling, Vision LLMs, and Strict Pydantic Schemas."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def serve_ui():
    """Serves the split-screen OpenAI-standard document intelligence console."""
    ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "index.html")
    if os.path.exists(ui_path):
        with open(ui_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Multimodal Document Intelligence Engine</h1>"

@app.post("/v1/extract/invoice", tags=["Extraction"])
async def extract_invoice():
    """Extracts and validates structured invoice data from an uploaded or sample document."""
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    extracted = await vision_extractor.extract_invoice(doc)
    grounding_report = grounding_shield.verify_invoice(extracted, doc)
    
    return {
        "document_id": doc.document_id,
        "filename": doc.filename,
        "extraction": extracted.model_dump(),
        "grounding": grounding_report.model_dump()
    }

@app.get("/v1/layout", tags=["Layout"])
async def get_layout():
    """Returns spatial bounding box layout breakdown for the active document."""
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    return layout_analyzer.get_layout_summary(doc)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "default_vision_model": settings.DEFAULT_VISION_MODEL
    }
