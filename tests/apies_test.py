from httpx import AsyncClient, ASGITransport, Client
from API_SCHEMAS import User, Item, app, authentication, CreatingItem, UpdateItem, CreatingUser, COOKIE_SESSION_ID_KEY
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from . import request_to_test_server, test_db_api, get_auth_token
from typing import Any


async def test_list_of_items(request_to_test_server: AsyncClient, get_auth_token: dict[str, str], test_db_api: AsyncSession):
    res = await request_to_test_server.get(url='/', cookies=get_auth_token)

    assert res.status_code == 200
    assert isinstance(res.json(), list)
    

async def test_creating_item(request_to_test_server: AsyncClient, get_auth_token: dict[str, str], test_db_api: AsyncSession):
    payload = CreatingItem(url='https://google.com', name='GTA 6', need_price=200, shop='wb')
    res = await request_to_test_server.post(url='/create_item', cookies=get_auth_token, json=payload.model_dump())

    query = select(Item)

    item = await test_db_api.execute(query)
    item = item.scalar_one()


    assert res.status_code == 200
    assert isinstance(item, Item)


async def test_deleting_item(request_to_test_server: AsyncClient, get_auth_token: dict[str, str], test_db_api: AsyncSession):
    item = Item(url='https://google.com', name='GTA 6', need_price=200, shop='wb', user_id=1, user_email='bogdanlavrenenko@gmail.com')
    test_db_api.add(item)
    await test_db_api.commit()
    
    res = await request_to_test_server.delete(url='/delete_item', cookies=get_auth_token, params={'id': item.id})

    query = select(Item)
    none = await test_db_api.execute(query)
    none = none.scalar_one_or_none()


    assert res.status_code == 200
    assert none == None


async def test_patching_item(request_to_test_server: AsyncClient, get_auth_token: dict[str, str], test_db_api: AsyncSession):
    item = Item(url='https://google.com', name='GTA 6', need_price=200, shop='wb', user_id=1, user_email='bogdanlavrenenko@gmail.com')
    test_db_api.add(item)
    await test_db_api.commit()


    new_item = UpdateItem(need_price=67)
    res = await request_to_test_server.patch(url='/patch_item', cookies=get_auth_token, json=new_item.model_dump(exclude_unset=True), params={'id':item.id})

    
    query = select(Item)
    update_item = await test_db_api.execute(query)
    update_item = update_item.scalar_one()


    assert res.status_code == 200

    await test_db_api.refresh(item)

    assert update_item.need_price == 67


async def test_creating_user(request_to_test_server: AsyncClient, get_auth_token: dict[str, str], test_db_api: AsyncSession):
    payload = CreatingUser(name='Bogdan', email='bogdanlavrenenko@gmail.com', password='qwerty')

    res = await request_to_test_server.post(url='/create_user', json=payload.model_dump())


    query = select(User)
    user = await test_db_api.execute(query)
    user = user.scalar_one()



    assert res.status_code == 200
    assert isinstance(user, User)


async def test_authentication(request_to_test_server: AsyncClient, test_db_api: AsyncSession):
    payload = CreatingUser(name='Bogdan', password='qwerty', email='bogdanlavrenenko@gmail.com')

    await request_to_test_server.post(url='/create_user', json=payload.model_dump())


    mock_response = Response()

    res = await authentication(username='Bogdan', password='qwerty', response=mock_response, ses=test_db_api)


    assert res != None


async def test_logout(request_to_test_server: AsyncClient, test_db_api: AsyncSession):
    payload = CreatingUser(name='Bogdan', password='qwerty', email='bogdanlavrenenko@gmail.com')
    await request_to_test_server.post(url='/create_user', json=payload.model_dump())
    
    
    mock_response = Response()


    await authentication(username='Bogdan', password='qwerty', response=mock_response, ses=test_db_api)

    set_cookie_header = mock_response.headers.get("set-cookie", "")

    cookie = {COOKIE_SESSION_ID_KEY: set_cookie_header}

    res = await request_to_test_server.post(url='/logout', cookies=cookie)


    assert res.status_code == 200
    assert not res.cookies


async def test_logging(request_to_test_server: AsyncClient, test_db_api: AsyncSession):
    payload = CreatingUser(name='Bogdan', password='qwerty', email='bogdanlavrenenko@gmail.com')
    await request_to_test_server.post(url='/create_user', json=payload.model_dump())


    payload = {'username': 'Bogdan', 'password': 'qwerty'}
    res = await request_to_test_server.post(url='/authentication', data=payload)


    assert res.status_code == 200

