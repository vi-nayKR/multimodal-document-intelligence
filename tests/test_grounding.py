import pytest
import asyncio
from src.extractor.schemas import InvoiceExtractionSchema, LineItemSchema
from src.verifier.grounding_shield import grounding_shield
from src.parser.document_loader import document_loader

def test_grounded_invoice_extraction():
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    
    extracted = InvoiceExtractionSchema(
        invoice_number="INV-2026-8891",
        invoice_date="2026-08-21",
        vendor_name="CloudScale Systems Inc",
        customer_name="Medha Platform Corp",
        line_items=[
            LineItemSchema(item_index=1, description="Enterprise Cloud Gateway Node", quantity=4.0, unit_price=1250.0, total_price=5000.0)
        ],
        subtotal=5000.0,
        tax_amount=900.0,
        total_amount=10620.00
    )

    report = grounding_shield.verify_invoice(extracted, doc)
    assert report.is_fully_grounded is True
    assert report.precision_score == 1.0
    assert len(report.flagged_fields) == 0

def test_hallucination_detection():
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    
    # Injected hallucinated vendor name and fabricated invoice number
    hallucinated = InvoiceExtractionSchema(
        invoice_number="INV-FAKE-99999",
        invoice_date="2026-08-21",
        vendor_name="Nonexistent Phantom Technologies LLC",
        customer_name="Medha Platform Corp",
        line_items=[
            LineItemSchema(item_index=1, description="Enterprise Cloud Gateway Node", quantity=4.0, unit_price=1250.0, total_price=5000.0)
        ],
        subtotal=5000.0,
        tax_amount=900.0,
        total_amount=10620.00
    )

    report = grounding_shield.verify_invoice(hallucinated, doc)
    assert report.is_fully_grounded is False
    assert "invoice_number" in report.flagged_fields
    assert "vendor_name" in report.flagged_fields
    assert report.precision_score < 1.0

def test_overall_precision_calculation():
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    extracted = InvoiceExtractionSchema(
        invoice_number="INV-2026-8891",
        invoice_date="2026-08-21",
        vendor_name="CloudScale Systems Inc",
        customer_name="Medha Platform Corp",
        subtotal=9000.0,
        tax_amount=1620.0,
        total_amount=10620.00
    )
    report = grounding_shield.verify_invoice(extracted, doc)
    assert report.total_fields == 5
    assert report.grounded_fields == 5
    assert report.precision_score == 1.0
