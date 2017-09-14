from hashlib import sha1
from pyramid.security import (Allow, Everyone)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import (
    Table, 
    Column, 
    Integer, 
    Text, 
    ForeignKey
)
from sqlalchemy.orm import (
    scoped_session, 
    sessionmaker, 
    relationship, 
    backref
)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Page(Base):
    __tablename__='pages'
    id = Column(Integer, primary_key=True)
    page_url = Column(Text)
    myhits = relationship('Hit')
