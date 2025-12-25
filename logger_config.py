import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """
    Configure comprehensive logging for the application.
    Logs security events, errors, and general application activity.
    """
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=10485760,
        backupCount=10
    )
    security_handler.setFormatter(formatter)
    security_handler.setLevel(logging.WARNING)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(security_handler)
    app.logger.setLevel(logging.INFO)
    
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    app.logger.info('Application startup')
