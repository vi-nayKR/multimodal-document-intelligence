from src.extractor.gemini_extractor import attach_evidence
from src.parser.real_document_parser import EvidenceCandidate, ParsedArtifact
from src.reconciliation.models import DocumentExtraction, DocumentType, ExtractedLineItem


def test_evidence_is_resolved_from_parser_coordinates():
    parsed = ParsedArtifact(
        text="Invoice INV-22 from Acme. Widget A 2 50 100. Total 100.",
        page_count=1,
        evidence=[
            EvidenceCandidate(page=1, text="Invoice INV-22 from Acme", bbox=(0.1, 0.1, 0.8, 0.2)),
            EvidenceCandidate(page=1, text="Widget A 2 50 100", bbox=(0.1, 0.3, 0.8, 0.4)),
            EvidenceCandidate(page=1, text="Total 100", bbox=(0.6, 0.8, 0.9, 0.9)),
        ],
    )
    extraction = DocumentExtraction(
        document_id="doc-1",
        document_type=DocumentType.INVOICE,
        document_number="INV-22",
        vendor_name="Acme",
        currency="USD",
        line_items=[ExtractedLineItem(description="Widget A", quantity=2, unit_price=50, total_price=100)],
        subtotal=100,
        total_amount=100,
    )

    grounded = attach_evidence(extraction, parsed)
    assert grounded.field_evidence["document_number"].bbox == (0.1, 0.1, 0.8, 0.2)
    assert grounded.line_items[0].evidence.page == 1
    assert not grounded.review_flags
