from io import BytesIO

from fastapi.testclient import TestClient

import src.main as main
from src.reconciliation.engine import reconcile_documents
from src.reconciliation.models import DocumentExtraction, DocumentType, ExtractedLineItem
from src.storage import JobStore


def extraction(kind: DocumentType) -> DocumentExtraction:
    return DocumentExtraction(
        document_id=kind.value,
        document_type=kind,
        document_number="INV-1" if kind == DocumentType.INVOICE else "PO-1",
        vendor_name="Acme",
        currency="USD",
        line_items=[ExtractedLineItem(
            sku="A-1",
            description="Widget",
            quantity=1,
            unit_price=10,
            total_price=10,
        )],
        subtotal=10,
        total_amount=10,
    )


def test_health_and_ui(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "store", JobStore(tmp_path / "api.db"))
    client = TestClient(main.app)

    assert client.get("/health").json()["service"] == "ReconcileAI"
    assert "Find the mismatch" in client.get("/").text


def test_upload_rejects_unsupported_files(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "store", JobStore(tmp_path / "api.db"))
    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path / "uploads")
    client = TestClient(main.app)
    response = client.post(
        "/api/v1/jobs",
        files={
            "invoice": ("invoice.txt", BytesIO(b"invoice"), "text/plain"),
            "purchase_order": ("po.pdf", BytesIO(b"pdf"), "application/pdf"),
        },
    )
    assert response.status_code == 415


def test_review_reruns_controls_and_records_audit(tmp_path, monkeypatch):
    store = JobStore(tmp_path / "api.db")
    monkeypatch.setattr(main, "store", store)
    client = TestClient(main.app)
    initial = reconcile_documents(
        extraction(DocumentType.INVOICE),
        extraction(DocumentType.PURCHASE_ORDER),
    )
    store.create("job-review", "invoice.pdf", "po.pdf")
    store.update("job-review", status="completed", result=initial.model_dump(mode="json"))

    invoice = initial.invoice.model_dump(mode="json")
    invoice["line_items"][0]["unit_price"] = 12
    invoice["line_items"][0]["total_price"] = 12
    invoice["subtotal"] = 12
    invoice["total_amount"] = 12
    response = client.put(
        "/api/v1/jobs/job-review/review",
        json={"invoice": invoice, "note": "Corrected invoice row"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["discrepancy_count"] == 2
    audit = payload["reviewer_edits"][0]
    assert audit["note"] == "Corrected invoice row"
    assert audit["sequence"] == 1
    assert audit["before"]["invoice"]["line_items"][0]["unit_price"] == 10
    assert audit["after"]["invoice"]["line_items"][0]["unit_price"] == 12
