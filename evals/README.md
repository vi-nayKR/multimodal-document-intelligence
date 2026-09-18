# ReconcileAI evaluation

The benchmark is generated locally so every document and label is reproducible.

```bash
python scripts/generate_benchmark.py
python scripts/run_reconciliation_eval.py --split held_out
```

The generator creates 50 invoice/purchase-order pairs: 20 development cases and 30 held-out cases. Held-out cases use different layouts. Generated PDFs live under `evals/generated/` and are ignored; `manifest.json` records ground truth and seeds.

The live runner reports discrepancy precision, recall and F1, review rate and latency. It requires `GEMINI_API_KEY` and stays separate from deterministic CI.
