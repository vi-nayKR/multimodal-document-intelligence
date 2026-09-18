"""Run the real ReconcileAI pipeline over a generated benchmark split."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.extractor.gemini_extractor import GeminiDocumentExtractor  # noqa: E402
from src.parser.real_document_parser import parse_document  # noqa: E402
from src.reconciliation.engine import reconcile_documents  # noqa: E402
from src.reconciliation.models import DocumentType  # noqa: E402

DATA = ROOT / "evals" / "generated"


async def evaluate_case(case: dict) -> dict:
    started = time.perf_counter()
    invoice_path = DATA / case["invoice"]
    po_path = DATA / case["purchase_order"]
    invoice_parsed, po_parsed = await asyncio.gather(parse_document(invoice_path), parse_document(po_path))
    extractor = GeminiDocumentExtractor()
    invoice, po = await asyncio.gather(
        extractor.extract(invoice_path, f"{case['case_id']}_invoice", DocumentType.INVOICE, invoice_parsed),
        extractor.extract(po_path, f"{case['case_id']}_po", DocumentType.PURCHASE_ORDER, po_parsed),
    )
    result = reconcile_documents(invoice, po)
    predicted = {item.type.value for item in result.discrepancies}
    expected = set(case["expected_discrepancies"])
    return {
        "case_id": case["case_id"],
        "expected": sorted(expected),
        "predicted": sorted(predicted),
        "true_positives": len(predicted & expected),
        "false_positives": len(predicted - expected),
        "false_negatives": len(expected - predicted),
        "review_required": result.summary.status == "review_required",
        "latency_seconds": round(time.perf_counter() - started, 3),
    }


async def main(split: str) -> None:
    manifest_path = DATA / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit("Run scripts/generate_benchmark.py first")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = [case for case in manifest["cases"] if case["split"] == split]
    results = []
    for index, case in enumerate(cases, 1):
        print(f"[{index}/{len(cases)}] {case['case_id']}")
        results.append(await evaluate_case(case))
    tp = sum(row["true_positives"] for row in results)
    fp = sum(row["false_positives"] for row in results)
    fn = sum(row["false_negatives"] for row in results)
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    report = {
        "benchmark": manifest["name"],
        "version": manifest["version"],
        "split": split,
        "cases": len(results),
        "discrepancy_precision": round(precision, 4),
        "discrepancy_recall": round(recall, 4),
        "discrepancy_f1": round(f1, 4),
        "review_rate": round(sum(row["review_required"] for row in results) / len(results), 4),
        "average_latency_seconds": round(sum(row["latency_seconds"] for row in results) / len(results), 3),
        "results": results,
    }
    report_dir = ROOT / "evals" / "reports"
    report_dir.mkdir(exist_ok=True)
    target = report_dir / f"{split}.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("development", "held_out"), default="held_out")
    args = parser.parse_args()
    asyncio.run(main(args.split))
