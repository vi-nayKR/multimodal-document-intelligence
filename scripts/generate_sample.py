"""Regenerate the fictional, prerecorded sample shown in the workbench."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.generate_benchmark import draw_document  # noqa: E402
from src.reconciliation.engine import reconcile_documents  # noqa: E402
from src.reconciliation.models import (  # noqa: E402
    DocumentExtraction, DocumentType, EvidenceReference, ExtractedLineItem,
)

OUTPUT = ROOT / "demo"


def document(kind: DocumentType, price: float) -> DocumentExtraction:
    name = "invoice" if kind == DocumentType.INVOICE else "purchase_order"
    evidence = EvidenceReference(
        document_id=f"sample_{name}", page=1,
        text=f"SKU-42 Network appliance 10 {price:.2f} {price * 10:.2f}",
        bbox=(0.08, 0.21, 0.91, 0.24), confidence=1,
    )
    return DocumentExtraction(
        document_id=f"sample_{name}", document_type=kind,
        document_number="INV-SAMPLE" if kind == DocumentType.INVOICE else "PO-SAMPLE",
        vendor_name="Kaveri Network Systems", buyer_name="Meridian Operations Pvt Ltd",
        currency="INR", line_items=[ExtractedLineItem(
            sku="SKU-42", description="Network appliance", quantity=10,
            unit_price=price, total_price=price * 10, evidence=evidence,
        )], subtotal=price * 10, total_amount=price * 10,
    )


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    invoice = document(DocumentType.INVOICE, 550)
    po = document(DocumentType.PURCHASE_ORDER, 500)
    for record in (invoice, po):
        name = record.document_type.value
        draw_document(
            OUTPUT / f"{name}.pdf", name.replace("_", " ").upper(),
            record.document_number,
            [{"sku": item.sku, "description": item.description,
              "quantity": item.quantity, "unit_price": item.unit_price,
              "total_price": item.total_price} for item in record.line_items],
            layout=3,
        )
    result = reconcile_documents(invoice, po).model_dump(mode="json")
    for index, discrepancy in enumerate(result["discrepancies"], start=1):
        discrepancy["discrepancy_id"] = f"sample_{index}"
    (OUTPUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
