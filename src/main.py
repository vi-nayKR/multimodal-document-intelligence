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

from typing import List
from pydantic import BaseModel, Field

class CustomLineItemInput(BaseModel):
    description: str = Field(..., example="Commercial Heavy Machinery Lease")
    quantity: float = Field(..., example=2.0)
    unit_price: float = Field(..., example=15000.0)

class CustomDocumentInput(BaseModel):
    filename: str = Field("commercial_loan_invoice.pdf", example="commercial_loan_invoice.pdf")
    invoice_number: str = Field("INV-2026-9901", example="INV-2026-9901")
    vendor_name: str = Field("AtlasOne Commercial Lending Partner", example="AtlasOne Commercial Lending Partner")
    customer_name: str = Field("Apex Freight & Logistics LLC", example="Apex Freight & Logistics LLC")
    line_items: List[CustomLineItemInput] = Field(
        default_factory=lambda: [
            CustomLineItemInput(description="Commercial Heavy Machinery Lease", quantity=2.0, unit_price=15000.0),
            CustomLineItemInput(description="Credit Risk Assessment Platform Access", quantity=1.0, unit_price=2500.0)
        ]
    )
    tax_rate: float = Field(0.18, example=0.18)

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

@app.post("/v1/extract/custom", tags=["Extraction"])
async def extract_custom_document(payload: CustomDocumentInput):
    """
    Ingests a newly provided commercial document, dynamically calculates line totals,
    subtotal, tax, and Grand Total Amount, and runs the Grounding Shield.
    """
    items = [
        {
            "item_index": idx,
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": round(item.quantity * item.unit_price, 2)
        }
        for idx, item in enumerate(payload.line_items, 1)
    ]
    doc = document_loader.load_custom_document(
        filename=payload.filename,
        invoice_number=payload.invoice_number,
        vendor_name=payload.vendor_name,
        customer_name=payload.customer_name,
        line_items=items,
        tax_rate=payload.tax_rate
    )
    extracted = await vision_extractor.extract_invoice(doc)
    grounding_report = grounding_shield.verify_invoice(extracted, doc)
    
    return {
        "document_id": doc.document_id,
        "filename": doc.filename,
        "arithmetic_breakdown": {
            "line_item_math": [
                f"{it['description']}: {it['quantity']} × ${it['unit_price']:,.2f} = ${it['total_price']:,.2f}"
                for it in items
            ],
            "subtotal": extracted.subtotal,
            "tax_amount": extracted.tax_amount,
            "formula": "Grand Total = Subtotal + Tax",
            "grand_total_calculated": extracted.total_amount
        },
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
