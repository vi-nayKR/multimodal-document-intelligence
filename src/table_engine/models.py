from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TableCell(BaseModel):
    row_idx: int
    col_idx: int
    text: str
    row_span: int = 1
    col_span: int = 1
    is_header: bool = False
    numeric_value: Optional[float] = None

class TableRow(BaseModel):
    row_idx: int
    cells: List[TableCell] = Field(default_factory=list)

class ReconstructedTable(BaseModel):
    table_id: str
    page_index: int
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    num_rows: int = 0
    num_cols: int = 0

    def to_markdown(self) -> str:
        """Converts the reconstructed table into GitHub Flavored Markdown."""
        if not self.headers:
            return ""
        
        md_lines = []
        md_lines.append("| " + " | ".join(self.headers) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(self.headers)) + " |")
        
        for row in self.rows:
            # Pad row if columns are missing
            padded_row = row + [""] * (len(self.headers) - len(row))
            md_lines.append("| " + " | ".join(padded_row[:len(self.headers)]) + " |")
            
        return "\n".join(md_lines)

    def to_csv(self) -> str:
        """Converts the reconstructed table into RFC-4180 CSV string."""
        lines = [",".join(f'"{h}"' if "," in h else h for h in self.headers)]
        for row in self.rows:
            lines.append(",".join(f'"{c}"' if "," in c else c for c in row))
        return "\n".join(lines)
