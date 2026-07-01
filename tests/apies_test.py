import pytest
from httpx import AsyncClient, ASGITransport
from API_SCHEMAS.main import some, app
from API_SCHEMAS.api import price_list, creating_item, patching
from API_SCHEMAS.database.models import Item
from API_SCHEMAS.models import Creating_Item, Update_Item
from sqlalchemy import select

async def test_some():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as conch:
        result = await conch.get('/') 
        assert result.status_code == 200
        assert isinstance(result.json(), list) 


async def test_creating_item(test_db):
    it = Creating_Item(url='https://www.example.com', name='sobaka', need_price=200, shop='wb')
    result = await creating_item(item=it, ses=test_db)
    await test_db.commit()
    s = select(Item)
    query = await test_db.execute(s)

    assert result is not None
    assert query is not None


async def test_patching(test_db):
    it = Creating_Item(url='https://www.example.com', name='sobaka', need_price=200, shop='wb')
    result = await creating_item(item=it, ses=test_db)
    await test_db.commit()
    data = Update_Item(name='loh')
    await patching(id=1, data=data, ses=test_db)
    query = await test_db.get(Item, 1)

    assert query.name == data.name





