from celery import Celery
from flask import Flask
from config import Config

def make_celery(app=None):
    app = app or Flask(__name__)
    Config.init_app(app)

    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery_app = make_celery()

def init_celery(app):
    Config.init_app(app)
    celery_app.conf.update(app.config)