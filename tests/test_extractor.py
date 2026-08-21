import pytest
import asyncio
from pydantic import ValidationError
from src.extractor.schemas import InvoiceExtractionSchema, LineItemSchema, FinancialBalanceSheetSchema
from src.extractor.vision_extractor import vision_extractor
from src.parser.document_loader import document_loader

def test_line_item_schema_validation():
    item = LineItemSchema(
        item_index=1,
        description="High-Throughput GPU Node",
        quantity=2.0,
        unit_price=1500.0,
        total_price=3000.0
    )
    assert item.quantity == 2.0
    assert item.total_price == 3000.0

def test_invoice_schema_validation():
    payload = {
        "invoice_number": "INV-1002",
        "invoice_date": "2026-08-21",
        "vendor_name": "DeepMind Corp",
        "customer_name": "Enterprise Client",
        "line_items": [
            {"item_index": 1, "description": "LLM License", "quantity": 1.0, "unit_price": 5000.0, "total_price": 5000.0}
        ],
        "subtotal": 5000.0,
        "tax_amount": 900.0,
        "total_amount": 5900.0,
        "currency": "USD"
    }
    invoice = InvoiceExtractionSchema(**payload)
    assert invoice.invoice_number == "INV-1002"
    assert len(invoice.line_items) == 1
    assert invoice.total_amount == 5900.0

def test_invalid_schema_rejection():
    with pytest.raises(ValidationError):
        # Missing required total_amount and customer_name
        InvoiceExtractionSchema(
            invoice_number="INV-FAIL",
            invoice_date="2026-08-21",
            vendor_name="Invalid Corp",
            subtotal=100.0
        )

@pytest.mark.asyncio
async def test_vision_extractor_end_to_end():
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    extracted = await vision_extractor.extract_invoice(doc)
    
    assert extracted.invoice_number == "INV-2026-8891"
    assert extracted.vendor_name == "CloudScale Systems Inc"
    assert len(extracted.line_items) == 3
    assert extracted.total_amount == 10620.00
    assert extracted.confidence_score >= 0.95
