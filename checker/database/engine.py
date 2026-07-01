from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from contextlib import asynccontextmanager

from checker_config import database_settings




URL = database_settings.database_url

class Base(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

engine = create_async_engine(URL, echo=True)
Session = async_sessionmaker(bind=engine)



@asynccontextmanager
async def ses_control():
    """get session to block async with"""


    async with Session() as ses:
        try:
            yield ses
        except Exception:
            await ses.rollback()
        finally:
            await ses.close()


async def ses_control_db():
    """get session
    
    !!!Dependence
    """
    async with Session() as ses:
        try:
            yield ses
        except Exception as e:
            await ses.rollback()
            raise e







