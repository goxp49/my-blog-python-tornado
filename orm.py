from sqlalchemy import Column, String, create_engine,DateTime,Boolean,Integer
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Settings to connect to mysql database
database_setting = { 'database_type':'mysql',    # 数据库类型
                'connector':'mysqlconnector',    # 数据库连接器
                'user_name':'root',              # 用户名，根据实际情况修改
                'password':'2952342',            # 用户密码，根据实际情况修改
                'host_name':'localhost:3306',         # 在本机上运行
                'database_name':'bloguser',
                }

# 创建对象的基类:
Base = declarative_base()

# 1. `primary_key`：主键，True和False。
# 2. `autoincrement`：是否自动增长，True和False。
# 3. `unique`：是否唯一。
# 4. `nullable`：是否可空，默认是True。
# 5. `default`：默认值。
# 6. `onupdate`：在更新的时候，一般用在时间上面。


class User(Base):
    __tablename__ = 'user'  # 表名

    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(20), nullable=False,unique=True)
    password = Column(String(20),nullable=False)
    mail = Column(String(30),nullable=False)
    regdate = Column(DateTime,nullable=False)
    sex = Column(Boolean,nullable=True,default=False)
    mobile = Column(String(11))
    loginnum = Column(Integer,nullable=False,default=0)
    lasttime = Column(DateTime)
    lastip = Column(String(30))
    curtime = Column(DateTime)
    curip = Column(String(30))
    admin = Column(Boolean, nullable=True,default=False)

    def __repr__(self):
        return "<User>{}:{}".format(self.name, self.password)


class Article(Base):
    __tablename__ = 'article'  # 表名

    id = Column(Integer,primary_key=True,autoincrement=True)
    userName = Column(String(20), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(20000), nullable=False)
    describe = Column(String(1000), nullable=False)
    category = Column(Integer, nullable=False)
    keywork = Column(String(100))
    password = Column(String(50))
    visibility = Column(Integer,nullable=False)
    date = Column(DateTime)
    pictuername = Column(String(200))

    def __repr__(self):
        return "<Article>{}:{}".format(self.name, self.password)


class LifeShare(Base):
    __tablename__ = 'lifeshare'  # 表名

    id = Column(Integer,primary_key=True,autoincrement=True)
    userName = Column(String(20), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(20000), nullable=False)
    describe = Column(String(1000), nullable=False)
    visibility = Column(Integer,nullable=False)
    date = Column(DateTime)
    pictuername = Column(String(200))

    def __repr__(self):
        return "<LifeShare>{}:{}".format(self.name, self.password)

class BBS(Base):
    __tablename__ = 'bbs'  # 表名

    id = Column(Integer,primary_key=True,autoincrement=True)
    icon = Column(Integer,default=0)
    ipaddress = Column(String(30))
    content = Column(String(20000), nullable=False)
    date = Column(DateTime)



class System(Base):
    __tablename__ = 'system'  # 表名

    id = Column(Integer,primary_key=True,autoincrement=True)
    handlers = Column(String(20),nullable=False)
    ipaddress = Column(String(30))
    dataclass = Column(String(30), nullable=False,unique=True)
    content = Column(String(20000), nullable=False)
    date = Column(DateTime)

class Category(Base):
    __tablename__ = 'category'  # 表名

    id = Column(Integer,primary_key=True,autoincrement=False)
    categoryname = Column(String(30),nullable=False)
    describe = Column(String(100))
    number = Column(Integer, default=0)

class Loginlog(Base):
    __tablename__ = 'loginlog'  # 表名

    id = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String(20))
    ipaddress = Column(String(30))
    date = Column(DateTime)

# 初始化数据库连接:
engine = create_engine(  # 生成连接字符串，有特定的格式
    database_setting['database_type'] +
    '+' +
    database_setting['connector'] +
    '://' +
    database_setting['user_name'] +
    ':' +
    database_setting['password'] +
    '@' +
    database_setting['host_name'] +
    '/' +
    database_setting['database_name']
)
Session = sessionmaker(bind=engine)
SessionType = scoped_session(sessionmaker(bind=engine))