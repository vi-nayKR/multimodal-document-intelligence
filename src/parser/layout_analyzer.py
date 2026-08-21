from typing import List, Dict, Any
from src.parser.models import ParsedDocument, ParsedPage, DocumentBlock, BlockType

class LayoutAnalyzer:
    """
    Spatial Layout & Topological Reading Order Analyzer.
    Segments raw OCR/Vision blocks into hierarchical semantic structures and orders them naturally.
    """
    @staticmethod
    def sort_reading_order(blocks: List[DocumentBlock]) -> List[DocumentBlock]:
        """
        Sorts blocks by top-to-bottom vertical bands, then left-to-right columns.
        Uses a vertical quantization bucket of 3% page height.
        """
        def sort_key(block: DocumentBlock):
            y_band = int(block.bbox.y0 * 33.3)  # Quantize into 30 vertical bands
            x_pos = int(block.bbox.x0 * 100)
            return (y_band, x_pos)

        return sorted(blocks, key=sort_key)

    @staticmethod
    def extract_table_regions(page: ParsedPage) -> List[DocumentBlock]:
        """Filters all blocks classified as tabular or data grids."""
        return [b for b in page.blocks if b.block_type == BlockType.TABLE_REGION]

    @staticmethod
    def extract_key_values(page: ParsedPage) -> List[DocumentBlock]:
        """Filters all key-value pair blocks."""
        return [b for b in page.blocks if b.block_type == BlockType.KEY_VALUE]

    @staticmethod
    def get_layout_summary(doc: ParsedDocument) -> Dict[str, Any]:
        """Generates statistical breakdown of document layout elements."""
        total_blocks = sum(len(p.blocks) for p in doc.pages)
        block_types = {}
        for p in doc.pages:
            for b in p.blocks:
                block_types[b.block_type.value] = block_types.get(b.block_type.value, 0) + 1

        return {
            "document_id": doc.document_id,
            "filename": doc.filename,
            "total_pages": doc.total_pages,
            "total_layout_blocks": total_blocks,
            "block_type_breakdown": block_types,
            "has_tables": block_types.get(BlockType.TABLE_REGION.value, 0) > 0
        }

layout_analyzer = LayoutAnalyzer()
