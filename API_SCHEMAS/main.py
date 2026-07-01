# the head fastapi app

from fastapi import FastAPI, Depends, HTTPException, status, Form, Response, Cookie
import uvicorn
from database.engine import Base, engine, Session
from database.models import Item, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from api import creating_item, list_of_items, patching, create_user, search_user_by_name
from models import CreatingItem, UpdateItem, CreatingUser, UserSchema
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from faststream.rabbit import RabbitQueue, RabbitBroker
from database.pass_to_hash import hash_pass, check_pass
from token_issuence import encode_jwt, decode_jwt
import uuid
from datetime import datetime, timezone
from typing import Any

from api_config import rabbit_settings

broker = RabbitBroker(url=rabbit_settings.rabbitmq_url)
queue = RabbitQueue(name='db', durable=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with broker:
        yield 
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=['*'],
    allow_headers=['*'],
)


async def db_helper():
    """dependence to gives sessions
    
    !!!Dependence
    """


    async with Session() as ses:
        try:
            yield ses
        except IntegrityError as e:
            await ses.rollback()
            print(e)
        except Exception as e:
            await ses.rollback()
            print(e)
            raise e
        finally: 
            await ses.close()


COOKIE_SESSION_ID_KEY = 'web-app-session-id'


def gen_ses_id():
    return uuid.uuid4().hex


async def authentication(response: Response, username: str = Form(), password: str = Form(), ses: AsyncSession = Depends(db_helper)):
    """create jwt when user do aunthentication

    !!!Dependence
    """


    try:
        user = await search_user_by_name(username=username, ses=ses)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user is not found')

    if check_pass(password=password, hashed_password=user.password):
        token = encode_jwt(payload={'id': user.id, 'sub': user.email})
        response.set_cookie(COOKIE_SESSION_ID_KEY, value=token, max_age=86400)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid password')


async def authorization(response: Response, token: str = Cookie(alias=COOKIE_SESSION_ID_KEY)):
    """check jwt and gives user
    
    !!!Dependence
    """


    try:
        payload = decode_jwt(token=token)
        now = int(datetime.now(timezone.utc).timestamp())
        time_left =payload['exp'] - now
        if time_left < 300:
            token = encode_jwt(payload={'id': payload['id'], 'sub': payload['sub']})
            response.set_cookie(key=COOKIE_SESSION_ID_KEY, value=token, max_age=1380)
        return payload

    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)





@app.post('/authentication')
async def loging(user: UserSchema = Depends(authentication)):
    return {'stauts': 200}


@app.get('/')
async def list_of_user_items(user: dict[str, Any] = Depends(authorization), db: AsyncSession = Depends(db_helper)):
    result = await list_of_items(ses=db, user_id=user['id'])
    return result





@app.delete('/del')
async def delete(id: int, user: dict[str, Any] = Depends(authorization),  ses: AsyncSession = Depends(db_helper)):
    try:
        item = select(Item).filter_by(id=id, user_id=user['id'])
        del_item = await ses.execute(item)
        result = del_item.scalars().first()
        res_data = {'id': result.id}
        await ses.delete(result)
        await broker.request(message={'deleted': res_data}, queue=queue)

        return {'status': 200}
    except AttributeError:
        await ses.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)




@app.post('/create_item')
async def creating(item: CreatingItem, user: dict[str, Any] = Depends(authorization), ses: AsyncSession = Depends(db_helper)):
    try:
        new_item = await creating_item(item=item, ses=ses, user_id=user['id'], user_email=user['sub'])
        mes: dict[str, int] = item.model_dump(mode='json')
        mes['email'] = user['sub']
        await broker.request(message={'created': mes, 'id': new_item.id, 'user_id': user['sub']}, queue=queue)

        return {'status': 200}
    except IntegrityError:
        await ses.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='try to use another url')



@app.patch('/patch_item')
async def patching_item(id: int, data: UpdateItem, user: dict[str, Any] = Depends(authorization), ses: AsyncSession = Depends(db_helper)):
    try:
        await patching(id=id, data=data, ses=ses, user_id=user['id'])
        await broker.request(message={'patched': data, 'id': user['sub'], 'item_id': id}, queue=queue)

        return {'stauts': 200}
    except IntegrityError:
        await ses.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid information')


@app.post('/create_user')
async def creating_user(user: CreatingUser, ses: AsyncSession = Depends(db_helper)): 
    try:
        user.password = hash_pass(user.password)
        await create_user(user=user, ses=ses)

        return {'status': 200}
    except IntegrityError:
        await ses.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='email is existing')
    

@app.post('/logout')
async def logout(response: Response, token: str = Cookie(alias=COOKIE_SESSION_ID_KEY)):
    try:
        response.delete_cookie(key=COOKIE_SESSION_ID_KEY)
        return {'status': 200}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



# entry point
if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0')




