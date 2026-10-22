# ReconcileAI evidence map

A local portfolio prototype for evidence-linked invoice/purchase-order review. Typed model extraction feeds deterministic matching and decimal-based financial controls; a human can correct records and rerun checks. It is not a deployed accounts-payable service or payment authority.

## Three separate evidence scopes

| Scope | Recorded evidence | Supported claim | Not established |
| --- | --- | --- | --- |
| Receipt field extraction | [Comparison](../results/COMPARISON.md), [JSON](../results/real_comparison.json), [CORD manifest](../results/cord_manifest.json) | Seven field types on 40 CORD receipts: 20 development, 20 held-out | End-to-end invoice/PO reconciliation accuracy or correct row association |
| Deterministic controls | [Verification artifact](../results/verification.json), [reconciliation engine](../src/reconciliation/engine.py), [tests](../tests/test_reconciliation.py) | All 50 labeled synthetic pairs pass fixture checks; extraction is labeled/prerecorded | Model perception, live invoice-pair discrepancy F1 or real financial correctness |
| Live invoice/PO path | [API](../src/main.py), [architecture](architecture.md), [paired runner](../scripts/run_reconciliation_eval.py) | An implemented extraction/review workflow and a separate evaluation runner | A completed paired live-quality result; do not invent a 30-pair F1 |

The six-document batch fixture (five completed, one deliberately failed, at most two workers) and two prerecorded sample findings demonstrate API/UI behavior, not model quality. None of these artifacts was regenerated during this documentation cleanup.

## Receipt comparison and failure modes

| Pipeline | Held-out field micro-F1 | Completed | Routed to review |
| --- | --- | --- | --- |
| Gemini vision, `gemini-3.1-flash-lite` | 76.03% | 20/20 | 100% |
| Groq Qwen vision, `qwen/qwen3.8-27b` | 65.96% | 19/20 | 100% |
| Docling OCR + text-only `gemini-3.1-flash-lite` | 56.92% | 20/20 | 85% |

- Both vision adapters also receive actual Docling text. The text baseline is not standalone Docling accuracy.
- Failed receipt extractions contribute missed fields to the field aggregate; the Qwen denominator is not silently reduced to 19 documents.
- Gemini unit-price F1 is 28.57%, well below its overall aggregate. See [field results](../results/COMPARISON.md), [error analysis](../ERROR_ANALYSIS.md) and [selected visual adjudications](../results/error_review.json).
- Scoring uses normalized value multisets per document. Correct values attached to the wrong row can still receive credit. The paired discrepancy scorer also counts discrepancy types without identifying the correct affected row; its quality rates cover completed cases, with failures separate.
- Gemini/Qwen review every held-out receipt, so no reduced review workload is demonstrated. CORD lacks required invoice/vendor headers and contains receipt-specific layouts; this routing rate is not a forecast for real invoices. The text baseline's 85% review rate is not a safety win: the recorded accepted-document accuracy is 0.0.
- Confidence is an evidence text-match heuristic, not a calibrated probability. Development-only threshold selection did not achieve its 20% review target. Do not lower mandatory safety flags or tune on the held-out set to advertise automation.

## Provenance and reproduction boundaries

CORD is attributed to Park et al. under CC BY 4.0. The [frozen manifest](../results/cord_manifest.json) records selected sources/checksums; dataset images and raw provider responses are not committed. Label-preparation corrections preserve the previous manifest and mark affected diagnostic judgments stale rather than silently rewriting scores.

The same `gemini-3.1-flash-lite` model performs extraction and diagnostic judging. Its diagnoses may share extractor errors; label-based F1 does not depend on the judge. Selected visual checks are diagnostic evidence, not a claim that every failure was independently adjudicated.

[Cost and usage records](../results/COMPARISON.md), [model-selection history](../results/model_selection.json) and [provider catalogue](../results/provider_catalog.json) preserve run metadata, model IDs and configured prices. Free-tier and paid-equivalent token costs are estimates, not billing receipts or measured business savings. Cached predictions can be rescored without fresh calls, but report-writing commands can overwrite published artifacts; use a separate experiment copy.

## Presentation and remaining work

Use the [three-minute demo](demo-script.md) and [claim boundaries](../results/CLAIMS.md). The sample-only demo is local; a deployment script is not a hosted deployment.

Row-aware field/discrepancy scoring and a new untouched end-to-end paired evaluation remain future work, not results of this documentation cleanup. The supported story is evidence-linked review, deterministic control engineering and an honestly bounded receipt comparison.
