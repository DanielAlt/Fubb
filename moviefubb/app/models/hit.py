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

class Hit(Base):
    __tablename__='hits'
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey(Page.id))
    user_id = Column(Text)
    query = Column(Text)
    user_agent = Column(Text)
    user_addr = Column(Text)
    referrer = Column(Text)
