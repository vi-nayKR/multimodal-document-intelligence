# Phase 4: Hallucination & Accuracy Grounding Shield

---

## 1. Overview & Objective

Large Language Models are prone to **hallucinating facts, inventing invoice numbers, or silently modifying numerical values** when generating structured outputs.
- In production financial and legal workflows, an ungrounded hallucination in a balance sheet or invoice total creates severe compliance liabilities.
- Relying on model self-confidence scores is insufficient, as generative models can produce confident hallucinations.

**Phase 4 Goal:** Implement a deterministic **Grounding & Accuracy Verification Shield** that:
1. Cross-checks every extracted key-value pair and tabular number back against the **ground-truth spatial OCR tokens**.
2. Calculates **token similarity ratios** (using normalized Levenshtein token distance) for every field.
3. Computes an aggregate **Document Precision Score** ($0.0 - 1.0$) and flags ungrounded fields for human-in-the-loop review.

---

## 2. Deterministic Grounding Verification Flow

```

 DETERMINISTIC GROUNDING SHIELD FLOW 

 Extracted Pydantic Schema [ Spatial Token Cross-Matcher ] OCR Tokens
 
 
 [ Normalized Similarity Evaluator ] 
 
 
 
 GROUNDED (Match >= 0.85) UNGROUNDED / FLAGGED
 (Field Confirmed in Source Doc) (Potential Hallucination) 

```

### A. Normalized Token Similarity Formula
Given an extracted field string $S_{\text{ext}}$ and candidate OCR tokens $S_{\text{ocr}}$:
$$\text{Similarity}(S_{\text{ext}}, S_{\text{ocr}}) = 1.0 - \frac{\text{Levenshtein Distance}(S_{\text{ext}}, S_{\text{ocr}})}{\max(\text{len}(S_{\text{ext}}), \text{len}(S_{\text{ocr}}))}$$

---

## 3. Step-by-Step Code Walkthrough

### Step 1: Verification Data Models (`src/verifier/grounding_shield.py`)
- `FieldVerificationResult`: Individual field outcome (`field_name`, `extracted_value`, `is_grounded`, `confidence`, `matched_ocr_token`).
- `GroundingReport`: Aggregate assessment with total fields evaluated, grounded field count, flagged anomalies, and document precision score.

### Step 2: Verification Engine (`GroundingShield`)
- Iterates over all scalar keys and line item fields in the extracted schema.
- Searches for corresponding substring or fuzzy match within raw document page texts.
- Flags any value missing from raw source tokens with `is_grounded: False`.

---

## 4. How to Run & Verify Phase 4

### Command:
```bash
./.venv/bin/pytest tests/test_grounding.py
```

### Expected Output:
```text
============================== 3 passed in 0.04s ==============================
```

### What the Tests Verify:
1. `test_grounded_invoice_extraction`: Confirms authentic extracted fields score $\ge 0.95$ precision.
2. `test_hallucination_detection`: Injects fabricated invoice numbers and asserts the shield flags them as ungrounded.
3. `test_overall_precision_calculation`: Validates aggregate precision calculations across mixed field states.

---

## 5. Technical Questions & Architectural Explanations

### Q: Why verify extracted fields against raw OCR tokens rather than asking the LLM to verify its own output?
> **Answer:** LLM self-verification suffers from correlated cognitive errors—if an LLM hallucinated a number during generation, asking the same model to verify its response frequently results in repeated confirmation of the hallucinated value. A deterministic string-matching shield against spatial OCR tokens operates as an independent, deterministic arbiter with zero hallucination risk.
