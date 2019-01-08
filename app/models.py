
from app.utils.ext import INTEGER, \
    TEXT, SMALLINT, Sequence, FLOAT, String, Column, \
    ForeignKey, DECIMAL
from app import db

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

@addModel
class FileModel(db.Model, BaseModel):
    """ 文件映射表 """

    __tablename__ = "bao_file"

    file_id = Column(INTEGER, Sequence(start=1, increment=1, name="file_id_sep"), primary_key=True, autoincrement=True)  # 主键
    file_hash = Column(String, nullable=False)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)

