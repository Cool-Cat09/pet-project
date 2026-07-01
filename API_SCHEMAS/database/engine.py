from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from contextlib import asynccontextmanager
from api_config import database_settings





URL = database_settings.database_url

class Base(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True)

engine = create_async_engine(URL, echo=True)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)



@asynccontextmanager
async def ses_control():
    """create async session
    
    !!!Dependence
    """


    async with Session() as ses:
        try:
            yield ses
            await ses.commit()
        except Exception:
            await ses.rollback()
        finally:
            await ses.close()








