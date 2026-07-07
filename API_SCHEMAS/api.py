from database.models import Item, User
from models import CreatingItem, UpdateItem, CreatingUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence



#api functions to works with BD

async def create_item(item: CreatingItem, user_id: int, user_email: str, ses: AsyncSession): 
    new_item = Item(**item.model_dump(mode='json'), user_id=user_id, user_email=user_email)
    ses.add(new_item)

    await ses.commit()


    return new_item


async def list_of_items(user_id: int, ses: AsyncSession ) -> Sequence[Item]:
    query = select(Item).where(Item.user_id==user_id)
    result = await ses.execute(query)
    list1 = result.scalars().all()


    return list1

async def patching(id: int, user_id: int, data: UpdateItem, ses: AsyncSession):
    update_data = data.model_dump(exclude_unset=True, mode='json')
    query = select(Item).filter_by(id=id, user_id=user_id)
    item = await ses.execute(query)
    item = item.scalar_one()

    for k, v in update_data.items():
         setattr(item, k, v)
    

    await ses.commit()
    await ses.refresh(item)
    

    return item

async def create_user(user: CreatingUser, ses: AsyncSession):
    new_user = user.model_dump(mode='json')
    create_user = User(**new_user)
    ses.add(create_user)

    await ses.commit()


    return 'ok'

async def search_user_by_name(username: str, ses: AsyncSession):
    query = select(User).filter(User.name==username)
    res = await ses.execute(query)
    user = res.scalar_one()

    return user




        




    
        