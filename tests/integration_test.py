import pytest
from . import rabbit_container, RabbitMqContainer, request_to_test_server_without_mock, AsyncClient, get_auth_token, Cookies, AsyncSession
from API_SCHEMAS import CreatingItem
from checker import Item_Checker
from sqlalchemy import select


@pytest.mark.integration
async def test_api_checker_connection(
        rabbit_container: RabbitMqContainer,
        request_to_test_server_without_mock: AsyncClient,
        get_auth_token: Cookies, 
        test_db_api: AsyncSession, 
        test_db_checker: AsyncSession):
        

        payload = CreatingItem(url='https://google.com', name='GTA 6', need_price=200, shop='wb')

        res = await request_to_test_server_without_mock.post(url='/create_item', cookies=get_auth_token, json=payload.model_dump(), timeout=5)


        query = select(Item_Checker)
        item = await test_db_checker.execute(query)
        item = item.scalar_one_or_none()


        assert isinstance(item, Item_Checker)


        

        




