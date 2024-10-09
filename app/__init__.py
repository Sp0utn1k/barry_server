from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure Logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    handler = RotatingFileHandler('logs/app.log', maxBytes=100000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask App Startup')

    # Initialize Scheduler
    scheduler = BackgroundScheduler()
    scheduler.start()

    from . import routes
    app.register_blueprint(routes.bp)

    return app
