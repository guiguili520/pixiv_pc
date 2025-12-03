import logging
import os
from datetime import datetime


class Logger:
    """Simple logging utility"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    @staticmethod
    def _setup_logger():
        """Setup logger configuration"""
        os.makedirs('logs', exist_ok=True)

        logger = logging.getLogger('pixiv_crawler')
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

        # File handler
        log_file = f'logs/crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        Logger._logger = logger

    @staticmethod
    def get_logger():
        """Get logger instance"""
        if Logger._logger is None:
            Logger()
        return Logger._logger

    @staticmethod
    def info(message):
        Logger.get_logger().info(message)

    @staticmethod
    def error(message):
        Logger.get_logger().error(message)

    @staticmethod
    def warning(message):
        Logger.get_logger().warning(message)

    @staticmethod
    def debug(message):
        Logger.get_logger().debug(message)
