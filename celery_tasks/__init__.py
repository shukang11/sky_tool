from celery import Celery


celery = Celery('tasks')
celery.config_from_object('celery_config')
    # TaskBase = celery.Task
    # class ContextTask(TaskBase):
    #     abstract = True
    #     def __call__(self, *args, **kwargs):
    #         with app.app_context():
    #             return TaskBase.__call__(self, *args, **kwargs)
    # celery.Task = ContextTask
