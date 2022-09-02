from sqlalchemy import Table, Column, Integer, String, MetaData, Boolean, create_engine, ForeignKey, DateTime, delete
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


class User(BaseModel):
    __tablename__ = 'users'   
    name = Column(String, unique=True)
    isAdmin = Column(Boolean, default=False)
    password = Column(String)   


class Container(BaseModel):
    __tablename__ = 'containers'
    name = Column(String)
    description = Column(String)
    owner = Column(String, ForeignKey('users.name', ondelete='cascade'))


class Object(BaseModel):
    __tablename__ = 'objects'
    name = Column(String)
    description = Column(String)
    container = Column(String, ForeignKey('containers.name', ondelete='cascade'))
    

class AuthToken(BaseModel):
    __tablename__ = 'auth_tokens'
    token = Column(String)
    user = Column(String, ForeignKey('users.name', ondelete='cascade'))
    expireDate = Column(DateTime)


BaseModel.metadata.create_all(engine)
