from app.utils.ext import INTEGER, \
    TEXT, SMALLINT, Sequence, FLOAT, String, Column, \
    ForeignKey, DECIMAL, db


__all__ = []

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
    def queryAll(Model):
        items = db.session.query(Model)
        return items or []


# Define models
Roles_Users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

@addModel
class Role(db.Model, BaseModel):
    __tablename__ = "bao_role"

    id = db.Column(INTEGER, primary_key=True)
    name = db.Column(String(80), unique=True)
    weights = db.Column(INTEGER) # 权重
    description = db.Column(String(255), nullable=True)


@addModel
class User(db.Model, BaseModel):
    __tablename__ = "bao_user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    login_token = db.Column(String(64), nullable=True)
    req_token =db.Column(String(64), nullable=True)

    @classmethod
    def get_user(cls, user_id=None, login_token=None, req_token=None):
        try:
            if user_id:
                return db.session.query(User).filter_by(id=user_id).first()
            elif login_token:
                return db.session.query(User).filter_by(login_token=login_token).first()
            elif req_token:
                return db.session.query(User).filter_by(req_token=req_token).first()
            pass
        except:
            return None


@addModel
class FileModel(db.Model, BaseModel):
    """ 文件映射表 """

    __tablename__ = "bao_file"

    file_id = Column(INTEGER, Sequence(start=1, increment=1, name="file_id_sep"), primary_key=True, autoincrement=True)  # 主键
    file_hash = Column(String, nullable=False)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
