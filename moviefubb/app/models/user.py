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

Index('user_index', User.username, unique=True, mysql_length=255)

user_group_table = Table('user_group', Base.metadata,
    Column('user_id', Integer, ForeignKey(User.id)),
    Column('group_id', Integer, ForeignKey(Group.id))
)


class Privacy(Base):
    __tablename__ = 'privacy'
    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User')

    show_profile = Column(Text)
    show_collection = Column(Text)
    show_stats = Column(Text)

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

