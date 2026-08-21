# 📘 Phase 2: Vision LLM Extraction & Pydantic Schema Enforcement

---

## 🎯 1. Overview & Objective

Unstructured LLM text outputs frequently suffer from **schema drift, missing required fields, and non-deterministic formatting** when parsing high-stakes enterprise documents.
- In financial, legal, and compliance workflows, downstream ERP and ledger systems require **100% strictly typed JSON schemas**.
- Vision Language Models (GPT-4o Vision, Claude 3.5 Sonnet, Qwen2-VL) process visual document images simultaneously with OCR tokens, preserving visual cues (e.g. bolded headers, checkmarks, stamps, line boundaries).

**Phase 2 Goal:** Implement a **Vision-Driven Structured Extraction Pipeline** that:
1. Translates document visual tokens and layout blocks into strictly validated **Pydantic Domain Schemas** (`InvoiceExtractionSchema`, `FinancialBalanceSheetSchema`, `KYCDocumentSchema`).
2. Enforces mandatory field typing, regex validations (e.g. ISO-8601 dates, currency symbols, tax IDs), and arithmetic cross-field assertions.
3. Automatically computes extraction confidence scores and flags validation discrepancies.

---

## 📐 2. Vision Extraction & Schema Enforcement Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VISION LLM EXTRACTION & VALIDATION FLOW                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Document Page (Image / PDF) ──► [ Multimodal Vision Encoder ]              │
│                                           │                                 │
│                                           ▼                                 │
│                           [ Guided JSON Schema Prompt ]                     │
│                                           │                                 │
│                                           ▼                                 │
│                           [ Raw Vision LLM Completion ]                     │
│                                           │                                 │
│                                           ▼                                 │
│                      [ Pydantic Runtime Schema Validator ]                  │
│                                           │                                 │
│                    ┌──────────────────────┴──────────────────────┐          │
│                    ▼                                             ▼          │
│          ✓ VALID SCHEMA ENFORCED                       ❌ SCHEMA VIOLATION   │
│     (Typed Object + Confidence: 0.98)             (Auto-Repair / Flag)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 3. Step-by-Step Code Walkthrough

### Step 1: Enterprise Pydantic Domain Schemas (`src/extractor/schemas.py`)
- **`LineItemSchema`:** `item_index`, `description`, `quantity`, `unit_price`, `total_price` with non-negative validators.
- **`InvoiceExtractionSchema`:** `invoice_number`, `invoice_date`, `vendor_name`, `customer_name`, `line_items`, `subtotal`, `tax_amount`, `total_amount`, and currency code.
- **`FinancialBalanceSheetSchema`:** Assets, liabilities, equity, and fiscal period validations.

### Step 2: Vision Extractor Engine (`src/extractor/vision_extractor.py`)
- Connects to multimodal vision models (GPT-4o Vision, Qwen2-VL, Claude 3.5).
- Parses structured responses, executes Pydantic model validation, and assigns field-level extraction confidence scores.

---

## 🧪 4. How to Run & Verify Phase 2

### Command:
```bash
./.venv/bin/pytest tests/test_extractor.py
```

### Expected Output:
```text
============================== 4 passed in 0.05s ==============================
```

### What the Tests Verify:
1. `test_invoice_schema_validation`: Confirms strict Pydantic parsing of invoice headers and line items.
2. `test_line_item_arithmetic_consistency`: Validates that subtotal matches line items sum.
3. `test_invalid_schema_rejection`: Proves missing required fields trigger validation errors.
4. `test_vision_extractor_end_to_end`: Tests full pipeline extraction from parsed document blocks.

---

## 💡 5. Technical Questions & Architectural Explanations

### Q: Why combine spatial OCR layout with Vision LLM visual features rather than relying on Vision LLM images alone?
> **Answer:** Pure vision-based models often suffer from subtle character errors on small fonts (e.g. misreading `8` as `B`, or dropping decimal places in `10,620.00`). By fusing spatial OCR bounding boxes with visual embeddings, the extractor grounds text tokens in exact 2D coordinates while using visual features to understand multi-level tables, visual stamps, and checkmarks.
