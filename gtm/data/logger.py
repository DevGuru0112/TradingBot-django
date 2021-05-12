import logging.handlers

from .data import Data


class Logger:

    # Logger = None

    def __init__(self, service_name="trader", enable_notifications=True):

        # Logger setup
        self.Logger = logging.getLogger(f"{service_name}_logger")

        self.Logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # default is "logs/trader.log"
        fh = logging.FileHandler(f"logs/{service_name}.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.Logger.addHandler(fh)

        # notification handler
        self.nh = Data.nh

    def log(self, message, level="info", notification=True):

        if level == "info":
            self.Logger.info(message)
        elif level == "warning":
            self.Logger.warning(message)
        elif level == "error":
            self.Logger.error(message)
        elif level == "debug":
            self.Logger.debug(message)

        if notification and self.nh.enabled:
            self.nh.send_notification(message)

    def info(self, message, notification=True):
        self.log(message, "info", notification)

    def warning(self, message, notification=True):
        self.log(message, "warning", notification)

    def error(self, message, notification=True):
        self.log(message, "error", notification)

    def debug(self, message, notification=True):
        self.log(message, "debug", notification)