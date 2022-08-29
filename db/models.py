from sqlalchemy import Table, Column, Integer, String, MetaData, Boolean, create_engine, ForeignKey, DateTime
from sqlalchemy.ext.declarative import as_declarative
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask




engine = create_engine('sqlite:////home/bianca/workspace/Project/object_storage/db/pdatabase.db', echo=True)
# meta = MetaData()

db = None

def register_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/bianca/workspace/Project/object_storage/db/pdatabase.db'    
    global db
    db = SQLAlchemy(app)

@as_declarative()
class BaseModel(object):
    ID = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now())
    updated_at = Column(DateTime, onupdate=lambda: datetime.datetime.now())

    def _to_dict(self):
        _dict = {col.name: getattr(self, col.name)
                 for col in self.__table__.columns}
        return _dict


    def save(self):
        db.session.add(self)
        db.session.commit()
        db.session.flush()
        db.session.refresh(self)
    # def __init__(self, created_at: str, updated_at: str):
    #     self.created_at = created_at
    #     self.updated_at = updated_at

    # def _to_dict(self):
    #     _dict = {col.name: getattr(self, col.name)
    #              for col in self.__table__.columns}
    #     return _dict


class User(BaseModel):
    __tablename__ = 'users'   
    name = Column(String)
    isAdmin = Column(Boolean, default=False)
    password = Column(String)

    # def __init__(self, created_at: str, updated_at: str, ID: int, name: str, isAdmin: bool, password: str):
    #     self.name = name
    #     self.isAdmin = isAdmin
    #     self.password = password
    #     super(User, self).__init__()


    def create(name, password):  # create new user
        new_user = User(name=name, password=password)
        new_user.save()
        


# users = Table(
#     'users', meta,
#     Column('userID', Integer, primary_key=True),
#     Column('name', String),
#     Column('isAdmin', Boolean),
#     Column('password', String))


class Container(BaseModel):
    __tablename__ = 'containers'
    name = Column(String)
    description = Column(String)
    owner = Column(String, ForeignKey('users.name'))

    def create(name, description, owner):
        new_container = Container(name=name, description=description, owner=owner)
        new_container.save()

# containers = Table(
#     'containers', meta,
#     Column('containerID', Integer, primary_key=True),
#     Column('name', String),
#     Column('description', String),
#     Column('ownerID', Integer, ForeignKey('users.userID')))


class Object(BaseModel):
    __tablename__ = 'objects'
    name = Column(String)
    description = Column(String)
    container = Column(String, ForeignKey('containers.name'))
    
    def create(name, description, container):
        new_object = Object(name=name, description=description, container=container)
        new_object.save()

# objects = Table(
#     'objects', meta,
#     Column('objectID', Integer, primary_key=True),
#     Column('name', String),
#     Column('containerID', Integer, ForeignKey('containers')),
#     Column('description', String))


class AuthToken(BaseModel):
    __tablename__ = 'auth_tokens'
    token = Column(String)
    user = Column(String, ForeignKey('users.name'))
    expireDate = Column(DateTime)

# auth_tokens = Table(
#     'authTokens', meta,
#     Column('token', String, primary_key=True),
#     Column('userID', Integer, ForeignKey('users')),
#     Column('expireDate', DateTime))


# def dict():
#     if isinstance(obj, BaseModel):
#         return obj._to_dict()
# import pdb; pdb.set_trace()
BaseModel.metadata.create_all(engine)
