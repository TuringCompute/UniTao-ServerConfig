import logging
import os


class Log:
    @staticmethod
    def get_logger(name, log_file="", level=logging.INFO):
        """
        Set up a logger that writes to both the console and a log file.

        :param name: The name of the logger.
        :param log_file: The path of the log file.
        :param level: The logging level (e.g., logging.INFO, logging.DEBUG).
        :return: A configured logger.
        """
        # Create a custom logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Prevent logger from adding duplicate handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create formatters
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)

        # Create console handlers
        c_handler = logging.StreamHandler()  # Console handler
        c_handler.setLevel(level)
        c_handler.setFormatter(formatter) # Attach formatter to handlers
        logger.addHandler(c_handler)

        if log_file != "":
            f_handler = logging.FileHandler(log_file)  # File handler
            f_handler.setLevel(level)
            f_handler.setFormatter(formatter)
            logger.addHandler(f_handler)
        return logger
