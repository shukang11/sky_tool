import os
import logging

root_dir = os.path.abspath((os.path.dirname(__file__)))

class Config:
    # 开启跨站请求伪造防护
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    """SQLALCHEMY配置"""
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
    LOGGING_DIR = os.path.join(root_dir, 'logs')

    """Celery 配置"""
    from datetime import timedelta
    from kombu import Exchange, Queue
    # 导入Task所在的模块，所有使用celery.task装饰器装饰过的函数，所需要把所在的模块导入
    # 我们之前创建的几个测试用函数，都在handlers.async_tasks和handlers.schedules中
    # 所以在这里需要导入这两个模块，以str表示模块的位置，模块组成tuple后赋值给CELERY_IMPORTS
    # 这样Celery在启动时，会自动找到这些模块，并导入模块内的task
    CELERY_IMPORTS = ('celery_tasks.tasks')

    # 为Celery设定多个队列，CELERY_QUEUES是个tuple，每个tuple的元素都是由一个Queue的实例组成
    # 创建Queue的实例时，传入name和routing_key，name即队列名称
    CELERY_QUEUES = {
        Queue('default', routing_key='task.#'),
        Queue('web_task', routing_key='web.#'),
        Queue('debet_task', routing_key='debet.#', delivery_mode=1), # 设置了阅后即焚模式
        }
    # 默认的交换机名称
    CELERY_DEFAULT_EXCHANGE = 'tasks'
    # 默认的交换机类型
    CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
    # 默认的路由键
    CELERY_DEFAULT_ROUTING_KEY = 'task.default'
    # 最后，为不同的task指派不同的队列
    # 将所有的task组成dict，key为task的名称，即task所在的模块，及函数名
    # 如async_send_email所在的模块为handlers.async_tasks
    # 那么task名称就是handlers.async_tasks.async_send_email
    # 每个task的value值也是为dict，设定需要指派的队列name，及对应的routing_key
    # 这里的name和routing_key需要和CELERY_QUEUES设定的完全一致
    CELERY_ROUTES = {
        'celery_tasks.tasks.async_email_to': {
            'queue': 'web_task', 
            'routing_key': 'task.email'
        },
        'celery_tasks.tasks.async_parser_feed': {
            'queue': 'debet_task', 
            'routing_key': 'task.parser'
        },
        'celery_tasks.tasks.report_local_ip': {
            'queue': 'debet_task', 
            'routing_key': 'task.report.ip'
        },
        'celery_tasks.tasks.parse_rsses': {
            'queue': 'debet_task', 
            'routing_key': 'task.parse.rss'
        },
    }

    CELERY_RESULT_BACKEND = 'redis://localhost:6379'

    BROKER_URL = 'redis://localhost:6379/0'

    CELERY_TIMEZONE='Asia/Shanghai'

    CELERY_TASK_SERIALIZER = 'json'

    CELERY_RESULT_SERIALIZER = 'json'

    CELERY_ACCEPT_CONTENT=['json']
    # 是否忽略结果
    CELERY_IGNORE_RESULT=False

    # 定义定时任务
    CELERYBEAT_SCHEDULE = {
        # 给计划任务取一个独一无二的名字吧
        'celery_tasks.tasks.report_local_ip': {
            # task就是需要执行计划任务的函数
            'task': 'celery_tasks.tasks.report_local_ip',
            # 配置计划任务的执行时间，这里是每300秒执行一次
            'schedule': timedelta(seconds=60*24*2),
            # 传入给计划任务函数的参数
            'args': ()
        },
        'celery_tasks.tasks.parse_rsses': {
            # task就是需要执行计划任务的函数
            'task': 'celery_tasks.tasks.parse_rsses',
            # 配置计划任务的执行时间，这里是每300秒执行一次
            'schedule': timedelta(seconds=60*24*2),
            # 传入给计划任务函数的参数
            'args': ()
        }
    }

    # 限制此类型的任务， 每分钟只处理10个
    CELERY_ANNOTATIONS = {
        'celery_tasks.tasks.report_local_ip': {'rate_limit': '1/m'},
        'celery_tasks.tasks.parse_rsses': { 'rate_limit': '1/m' },
    }

    @classmethod
    def init_app(app, *args, **kwargs):
        filename=os.path.join(Config.LOGGING_DIR, 'debug.log')
        if not os.path.exists(filename):
            os.makedirs(Config.LOGGING_DIR)
            open(filename, 'w').close()
            
        logging.basicConfig(
            filename=filename, 
            level=logging.WARNING
            )


class DevelopmentConfig(Config):
    DEBUG = True

    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(root_dir, 'data-dev.sqlite')

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345678@localhost/sky_tool_dev'
    # 'mysql://root:12345678@localhost/sky_tool_dev'
    SERVICE_TOKEN_SUFFIX = 'im_token_suffix'
    # 打开数据库语句输出
    SQLALCHEMY_ECHO = False
    # 分页数量
    PAGE_LIMIT = 11


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(root_dir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/sky_tool'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
