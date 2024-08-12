"""
Celery application configuration and initialization.

This module sets up the Celery application, configures it with the Flask app,
and provides functions to initialize Celery with the Flask app context.
"""

from celery import Celery
from flask import Flask
from config import Config


def make_celery(app=None):
    """
    Create and configure a Celery app instance.

    This function creates a Celery app, configures it with the Flask app's
    configuration, and sets up a custom task class that runs tasks with the
    Flask app context.

    Args:
        app (Flask, optional): A Flask application instance. If not provided,
                               a new Flask app will be created.

    Returns:
        Celery: A configured Celery application instance.
    """
    app = app or Flask(__name__)
    Config.init_app(app)

    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url'],
        include=['tasks.sync_tasks']
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
    """
    Initialize Celery with the Flask app's configuration.

    This function updates the Celery app's configuration with the Flask app's
    configuration.

    Args:
        app (Flask): A Flask application instance.
    """
    Config.init_app(app)
    celery_app.conf.update(app.config)