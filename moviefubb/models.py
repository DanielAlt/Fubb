import os
from hashlib import sha1

from pyramid.security import (Allow, Everyone)

from sqlalchemy import (Table, Column, Index, Integer, Text, Boolean, ForeignKey)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Page(Base):
    __tablename__='pages'
    id = Column(Integer, primary_key=True)
    page_url = Column(Text)
    myhits = relationship('Hit')

class Hit(Base):
    __tablename__='hits'
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey(Page.id))
    user_id = Column(Text)
    query = Column(Text)
    user_agent = Column(Text)
    user_addr = Column(Text)
    referrer = Column(Text)

class Group(Base):
    __tablename__='groups'
    id = Column(Integer, primary_key=True, unique=True)
    groupname = Column(Text)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, unique=True)
    username = Column(Text, unique=True)
    email = Column(Text, unique=True)
    password = Column(Text)
    entry_date = Column(Text)
    terms_accepted = Column(Boolean)
    solicitation = Column(Boolean)
    confirmed = Column(Boolean)
    confirmation_string = Column(Text)

    mygroups = relationship(Group, secondary='user_group')
    mymovies = relationship('Movie')
    # myhits = relationship('Hit')
    profile = relationship("Profile", uselist=False)
    privacy = relationship("Privacy", uselist=False)

    def addGroup(self, group):
        self.mygroups.append(group)
        return self

    def removeGroup(self, groupname):
        if groupname in self.mygroups:
            self.mygroups.remove(groupname)

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship("User")
    
    fav_film = Column(Text)
    fav_show = Column(Text)
    fav_genre = Column(Text)
    about_me = Column(Text)
    picture = Column(Text)

class Privacy(Base):
    __tablename__ = 'privacy'
    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User')

    show_profile = Column(Text)
    show_collection = Column(Text)
    show_stats = Column(Text)

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
Index('user_index', User.username, unique=True, mysql_length=255)

user_group_table = Table('user_group', Base.metadata,
    Column('user_id', Integer, ForeignKey(User.id)),
    Column('group_id', Integer, ForeignKey(Group.id))
)

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'show'),
                (Allow, 'user', 'edit'),
                (Allow, 'admin', 'admin')]
    def __init__(self, request):
        pass