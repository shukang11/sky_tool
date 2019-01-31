import os

root_dir = os.path.abspath((os.path.dirname(__file__)))


class Config:
    # 开启跨站请求伪造防护
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    """配置上传文件相关"""
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = ('txt', 'png', 'jpg', 'jpeg')

    """Flask Uploads 配置"""
    UPLOADED_PHOTOS_DEST = UPLOAD_FOLDER
    UPLOADS_DEFAULT_DEST = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 10*1024*1024

    """Flask Security 配置"""
    SECURITY_PASSWORD_SALT = "saltValue"
    SECURITY_PASSWORD_HASH = "sha512_crypt"


    """ Logging 设置 """
    LOGGING_FORMATTER = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
    LOGGING_DATE_FORMATTER = "%a %d %b %Y %H:%M:%S"

    @classmethod
    def init_app(app, *args, **kwargs):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(root_dir, 'data-dev.sqlite')

    # 'mysql://root:123456@localhost/tree_appdev'
    SERVICE_TOKEN_SUFFIX = 'im_token_suffix'
    # 分页数量
    PAGE_LIMIT = 11


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(root_dir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:111111@localhost/tree_app'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
