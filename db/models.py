from sqlalchemy import Table, Column, Integer, String, MetaData, Boolean, create_engine, ForeignKey, DateTime
from sqlalchemy.ext.declarative import as_declarative
import datetime

engine = create_engine('sqlite:///pdatabase.db', echo = True)
meta = MetaData()


@as_declarative()
class BaseModel(object):

    created_at = Column(DateTime, default=lambda: datetime.datetime.now())
    updated_at = Column(DateTime, onupdate=lambda: datetime.datetime.now())
    def _to_dict(self):
        _dict = {col.name: getattr(self, col.name)
                 for col in self.__table__.columns}
        return _dict


class User(BaseModel):
	__tablename__ = 'users'
	userID = Column(Integer, primary_key=True)
	name = Column(String)
	isAdmin = Column(Boolean)
	password = Column(String)

# users = Table(
# 	'users', meta,
# 	Column('userID', Integer, primary_key=True),
# 	Column('name', String),
# 	Column('isAdmin', Boolean),
# 	Column('password', String))


class Container():
	__tablename__ = 'containers'
	containerID = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	ownerID = Column(Integer, ForeignKey('users.userID'))

# containers = Table(
# 	'containers', meta,
# 	Column('containerID', Integer, primary_key=True),
# 	Column('name', String),
# 	Column('description', String),
# 	Column('ownerID', Integer, ForeignKey('users.userID')))

class Object():
	__tablename__ = 'objects'
	objectID = Column(Integer, primary_key=True)
	name = Column(String)
	containerID = Column(Integer, ForeignKey('containers'))
	description = Column(String)

# objects = Table(
# 	'objects', meta,
# 	Column('objectID', Integer, primary_key=True),
# 	Column('name', String),
# 	Column('containerID', Integer, ForeignKey('containers')),
# 	Column('description', String))

class AuthToken():
	__tablename__ = 'auth_tokens'
	token = Column(String, primary_key=True)
	userID = Column(Integer, ForeignKey('users'))
	expireDate = Column(DateTime)

# auth_tokens = Table(
# 	'authTokens', meta,
# 	Column('token', String, primary_key=True),
# 	Column('userID', Integer, ForeignKey('users')),
# 	Column('expireDate', DateTime))
def dict():
	if isinstance(obj, BaseModel):
		return obj._to_dict()

meta.create_all(engine)