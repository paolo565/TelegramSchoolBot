"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

from sqlalchemy import Column, Integer, Enum, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum("class", "teacher", "classroom"), nullable=False)
    name = Column(String(32), nullable=False)
    url = Column(String(55), nullable=False)
    last_file_id = Column(String(32), nullable=True, default=None)
    last_hash = Column(String(32), nullable=True, default=None)
    last_check = Column(DateTime, nullable=True, default=None)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(55), unique=True, nullable=False)
    title = Column(String(32), nullable=False)
    added_at = Column(DateTime, nullable=False, default=func.now())


class Subscriber(Base):
    __tablename__ = "subscribers"


    chat_id = Column(Integer, primary_key=True, autoincrement=False)
    subscribed_at = Column(DateTime, nullable=False, default=func.now())
