# Phase 6: Production-Grade Interactive Web Console & Master Architecture

---

## 1. Overview & Objective

In modern document intelligence workflows, business users and software engineers require an **interactive visual audit console** to inspect document extractions in real-time.
- Visual inspection allows users to hover over extracted JSON keys and immediately see the corresponding **2D bounding box highlighted on the original document scan**.
- Provides instant toggle views between strictly validated Pydantic JSON, reconstructed Markdown tables, raw CSV exports, and deterministic grounding shield reports.

**Phase 6 Goal:** Build and deploy a **Production-Grade OpenAI-Standard Interactive Web Console** (`ui/index.html`) mounted on FastAPI to deliver:
- **Split-Screen Workspace:** Interactive document canvas on the left with rendered spatial bounding boxes + Extracted structured data viewer on the right.
- **Multi-Format Tab Viewers:** Live switching between `JSON Schema`, `Markdown Table`, `CSV Export`, and `Grounding Shield Report`.
- **Pre-Loaded Enterprise Document Presets:** Instant 1-click testing on commercial invoices, financial statements, and compliance receipts.
- **FastAPI Endpoints:** Complete REST API supporting `/v1/extract`, `/v1/layout`, `/v1/table`, and `/health`.

---

## 2. Web Console Architecture & Component Hierarchy

```

 MULTIMODAL DOCUMENT INTELLIGENCE CONSOLE 

 LEFT PANE: Spatial Document Canvas RIGHT PANE: Structured Data Viewer 

 • Visual Document Scan Preview • Tabs: [ JSON | Table | Grounding] 
 • Color-Coded Bounding Boxes: • Strictly Validated Pydantic Schema
 [🟩 Header: INV-2026-8891] • Verified Totals & Tax Math 
 [🟦 Key-Value: Vendor/Customer] • Grounding Badge: 100% GROUNDED 
 [🟨 Table Region: 3 Line Items] • One-Click CSV / Markdown Download 
 
 • Preset Document Selector: • Telemetry HUD: 
 (Tax Invoice, Balance Sheet) Latency: 51ms | Confidence: 0.985 

```

---

## 3. Step-by-Step Code Walkthrough

### Step 1: Frontend Single-File Dashboard (`ui/index.html`)
- Built with **Tailwind CSS** following the OpenAI dark theme design system (`#212121` background, `#171717` sidebar, `#10a37f` emerald highlights).
- Implements interactive SVG bounding box overlays mapping normalized coordinates $(x_0, y_0, x_1, y_1)$ onto document preview elements.
- Provides real-time tabs for JSON view with syntax highlighting, Markdown rendered tables, and Grounding Shield verification checklists.

### Step 2: FastAPI Server Integration (`src/main.py`)
- Mounts web console at `GET /`.
- Exposes `/v1/extract` for multipart document uploads and automated Pydantic extraction.
- Exposes `/v1/layout` for raw bounding box and spatial block queries.

---

## 4. How to Run & Experience Phase 6

### 1. Launch the Server:
```bash
./start_server.sh
# or: ./.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open Your Browser:
Open [**http://localhost:8000**](http://localhost:8000) to access the interactive document intelligence console!

### 3. Test Interactive Workflows:
- Click **"Load Sample Tax Invoice"** $\rightarrow$ observe instant spatial bounding boxes on the document scan.
- Switch to the **"Reconstructed Table"** tab $\rightarrow$ view formatted Markdown and CSV exports with verified line item arithmetic.
- Switch to the **"Grounding Report"** tab $\rightarrow$ verify 100% match against raw OCR tokens.

---

## 5. Technical Questions & Architectural Explanations

### Q: How does coordinate bounding box mapping improve human-in-the-loop (HITL) review efficiency?
> **Answer:** When an automated system flags a low-confidence field (e.g. `confidence < 0.85`), requiring human reviewers to search through a multi-page document manually takes 30–60 seconds per field. By projecting spatial bounding box coordinates directly onto the document canvas, reviewers can instantly pinpoint the source text in $<2\text{ seconds}$, accelerating review speed by over $15\times$.
