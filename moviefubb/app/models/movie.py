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

class Movie(Base):
    __tablename__ = 'movies'
    """ ID's """
    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    
    """ User Defined """
    title = Column(Text)
    location = Column(Text)
    status_dl = Column(Text)
    status_w = Column(Text)
    genre_tags = Column(Text)
    
    """ Bot/Computer Generated Got Stuff """
    entry_date = Column(Text)
    year = Column(Integer)
    rated = Column(Text)
    runtime = Column(Text)
    director = Column(Text)
    writer = Column(Text)
    actors = Column(Text)
    plot = Column(Text)

    country = Column(Text)
    awards = Column(Text)
    imdb_rating = Column(Text)
    imdb_votes = Column(Text)

    language = Column(Text)
    magnet = Column(Text)
    poster = Column(Text)
    imdb_id = Column(Text)
    embed = Column(Text)
    
Index('movie_index', Movie.title, mysql_length=255)