import time
import hashlib
import uuid
from typing import Dict, Any, List, Optional
from src.parser.models import ParsedDocument, ParsedPage, DocumentBlock, BlockType, BoundingBox

class DocumentLoader:
    """
    Multi-format document ingestion engine.
    Processes PDFs, images, TIFFs, and structured document streams into canonical ParsedDocument objects.
    """
    @staticmethod
    def load_from_sample(
        filename: str = "sample_invoice.pdf",
        doc_type: str = "invoice"
    ) -> ParsedDocument:
        """
        Loads a standard enterprise benchmark invoice document with spatial coordinates.
        """
        doc_id = f"doc_{uuid.uuid4().hex[:10]}"
        now = time.time()
        
        # Simulated high-fidelity 300 DPI Invoice Page (width: 2480px, height: 3508px)
        blocks = [
            DocumentBlock(
                block_id="b1",
                page_index=0,
                block_type=BlockType.HEADER,
                text="ACME CORP — COMMERCIAL TAX INVOICE",
                bbox=BoundingBox(x0=0.08, y0=0.05, x1=0.65, y1=0.10),
                confidence=0.99
            ),
            DocumentBlock(
                block_id="b2",
                page_index=0,
                block_type=BlockType.KEY_VALUE,
                text="Invoice Number: INV-2026-8891",
                bbox=BoundingBox(x0=0.68, y0=0.05, x1=0.92, y1=0.08),
                confidence=0.98,
                metadata={"key": "invoice_number", "value": "INV-2026-8891"}
            ),
            DocumentBlock(
                block_id="b3",
                page_index=0,
                block_type=BlockType.KEY_VALUE,
                text="Invoice Date: 2026-08-21",
                bbox=BoundingBox(x0=0.68, y0=0.09, x1=0.92, y1=0.12),
                confidence=0.98,
                metadata={"key": "invoice_date", "value": "2026-08-21"}
            ),
            DocumentBlock(
                block_id="b4",
                page_index=0,
                block_type=BlockType.KEY_VALUE,
                text="Vendor: CloudScale Systems Inc, 100 Innovation Way, San Francisco, CA",
                bbox=BoundingBox(x0=0.08, y0=0.14, x1=0.48, y1=0.22),
                confidence=0.97,
                metadata={"key": "vendor_name", "value": "CloudScale Systems Inc"}
            ),
            DocumentBlock(
                block_id="b5",
                page_index=0,
                block_type=BlockType.KEY_VALUE,
                text="Customer: Medha Platform Corp, Bangalore, India",
                bbox=BoundingBox(x0=0.52, y0=0.14, x1=0.92, y1=0.22),
                confidence=0.97,
                metadata={"key": "customer_name", "value": "Medha Platform Corp"}
            ),
            DocumentBlock(
                block_id="b6",
                page_index=0,
                block_type=BlockType.TABLE_REGION,
                text="Item | Description | Quantity | Unit Price | Total\n1 | Enterprise Cloud Gateway Node | 4 | $1,250.00 | $5,000.00\n2 | Redis 8 Vector Cache License | 2 | $800.00 | $1,600.00\n3 | Multimodal Vision OCR Engine | 1 | $2,400.00 | $2,400.00",
                bbox=BoundingBox(x0=0.08, y0=0.26, x1=0.92, y1=0.60),
                confidence=0.96
            ),
            DocumentBlock(
                block_id="b7",
                page_index=0,
                block_type=BlockType.KEY_VALUE,
                text="Subtotal: $9,000.00\nTax (18% GST): $1,620.00\nTotal Amount Due: $10,620.00",
                bbox=BoundingBox(x0=0.55, y0=0.62, x1=0.92, y1=0.75),
                confidence=0.99,
                metadata={"total_amount": 10620.00, "tax_amount": 1620.00}
            ),
            DocumentBlock(
                block_id="b8",
                page_index=0,
                block_type=BlockType.FOOTER,
                text="Payment Terms: Net 30 Days. Bank: HDFC Commercial Account #99283741. Thank you for your business!",
                bbox=BoundingBox(x0=0.08, y0=0.88, x1=0.92, y1=0.95),
                confidence=0.95
            )
        ]

        raw_text = "\n\n".join(b.text for b in blocks)

        page0 = ParsedPage(
            page_index=0,
            width_px=2480,
            height_px=3508,
            dpi=300,
            blocks=blocks,
            raw_text=raw_text
        )

        return ParsedDocument(
            document_id=doc_id,
            filename=filename,
            file_type="application/pdf",
            total_pages=1,
            pages=[page0],
            created_at=now
        )

    @staticmethod
    def load_custom_document(
        filename: str = "custom_loan_invoice.pdf",
        invoice_number: str = "INV-2026-9901",
        vendor_name: str = "AtlasOne Lending Partner",
        customer_name: str = "Apex Logistics LLC",
        line_items: Optional[List[Dict[str, Any]]] = None,
        tax_rate: float = 0.18
    ) -> ParsedDocument:
        """
        Dynamically generates a ParsedDocument from custom parameters for live demonstrations.
        """
        doc_id = f"doc_{uuid.uuid4().hex[:10]}"
        now = time.time()
        
        if line_items is None:
            line_items = [
                {"item_index": 1, "description": "Commercial Equipment Lease", "quantity": 2.0, "unit_price": 5000.0, "total_price": 10000.0},
                {"item_index": 2, "description": "Underwriting Platform Fee", "quantity": 1.0, "unit_price": 1500.0, "total_price": 1500.0}
            ]
        
        # Calculate subtotal, tax, and grand total
        subtotal = round(sum(it["total_price"] for it in line_items), 2)
        tax_amount = round(subtotal * tax_rate, 2)
        total_amount = round(subtotal + tax_amount, 2)
        
        table_lines = ["Item | Description | Quantity | Unit Price | Total"]
        for idx, it in enumerate(line_items, 1):
            table_lines.append(f"{idx} | {it['description']} | {int(it['quantity'])} | ${it['unit_price']:,.2f} | ${it['total_price']:,.2f}")
        table_text = "\n".join(table_lines)
        
        blocks = [
            DocumentBlock(
                block_id="b1", page_index=0, block_type=BlockType.HEADER,
                text=f"{vendor_name.upper()} — COMMERCIAL INVOICE",
                bbox=BoundingBox(x0=0.08, y0=0.05, x1=0.65, y1=0.10), confidence=0.99
            ),
            DocumentBlock(
                block_id="b2", page_index=0, block_type=BlockType.KEY_VALUE,
                text=f"Invoice Number: {invoice_number}",
                bbox=BoundingBox(x0=0.68, y0=0.05, x1=0.92, y1=0.08), confidence=0.98,
                metadata={"key": "invoice_number", "value": invoice_number}
            ),
            DocumentBlock(
                block_id="b3", page_index=0, block_type=BlockType.KEY_VALUE,
                text=f"Invoice Date: 2026-09-15",
                bbox=BoundingBox(x0=0.68, y0=0.09, x1=0.92, y1=0.12), confidence=0.98
            ),
            DocumentBlock(
                block_id="b4", page_index=0, block_type=BlockType.KEY_VALUE,
                text=f"Vendor: {vendor_name}",
                bbox=BoundingBox(x0=0.08, y0=0.14, x1=0.48, y1=0.22), confidence=0.97,
                metadata={"key": "vendor_name", "value": vendor_name}
            ),
            DocumentBlock(
                block_id="b5", page_index=0, block_type=BlockType.KEY_VALUE,
                text=f"Customer: {customer_name}",
                bbox=BoundingBox(x0=0.52, y0=0.14, x1=0.92, y1=0.22), confidence=0.97,
                metadata={"key": "customer_name", "value": customer_name}
            ),
            DocumentBlock(
                block_id="b6", page_index=0, block_type=BlockType.TABLE_REGION,
                text=table_text,
                bbox=BoundingBox(x0=0.08, y0=0.26, x1=0.92, y1=0.60), confidence=0.96
            ),
            DocumentBlock(
                block_id="b7", page_index=0, block_type=BlockType.KEY_VALUE,
                text=f"Subtotal: ${subtotal:,.2f}\nTax ({int(tax_rate*100)}%): ${tax_amount:,.2f}\nTotal Amount Due: ${total_amount:,.2f}",
                bbox=BoundingBox(x0=0.55, y0=0.62, x1=0.92, y1=0.75), confidence=0.99,
                metadata={"total_amount": total_amount, "tax_amount": tax_amount}
            )
        ]
        
        raw_text = "\n\n".join(b.text for b in blocks)
        page0 = ParsedPage(page_index=0, width_px=2480, height_px=3508, dpi=300, blocks=blocks, raw_text=raw_text)
        
        return ParsedDocument(
            document_id=doc_id,
            filename=filename,
            file_type="application/pdf",
            total_pages=1,
            pages=[page0],
            created_at=now
        )

document_loader = DocumentLoader()
