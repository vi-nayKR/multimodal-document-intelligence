import pytest
from src.parser.models import BoundingBox, DocumentBlock, BlockType
from src.parser.document_loader import document_loader
from src.parser.layout_analyzer import layout_analyzer

def test_bounding_box_normalization_and_area():
    bbox = BoundingBox(x0=0.1, y0=0.2, x1=0.5, y1=0.6)
    assert bbox.width == pytest.approx(0.4)
    assert bbox.height == pytest.approx(0.4)
    assert bbox.area == pytest.approx(0.16)

def test_bounding_box_overlap():
    b1 = BoundingBox(x0=0.1, y0=0.1, x1=0.4, y1=0.4)
    b2 = BoundingBox(x0=0.3, y0=0.3, x1=0.6, y1=0.6)
    b3 = BoundingBox(x0=0.7, y0=0.7, x1=0.9, y1=0.9)
    assert b1.overlaps(b2) is True
    assert b1.overlaps(b3) is False

def test_document_loader_ingestion():
    doc = document_loader.load_from_sample("invoice_4092.pdf")
    assert doc.total_pages == 1
    assert len(doc.pages) == 1
    assert len(doc.pages[0].blocks) == 8
    assert "ACME CORP" in doc.pages[0].raw_text

def test_layout_block_classification_and_sorting():
    doc = document_loader.load_from_sample("invoice_4092.pdf")
    page = doc.pages[0]
    
    tables = layout_analyzer.extract_table_regions(page)
    assert len(tables) == 1
    assert "Enterprise Cloud Gateway Node" in tables[0].text
    
    key_values = layout_analyzer.extract_key_values(page)
    assert len(key_values) >= 4
    
    sorted_blocks = layout_analyzer.sort_reading_order(page.blocks)
    assert sorted_blocks[0].block_type == BlockType.HEADER
    assert sorted_blocks[-1].block_type == BlockType.FOOTER
    
    summary = layout_analyzer.get_layout_summary(doc)
    assert summary["has_tables"] is True
    assert summary["total_layout_blocks"] == 8
