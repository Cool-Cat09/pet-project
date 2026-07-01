from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, MappedAsDataclass
from pydantic import HttpUrl, EmailStr
from .engine import Base


#database models


class Item(MappedAsDataclass, Base):
    __tablename__ = 'items'

    id: Mapped[int]
    url: Mapped[HttpUrl] = mapped_column(String)
    name: Mapped[str]  
    need_price: Mapped[int]
    shop: Mapped[str]
    email: Mapped[EmailStr] = mapped_column(String)