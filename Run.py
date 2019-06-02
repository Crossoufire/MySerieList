from MyLists import app
import os
import sys

import logging
from logging.handlers import RotatingFileHandler

if __name__ == "__main__":
    if not os.path.isfile('./config.ini'):
        print("Config file not found. Exit.")
        sys.exit()

    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler = RotatingFileHandler("MyLists/log/mylists.log", maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    app.run(debug=True)
