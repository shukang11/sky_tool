from app.utils.ext import INTEGER, \
    TEXT, SMALLINT, Sequence, FLOAT, String, Column, \
    ForeignKey, DECIMAL, db, INTEGER
from app.utils.strings import get_unix_time_tuple


"""
doc: http://docs.jinkan.org/docs/flask-sqlalchemy/models.html
"""

__all__ = ['User', 'FileModel', 'FileUserModel', 'LoginRecord', 'TodoModel', 'RssModel']

# 对外展示的
tables = {}


def addModel(model):
    tables[model.__name__] = model
    return model


class BaseModel():
    """可以拓展功能"""

    def save(self, commit=False):
        db.session.add(self)
        if commit:
            db.session.commit()

    def delete(self, logic=True):

        if logic:
            self.is_delete = True
        else:
            db.session.delete(self)
        db.session.commit()

    @staticmethod
    def query_all(Model):
        items = db.session.query(Model).all()
        return items or []


@addModel
class User(db.Model, BaseModel):
    __tablename__ = "bao_user"

    id = Column(INTEGER, primary_key=True)
    email = Column(String(255), unique=True)
    nickname = Column(String(255), nullable=True)
    password = Column(String(255))
    status = Column(SMALLINT, default=0)  # 用户状态
    # 用本地的 token ，用来重新获得请求 token 的 token
    token = Column(String(64), nullable=True)

    @classmethod
    def get_user(cls, user_id=None, token=None):
        """
        获得用户
        :param user_id: 用户的id
        :param token:  用户的token
        :return: 用户实例， 可能为空
        """
        if user_id:
            return db.session.query(User).filter_by(id=user_id).first()
        elif token:
            return db.session.query(User).filter_by(token=token).first()


@addModel
class FileModel(db.Model, BaseModel):
    """ 文件映射表 """

    __tablename__ = "bao_file"

    file_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="file_id_sep"), primary_key=True, autoincrement=True)  # 主键
    file_hash = Column(String(64), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_type = Column(String(32), nullable=True)

class FileUserModel(db.Model, BaseModel):
    """ 文件与用户映射 """
    __tablename__ = "bao_file_user"

    file_user_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="file_user_id_sep"), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, nullable=False)
    file_id = Column(INTEGER, nullable=False)
    add_time = Column(String(20), nullable=True)
    file_user_state = Column(SMALLINT, nullable=True)  # 1 创建(未验证) 2 有效 3 失效

    def __init__(self, user_id: int, file_id: int, add_time: str=None):
        self.user_id = user_id
        self.file_id = file_id
        self.file_user_state = 1
        self.add_time = add_time or get_unix_time_tuple()

@addModel
class LoginRecord(db.Model, BaseModel):
    """ 登录记录表 """

    __tablename__ = "bao_login_record"

    record_id = Column(INTEGER, Sequence(start=1, increment=1,
                                         name="record_id_sep"), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER)
    login_time = Column(String(20), nullable=True)
    log_ip = Column(String(20), nullable=True)


@addModel
class TodoModel(db.Model, BaseModel):
    """ Todo list """
    __tablename__ = "bao_todo"

    todo_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="todo_id_sep"), primary_key=True, autoincrement=True)
    todo_title = Column(String(255), nullable=True)
    add_time = Column(String(20), nullable=True)
    bind_user_id = Column(INTEGER, nullable=True)
    todo_state = Column(SMALLINT, nullable=True)  # 1 创建 2 完成 3 删除

@addModel
class RssModel(db.Model, BaseModel):
    """ rss 订阅 """
    __tablename__ = "bao_rss"

    rss_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="rss_id_sep"), primary_key=True, autoincrement=True)
    rss_link = Column(String(255), nullable=True, unique=True)
    rss_subtitle = Column(String(255), nullable=True)
    add_time = Column(String(20), nullable=True)
    rss_version = Column(String(10), nullable=True)
    rss_state = Column(SMALLINT, nullable=True)  # 1 创建(未验证) 2 有效 3 失效

    def __init__(self, link: str, add_time: str=None):
        self.rss_link = link
        self.rss_state = 1
        self.add_time = add_time or get_unix_time_tuple()


@addModel
class RssUserModel(db.Model,  BaseModel):
    """ rss 与用户映射 """
    __tablename__ = "bao_rss_user"

    rss_user_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="rss_user_id_sep"), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, nullable=False)
    rss_id = Column(INTEGER, nullable=False)
    add_time = Column(String(20), nullable=True)
    rss_user_state = Column(SMALLINT, nullable=True)  # 1 创建(未验证) 2 有效 3 失效

    def __init__(self, user_id: int, rss_id: int, add_time: str=None):
        self.user_id = user_id
        self.rss_id = rss_id
        self.rss_user_state = 1
        self.add_time = add_time or get_unix_time_tuple()

@addModel
class RssContentModel(db.Model, BaseModel):

    __tablename__ = "bao_rss_content"

    content_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="content_id_sep"), primary_key=True, autoincrement=True)
    content_base = Column(String(255), nullable=True)
    content_link = Column(String(255), unique=True, nullable=True)
    content_title = Column(String(255), nullable=True)
    content_description = Column(TEXT, nullable=True)
    add_time = Column(String(20), nullable=True)

    def __init__(self, link: str, baseurl: str, title: str, description: str, add_time: str=None):
        self.content_link = link
        self.content_base = baseurl
        self.content_title = title
        self.content_description = description
        self.add_time = add_time or get_unix_time_tuple()


class RssReadRecordModel(db.Model, BaseModel):
    __tablename__ = 'bao_rss_read_record'

    read_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="read_id_sep"), primary_key=True, autoincrement=True)
    read_url_id = Column(INTEGER, nullable=False)
    read_user_id = Column(INTEGER)
    read_time = Column(String(20), nullable=True)

    def __init__(self, url_id: int, user_id: int, read_at: str = None):
        self.read_url_id = url_id
        self.read_user_id = user_id
        self.read_time = read_at or get_unix_time_tuple()

class TaskModel(db.Model, BaseModel):
    """ 包含了任务发起者，开始时间, 结束时间 状态等 """
    __tablename__ = 'bao_task_record'

    task_id = Column(String(125), primary_key=True)
    tast_name = Column(String(255))
    argsrepr = Column(String(255))
    kwargs = Column(String(255))
    user_id = Column(INTEGER)
    begin_at = Column(String(20))
    end_at = Column(String(20))
    is_succ = Column(SMALLINT)
