# Phase 3: Complex Table Reconstruction, Merged Cells & Markdown/CSV Exporter

---

## 1. Overview & Objective

Tabular data in business documents (e.g. multi-line purchase orders, financial income statements, fee schedules) represents the **highest error-rate category** in automated document processing.
- Naive extractors flatten tables into unstructured strings, merging neighboring columns and failing to detect merged header cells (e.g. `Q1 2026 | Q2 2026` spanning across sub-columns).
- Downstream business intelligence and automated reconciliation workflows require **clean 2D tabular matrices, Markdown tables for LLM reasoning, and CSV exports for ERP ingestion**.

**Phase 3 Goal:** Implement a **2D Table Reconstruction & Structural Recognition Engine** that:
1. Identifies table header rows, data rows, and summary footer rows.
2. Resolves multi-column cell alignments and preserves row/column index relationships.
3. Automatically executes arithmetic consistency checks (e.g. $\sum (\text{Qty} \times \text{Price}) == \text{Subtotal}$).
4. Exports structured tables into **Markdown tables**, **CSV strings**, and **typed JSON matrices**.

---

## 2. 2D Table Grid Reconstruction Architecture

```

 TABLE STRUCTURE RECONSTRUCTION 

 Raw Table Block [ Row/Column Grid Segmentation ] 
 
 
 [ 2D Cell Matrix (Row x Col) ] 
 
 
 
 [ Markdown Exporter ] [ CSV Exporter ] [ Arithmetic Cross-Check ] 
 | Col1 | Col2 | Col3 | Col1,Col2,Col3 Qty * Price == Total 
 |------|------|------| Val1,Val2,Val3 Sum(Totals) == Subtotal 

```

---

## 3. Step-by-Step Code Walkthrough

### Step 1: Table Data Models (`src/table_engine/models.py`)
- `TableCell`: Contains `row_idx`, `col_idx`, `row_span`, `col_span`, `text`, and optional `numeric_value`.
- `TableRow`: List of cells forming a horizontal row.
- `ReconstructedTable`: Container with headers, rows, row count, column count, and export utilities.

### Step 2: Table Reconstructor (`src/table_engine/reconstructor.py`)
- **`from_text_block(block)`:** Parses delimited or whitespace-separated table strings into normalized 2D matrices.
- **`to_markdown()`:** Generates clean GitHub Flavored Markdown tables.
- **`to_csv()`:** Produces RFC-4180 compliant CSV strings.
- **`validate_arithmetic()`:** Performs sanity cross-checks on numeric columns.

---

## 4. How to Run & Verify Phase 3

### Command:
```bash
./.venv/bin/pytest tests/test_table_engine.py
```

### Expected Output:
```text
============================== 4 passed in 0.05s ==============================
```

### What the Tests Verify:
1. `test_table_matrix_construction`: Verifies row and column counts from sample table blocks.
2. `test_markdown_export`: Asserts table formats into valid markdown table syntax.
3. `test_csv_export`: Asserts table converts into comma-separated CSV with header rows.
4. `test_arithmetic_cross_check`: Confirms line item math validation flags anomalies accurately.

---

## 5. Technical Questions & Architectural Explanations

### Q: Why is Markdown table representation preferred over raw JSON when passing tables to LLMs?
> **Answer:** Markdown tables maintain clear visual row and column delimiters (`| --- |`) that align naturally with LLM pretraining data. In empirical evaluations, LLMs perform significantly better at numerical reasoning and cross-column comparisons when tables are presented as Markdown tables rather than deeply nested JSON objects, while consuming fewer tokens.
