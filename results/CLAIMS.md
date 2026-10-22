# Supported claims and boundaries

Numeric sources: [real_comparison.json](real_comparison.json), [COMPARISON.md](COMPARISON.md) and [verification.json](verification.json). These are recorded artifacts, not measurements rerun during documentation cleanup.

## Supported by the committed evidence

- Compared Gemini `gemini-3.1-flash-lite`, Groq `qwen/qwen3.8-27b` and Docling OCR plus text-only Gemini on 40 public CORD receipts (20 development, 20 held-out). Recorded held-out field micro-F1: 76.03%, 65.96%, 56.92% across seven field types. Failed documents contribute missed fields; Qwen completed 19/20 held-out documents.
- Built invoice/PO reconciliation with deterministic controls verified against 50 labeled synthetic pairs across four scenarios. Those checks use labeled/prerecorded extraction, not a live model.
- Added persistent batch processing with SSE progress, verified with a six-document stub fixture, and a local no-key PDF review demo highlighting two precomputed findings.

## Required qualifications

- Receipt field F1 is not invoice/PO discrepancy F1, correct row association, payment accuracy or a production outcome. No completed 30-held-out-pair live-quality result is claimed.
- Gemini unit-price F1 is 28.57%. Both vision pipelines route 100% of held-out receipts to review; reduced manual-review work is unproven. The text baseline routes 85%, but its recorded accepted-document accuracy is 0.0.
- Docling-plus-text-LLM is not standalone OCR; both vision pipelines also receive parsed Docling text. The scorer matches normalized values per document and can miss incorrect line-item associations.
- Confidence is a heuristic, not a calibrated probability. The same-model diagnostic judge cannot independently validate extraction; diagnoses do not determine field F1.
- Token costs are configured estimates, not billing receipts or measured savings. The sample-only demo is local, not a deployed production document-AI service.

See the [evidence map](../docs/evidence.md) for implementation links, attribution, correction history and unmeasured work. Do not combine these separate evaluation scopes into a single headline accuracy or automation rate.
