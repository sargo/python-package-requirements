import os
import logging.config

from . import app


def run():
    log_config = os.path.join(os.path.dirname(__file__), '..', 'logging.ini')
    logging.config.fileConfig(log_config)
    app.run(host='0.0.0.0', debug=True)
