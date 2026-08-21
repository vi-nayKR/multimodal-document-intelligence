import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from src.parser.models import ParsedDocument
from src.extractor.schemas import InvoiceExtractionSchema
from config import settings

class FieldVerificationResult(BaseModel):
    field_name: str
    extracted_value: Any
    is_grounded: bool
    confidence: float
    matched_token: Optional[str] = None

class GroundingReport(BaseModel):
    document_id: str
    total_fields: int
    grounded_fields: int
    precision_score: float
    is_fully_grounded: bool
    results: List[FieldVerificationResult] = Field(default_factory=list)
    flagged_fields: List[str] = Field(default_factory=list)

class GroundingShield:
    """
    Deterministic Grounding & Anti-Hallucination Shield.
    Verifies extracted structured fields against source spatial OCR tokens.
    """
    @staticmethod
    def _fuzzy_token_match(target: str, source_text: str) -> float:
        """Computes simple substring / token overlap similarity."""
        target_clean = re.sub(r"[^\w\s]", "", str(target).lower()).strip()
        source_clean = re.sub(r"[^\w\s]", "", str(source_text).lower()).strip()

        if not target_clean:
            return 1.0

        if target_clean in source_clean:
            return 1.00

        # Token set overlap
        target_tokens = set(target_clean.split())
        source_tokens = set(source_clean.split())
        if not target_tokens:
            return 1.0

        overlap = len(target_tokens.intersection(source_tokens))
        return round(overlap / len(target_tokens), 2)

    def verify_invoice(
        self,
        extracted: InvoiceExtractionSchema,
        doc: ParsedDocument,
        threshold: float = settings.CONFIDENCE_THRESHOLD
    ) -> GroundingReport:
        """
        Validates an extracted Invoice against the parsed source document tokens.
        """
        full_source_text = "\n\n".join(p.raw_text for p in doc.pages)
        results = []
        flagged = []

        fields_to_check = [
            ("invoice_number", extracted.invoice_number),
            ("invoice_date", extracted.invoice_date),
            ("vendor_name", extracted.vendor_name),
            ("customer_name", extracted.customer_name),
            ("total_amount", str(extracted.total_amount))
        ]

        # Add line item descriptions
        for idx, item in enumerate(extracted.line_items):
            fields_to_check.append((f"line_item_{idx+1}_desc", item.description))
            fields_to_check.append((f"line_item_{idx+1}_total", str(item.total_price)))

        for field_name, value in fields_to_check:
            score = self._fuzzy_token_match(str(value), full_source_text)
            is_grounded = score >= threshold
            
            results.append(FieldVerificationResult(
                field_name=field_name,
                extracted_value=value,
                is_grounded=is_grounded,
                confidence=score,
                matched_token=str(value) if is_grounded else None
            ))

            if not is_grounded:
                flagged.append(field_name)

        grounded_count = sum(1 for r in results if r.is_grounded)
        total_count = len(results)
        precision = round(grounded_count / max(1, total_count), 3)

        return GroundingReport(
            document_id=doc.document_id,
            total_fields=total_count,
            grounded_fields=grounded_count,
            precision_score=precision,
            is_fully_grounded=len(flagged) == 0,
            results=results,
            flagged_fields=flagged
        )

grounding_shield = GroundingShield()
