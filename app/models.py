from app.utils.ext import INTEGER, \
    TEXT, SMALLINT, Sequence, FLOAT, String, Column, \
    ForeignKey, DECIMAL, db


"""
doc: http://docs.jinkan.org/docs/flask-sqlalchemy/models.html
"""

__all__ = ['User', 'FileModel']

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

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    nickname = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255))
    status = db.Column(db.SMALLINT, default=0) # 用户状态
    token = db.Column(String(64), nullable=True) # 用本地的token ，用来重新获得请求 token 的 token

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

    file_id = Column(INTEGER, Sequence(start=1, increment=1, name="file_id_sep"), primary_key=True, autoincrement=True)  # 主键
    file_hash = Column(String, nullable=False)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
