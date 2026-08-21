# Phase 1: Document Ingestion, Spatial OCR & Layout Analysis

---

## 1. Overview & Objective

Enterprise documents (invoices, financial statements, contracts, tax filings, medical reports) present complex **2D spatial structures** that traditional sequential OCR and plain-text extractors fail to parse accurately.
- Standard OCR linearizes text into unstructured strings, destroying column layouts, table cell associations, and key-value spatial pairings.
- Complex multi-page documents require preserving **exact coordinate bounding boxes ($x_0, y_0, x_1, y_1$)**, reading order heuristics, and semantic block classification (headers, key-value fields, tables, footers).

**Phase 1 Goal:** Build a high-performance **Multi-Page Document Ingestion & Spatial Layout Analysis Engine** that:
1. Normalizes multi-format documents (PDFs, TIFFs, PNGs, JPEGs) into canonical page image representations.
2. Extracts hierarchical spatial bounding boxes with normalized coordinates ($0.0 - 1.0$).
3. Reconstructs multi-column reading orders and classifies blocks into `HEADER`, `PARAGRAPH`, `TABLE_REGION`, `KEY_VALUE_PAIR`, and `METADATA`.

---

## 2. Spatial Coordinate System & Layout Classification

```

 SPATIAL BOUNDING BOX NORMALIZATION 

 (0.0, 0.0) (1.0, 0.0) 
 
 
 [HEADER] Invoice #4092 [METADATA] Date: 08/21 
 (x0, y0, x1, y1) (x0, y0, x1, y1) 
 
 
 
 [TABLE_REGION] Line Items & Tax Subtotals 
 Merged Cells | 2D Spatial Cell Coordinates 
 
 
 (0.0, 1.0) (1.0, 1.0) 

```

### A. Coordinate Normalization
Given page pixel width $W$ and height $H$, raw pixel coordinates $(X_0, Y_0, X_1, Y_1)$ are transformed into scale-invariant normalized coordinates:
$$x_0 = \frac{X_0}{W}, \quad y_0 = \frac{Y_0}{H}, \quad x_1 = \frac{X_1}{W}, \quad y_1 = \frac{Y_1}{H}$$

This ensures layout models and Vision LLMs can reason over relative document positions regardless of varying DPI resolutions.

### B. Multi-Column Reading Order Sorting
Topological sorting heuristic orders blocks by vertical band ($Y$) and horizontal flow ($X$):
$$\text{Sort Key}(B) = \lfloor y_0 \times 100 \rfloor \times 1000 + \lfloor x_0 \times 100 \rfloor$$

---

## 3. Step-by-Step Code Walkthrough

### Step 1: Spatial Data Models (`src/parser/models.py`)
- `BoundingBox`: Normalized rectangular coordinates with area and overlap calculation utilities.
- `DocumentBlock`: Single semantic unit containing text content, bounding box, block type, confidence score, and page index.
- `ParsedDocument`: Container holding all document pages, total token counts, and structured layout blocks.

### Step 2: Multi-Page Document Loader (`src/parser/document_loader.py`)
- Ingests raw byte streams, base64 payloads, and files.
- Extracts document metadata, computes MD5 content hashes, and detects page dimensions.

### Step 3: Layout Analysis Engine (`src/parser/layout_analyzer.py`)
- Identifies spatial hierarchies (Headers, Key-Value pairs, Table boundaries).
- Constructs topological reading order graphs, eliminating left-to-right scanning errors on multi-column pages.

---

## 4. How to Run & Verify Phase 1

### Command:
```bash
./.venv/bin/pytest tests/test_parser.py
```

### Expected Output:
```text
============================== 4 passed in 0.05s ==============================
```

### What the Tests Verify:
1. `test_bounding_box_normalization`: Asserts coordinates scale to $[0.0, 1.0]$ bounds.
2. `test_document_loader_ingestion`: Ingests simulated multi-page invoice payloads.
3. `test_layout_block_classification`: Confirms accurate classification of headers, key-value pairs, and table blocks.
4. `test_reading_order_sorting`: Verifies multi-column document blocks sort correctly from top-to-bottom and left-to-right.

---

## 5. Technical Questions & Architectural Explanations

### Q: Why normalize bounding boxes to relative [0.0, 1.0] coordinates instead of using raw pixel coordinates?
> **Answer:** Scanned enterprise documents arrive at vastly different resolutions (e.g. 72 DPI mobile camera scans vs 300 DPI flatbed industrial scans). Normalizing all spatial coordinates into a unit scale ($[0.0, 1.0]$) decouples document layout geometry from physical pixel density, allowing Vision LLMs and spatial downstream extractors to evaluate relative positions uniformly.
