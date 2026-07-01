from sqlalchemy.orm import Mapped, mapped_column, relationship 
from sqlalchemy import ForeignKey, String
from .engine import Base
from pydantic import HttpUrl, EmailStr


#database models

class Item(Base):
    __tablename__ = 'items'

    url: Mapped[HttpUrl] = mapped_column(String)
    name: Mapped[str]  
    need_price: Mapped[int]
    shop: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user_email: Mapped[EmailStr] = mapped_column(String)
    user: Mapped['User'] = relationship(back_populates='items')


class User(Base):
    __tablename__ = 'users'

    name: Mapped[str] = mapped_column(unique=True)
    email: Mapped[EmailStr] = mapped_column(String, unique=True)
    password: Mapped[str]
    items: Mapped[list['Item']] = relationship(back_populates='user')

