import asyncio
import time
import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parser.document_loader import document_loader
from src.parser.layout_analyzer import layout_analyzer
from src.extractor.vision_extractor import vision_extractor
from src.table_engine.reconstructor import table_reconstructor
from src.verifier.grounding_shield import grounding_shield

async def process_single_document(doc_id: int) -> Dict[str, Any]:
    start_total = time.perf_counter()

    # 1. Ingest & Spatial Parse
    doc = document_loader.load_from_sample(f"invoice_{doc_id}.pdf")
    page = doc.pages[0]
    
    # 2. Table Structure Recognition
    table_blocks = layout_analyzer.extract_table_regions(page)
    tables = [table_reconstructor.parse_table_block(tb) for tb in table_blocks]
    table_valid = all(table_reconstructor.validate_arithmetic(t)["valid"] for t in tables)

    # 3. Vision LLM Structured Extraction
    extracted = await vision_extractor.extract_invoice(doc)
    
    # 4. Grounding & Anti-Hallucination Verification
    report = grounding_shield.verify_invoice(extracted, doc)
    
    elapsed_ms = (time.perf_counter() - start_total) * 1000.0

    return {
        "doc_id": doc_id,
        "elapsed_ms": round(elapsed_ms, 2),
        "schema_valid": extracted.total_amount > 0,
        "is_grounded": report.is_fully_grounded,
        "precision_score": report.precision_score,
        "table_valid": table_valid,
        "fields_extracted": report.total_fields
    }

async def run_benchmark(concurrency: int = 50):
    print(f"⚡ Launching Document Intelligence Benchmark with {concurrency} concurrent workers...")
    
    start_bench = time.perf_counter()
    tasks = [process_single_document(i) for i in range(1, concurrency + 1)]
    results = await asyncio.gather(*tasks)
    total_time_sec = time.perf_counter() - start_bench

    # Aggregations
    latencies = sorted([r["elapsed_ms"] for r in results])
    schema_success = sum(1 for r in results if r["schema_valid"])
    grounded_success = sum(1 for r in results if r["is_grounded"])
    total_fields = sum(r["fields_extracted"] for r in results)
    
    def p(arr, percentile):
        if not arr: return 0.0
        idx = int(len(arr) * percentile)
        return arr[min(idx, len(arr) - 1)]

    dps = round(len(results) / max(0.001, total_time_sec), 1)

    print("\n" + "=" * 70)
    print("📊 MULTIMODAL DOCUMENT INTELLIGENCE — BENCHMARK RESULTS")
    print("=" * 70)
    print(f"Total Documents Processed:  {len(results)}")
    print(f"Concurrent Workers:         {concurrency}")
    print(f"Schema Compliance Rate:     {schema_success} / {len(results)} ({round(schema_success/len(results)*100, 1)}%)")
    print(f"Grounding Precision Rate:   {round(grounded_success/len(results)*100, 1)}%")
    print(f"Total Fields Extracted:     {total_fields} fields")
    print(f"Throughput (Docs/sec):      {dps} docs/second")
    print("-" * 70)
    print("LATENCY BREAKDOWN (End-to-End Pipeline):")
    print(f"  • Total End-to-End (p50):   {p(latencies, 0.50):.2f} ms")
    print(f"  • Total End-to-End (p95):   {p(latencies, 0.95):.2f} ms")
    print(f"  • Total End-to-End (p99):   {p(latencies, 0.99):.2f} ms")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
