import re
import uuid
from typing import List, Dict, Any, Optional
from src.table_engine.models import ReconstructedTable
from src.parser.models import DocumentBlock

class TableReconstructor:
    """
    2D Table Structure Recognition & Format Transformation Engine.
    Converts unstructured OCR/Vision table regions into structured matrices, Markdown, and CSV.
    """
    @staticmethod
    def parse_table_block(block: DocumentBlock) -> ReconstructedTable:
        """
        Parses pipe-delimited or tabular text into a ReconstructedTable object.
        """
        lines = [l.strip() for l in block.text.strip().split("\n") if l.strip()]
        if not lines:
            return ReconstructedTable(table_id=f"tbl_{uuid.uuid4().hex[:8]}", page_index=block.page_index)

        # Parse header row
        header_line = lines[0]
        if "|" in header_line:
            headers = [h.strip() for h in header_line.split("|") if h.strip()]
        else:
            headers = [h.strip() for h in re.split(r"\s{2,}", header_line) if h.strip()]

        # Parse data rows
        rows = []
        for line in lines[1:]:
            if "|" in line:
                row = [c.strip() for c in line.split("|") if c.strip()]
            else:
                row = [c.strip() for c in re.split(r"\s{2,}", line) if c.strip()]
            if row:
                rows.append(row)

        return ReconstructedTable(
            table_id=f"tbl_{uuid.uuid4().hex[:8]}",
            page_index=block.page_index,
            headers=headers,
            rows=rows,
            num_rows=len(rows),
            num_cols=len(headers)
        )

    @staticmethod
    def validate_arithmetic(table: ReconstructedTable) -> Dict[str, Any]:
        """
        Scans table rows to verify Quantity * Unit Price == Total arithmetic assertions.
        """
        anomalies = []
        rows_checked = 0

        for idx, row in enumerate(table.rows):
            # Check if row has at least 5 columns (Item, Desc, Qty, Price, Total)
            if len(row) >= 5:
                try:
                    qty_str = re.sub(r"[^\d.]", "", row[2])
                    price_str = re.sub(r"[^\d.]", "", row[3])
                    total_str = re.sub(r"[^\d.]", "", row[4])

                    if qty_str and price_str and total_str:
                        qty = float(qty_str)
                        price = float(price_str)
                        total = float(total_str)
                        rows_checked += 1

                        expected_total = round(qty * price, 2)
                        if abs(expected_total - total) > 0.05:
                            anomalies.append({
                                "row_index": idx + 1,
                                "item": row[1],
                                "expected": expected_total,
                                "actual": total
                            })
                except (ValueError, IndexError):
                    pass

        return {
            "valid": len(anomalies) == 0,
            "rows_checked": rows_checked,
            "anomalies": anomalies
        }

table_reconstructor = TableReconstructor()
