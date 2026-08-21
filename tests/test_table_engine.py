import pytest
from src.table_engine.models import ReconstructedTable
from src.table_engine.reconstructor import table_reconstructor
from src.parser.document_loader import document_loader
from src.parser.layout_analyzer import layout_analyzer

def test_table_matrix_construction():
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    table_block = layout_analyzer.extract_table_regions(doc.pages[0])[0]
    
    table = table_reconstructor.parse_table_block(table_block)
    assert table.num_rows == 3
    assert table.num_cols == 5
    assert "Description" in table.headers
    assert "Unit Price" in table.headers

def test_markdown_export():
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    table_block = layout_analyzer.extract_table_regions(doc.pages[0])[0]
    table = table_reconstructor.parse_table_block(table_block)
    
    md = table.to_markdown()
    assert "| Item | Description | Quantity | Unit Price | Total |" in md
    assert "| --- | --- | --- | --- | --- |" in md
    assert "Enterprise Cloud Gateway Node" in md

def test_csv_export():
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    table_block = layout_analyzer.extract_table_regions(doc.pages[0])[0]
    table = table_reconstructor.parse_table_block(table_block)
    
    csv_str = table.to_csv()
    assert "Item,Description,Quantity,Unit Price,Total" in csv_str
    assert "Redis 8 Vector Cache License" in csv_str

def test_arithmetic_cross_check():
    doc = document_loader.load_from_sample("sample_invoice.pdf")
    table_block = layout_analyzer.extract_table_regions(doc.pages[0])[0]
    table = table_reconstructor.parse_table_block(table_block)
    
    check = table_reconstructor.validate_arithmetic(table)
    assert check["valid"] is True
    assert check["rows_checked"] == 3
    assert len(check["anomalies"]) == 0
