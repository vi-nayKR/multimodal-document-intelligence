# Three-minute ReconcileAI demo

## Before presenting

There is no hosted demo. Use the local review workbench with **Open prerecorded sample**, as described in the [README](../README.md). The fictional PDFs and frozen extraction require no provider key. This route demonstrates evidence, corrections and deterministic controls—not live OCR or model quality. The separate Gradio entrypoint is also sample-only and accepts no uploads.

Use the API workbench for correction/reconciliation steps below, not the read-only Gradio sample. If demonstrating fresh uploads instead, configure Docling and a provider key beforehand, label the run as live, and expect latency, failures and cost. Never upload private financial documents for a portfolio demonstration.

For a loopback-only API demo, after installing the README requirements and activating the project's virtual environment:

```bash
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` and choose the prerecorded sample. Unlike `start_server.sh`, this does not bind all network interfaces. Keep real keys and financial documents out of the presentation.

## 60-second architecture explanation

Use this as a standalone explanation, or follow the three-minute demo below. Show the [architecture diagram](architecture.md); do not count both scripts as one three-minute demo.

> ReconcileAI separates document perception from financial checks. FastAPI stores an invoice and purchase order, then Docling parses their text and layout before the configured Gemini extractor receives images and parsed context. Validated records feed deterministic Python matching and monetary controls. Money comparisons use Decimal cent rounding; the model does not decide whether to pay. The workbench shows resolved source regions and review flags. A reviewer can correct extracted JSON and rerun the controls without another model call, while retaining before-and-after records. SQLite stores jobs and results; in-process batch workers stream progress through SSE. Startup reschedules incomplete jobs, so this is single-process recovery, not exactly-once distributed execution. The trade-off is inspectable local review rather than production automation. Our prerecorded demo uses fictional frozen data; receipt field scores and synthetic control checks remain separate evidence.

## Three-minute walkthrough

1. **Problem (20 seconds):** "A plausible extraction is insufficient for accounts-payable review. Reviewers need the source, decimal-exact controls and a correction trail. This is a review aid, not payment authorization."
2. **Sample (20 seconds):** Open the prerecorded invoice and purchase order. The invoice shows ten units at ₹550; the order shows ten at ₹500. Explicitly label the extraction as frozen sample data, not a new Gemini response.
3. **Architecture (25 seconds):** Explain the live path: Docling supplies text and geometry, a model returns typed fields, and deterministic code matches rows and checks amounts. The model does not approve payment. The sample bypasses live extraction.
4. **Finding (35 seconds):** Open the ₹500 price discrepancy. Show expected/actual values, highlight the invoice source row, then switch to purchase-order evidence. Describe this as one fixture demonstration, not measured reconciliation accuracy.
5. **Review (35 seconds):** Open Review JSON, make a deliberate correction, save and show the controls rerun with a review-history entry. Explain that human correction can repair an extraction; it does not retrospectively improve benchmark model scores.
6. **Recorded evaluation (30 seconds):** Open [COMPARISON.md](../results/COMPARISON.md). Say: "On 20 held-out CORD receipts, Gemini/Qwen/Docling-plus-text-LLM recorded 76.03%/65.96%/56.92% field micro-F1. These are receipt field scores, not invoice-pair discrepancy F1." Show Gemini's 28.57% unit-price F1, Qwen's 19/20 completion, and 100% Gemini/Qwen review routing. The 50 synthetic pairs separately verify deterministic controls with labeled extraction.
7. **Engineering close (15 seconds):** Show persisted jobs, source evidence, human correction and the [evidence map](evidence.md). Note that the current scorer can miss wrong row associations and that reduced human-review work has not been demonstrated.

Do not use an unmeasured "30 held-out invoice-pair F1," describe Docling-plus-Gemini as OCR alone, or present configured cost estimates as billed savings. No new model run is needed to explain the committed evidence.
