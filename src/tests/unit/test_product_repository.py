import pytest
from app.repository import product_repo


@pytest.mark.asyncio
async def test_get_pioneer_products_success():
    repo = product_repo.ProductRepository()

    result = await repo.get_pioneer_products()

    assert isinstance(result, list)
    assert len(result) > 0
    assert 'name' in result[0] 
    assert 'amount' in result[0]
    assert 'percentage' in result[0] 



@pytest.mark.asyncio
async def test_get_pioneer_products_failure(monkeypatch):
    repo = product_repo.ProductRepository()
    monkeypatch.setattr(product_repo, 'pioneer_products', [])

    result = await repo.get_pioneer_products()

    assert result == []
    