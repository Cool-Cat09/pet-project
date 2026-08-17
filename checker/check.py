import httpx
import asyncio
from database.engine import ses_control, engine, ses_control_db
from sqlalchemy import select
from database.models import Item_Checker
from check_base import PARAMS
from faststream.rabbit import RabbitBroker, RabbitQueue
from faststream import FastStream, Depends
from sqlalchemy.ext.asyncio import AsyncSession 
from pydantic import EmailStr

from typing import Any

from checker_config import rabbit_settings
from log_conf import logger


#in infinity loop checking need_price from BD and compare with parsing data from sites

log = logger()


broker = RabbitBroker(url=rabbit_settings.rabbitmq_url)
app = FastStream(broker)

queue = RabbitQueue(name='main', durable=True)
queue1 = RabbitQueue(name='db', durable=True)


async def check_from_sites(url: EmailStr, client: httpx.AsyncClient):
    """do a request to a sites and get data
    
    return: data
    """


    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://google.com"}
    

    response = await client.get(url=url, headers=headers, follow_redirects=True)
    try:
        data = response.json()
    except Exception as e:
        print(e)
        return '0'
    return data

async def db_checker():
    """main func of checker. compare prices and send message to sendler"""


    async with httpx.AsyncClient(verify=False) as client:
        while True:
            async with ses_control() as session:
                query = select(Item_Checker)
                result = await session.execute(query)
                items = result.scalars().all()
                for item in items:
                    url = item.url
                    need_price = item.need_price
                    data = await check_from_sites(url=url, client=client)
                    if data == '0':
                        log.info('exc')
                    else:
                        price = PARAMS.get(item.shop)
                        price_val = None
                        try:
                            price_val = price(data=data)
                            log.info(msg=price_val)
                            log.info(msg=need_price)
                            if price_val and price_val <= need_price:
                                await broker.publish(message={'status': 'fell', 'email': item.email}, queue='main')
                                log.info('publish')
                        except Exception as e:
                            log.info(e)
                        

                
            await asyncio.sleep(90)


@broker.subscriber(queue1)
async def insert_in_db(msg: dict[str, Any], ses: AsyncSession = Depends(ses_control_db)):
    """listening messege from API change DB"""


    if 'created' in msg:
        data = msg['created']
        new_item = Item_Checker(name=data.get('name'), url=data.get('url'), shop=data.get('shop'), need_price=data.get('need_price'), id=msg['id'], email=data.get('email'))
        ses.add(new_item)
        await ses.commit()

        return {'status': 200}

    
    if 'deleted' in msg:
        data = msg['deleted']
        t_id = data.get('id')
        deletion = select(Item_Checker).filter(Item_Checker.id==t_id)
        del_item = await ses.execute(deletion)
        res = del_item.scalars().first()
        await ses.delete(res)
        await ses.commit()
        
        return {'status': 200}
    

    if 'patched' in msg:
        data = msg['patched']
        item_id: int = msg['item_id']
        query = select(Item_Checker).filter_by(id=item_id)
        item = await ses.execute(query)
        item = item.scalar_one_or_none()

        for k, v in data.items():
            setattr(item, k, v)
        

        await ses.commit()
        await ses.refresh(item)
        

        return {'status': 200}
        




@app.after_startup
async def starting_app():
    asyncio.create_task(db_checker())


@app.after_shutdown
async def close():
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(app.run())

