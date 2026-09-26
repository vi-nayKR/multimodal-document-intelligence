# ReconcileAI evaluation

The benchmark is generated locally so every document and label is reproducible. The committed `benchmark_v1.1.0_manifest.json` freezes case IDs, splits, scenarios, and labels; the live runner rejects a changed generated manifest.

```bash
python scripts/generate_benchmark.py
python scripts/run_reconciliation_eval.py --split held_out
```

The generator creates 50 invoice/purchase-order pairs: 20 development cases and 30 held-out cases. Held-out cases use different layouts. Generated PDFs live under `evals/generated/` and are ignored; `manifest.json` records ground truth and seeds.

The live runner requires `GEMINI_API_KEY` and stays separate from deterministic CI. Benchmark version 1.1.0 retains the same split and scenarios and adds row-value and expected row-position labels. The report records duplicate discrepancy types as counts, exact extracted row values, evidence row placement, failures, review rate, latency, provider metadata, dataset hash, and commit. Discrepancy scoring still compares types without identifying which row caused each finding, and the documents are synthetic and simple. Quality rates cover completed cases only; failed cases are counted separately. No live-provider result is committed yet.
