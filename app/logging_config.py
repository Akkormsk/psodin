import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging(app):
    try:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')
        handler = RotatingFileHandler(log_path, maxBytes=10000, backupCount=5)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.info('Logging is set up and running.')
    except Exception as e:
        print(f"Error setting up logger: {e}")
