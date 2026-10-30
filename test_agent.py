import pytest
from tools import search_product, check_price

def test_search_existing_product():
    result = search_product.invoke({"query": "laptop"})
    assert "P001" in result

def test_check_price_p002():
    result = check_price.invoke({"product_id": "P002"})
    assert "15,000" in result

def test_unknown_product_price():
    result = check_price.invoke({"product_id": "P999"})
    assert "not found" in result.lower()

def test_tool_exception_handled(monkeypatch):
    monkeypatch.setattr("tools.PRODUCTS", None)
    result = check_price.invoke({"product_id": "P001"})
    assert "error" in result.lower()
