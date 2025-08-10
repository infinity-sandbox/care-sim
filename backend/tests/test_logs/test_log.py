from typing import Optional
import pytest
import logging
import os, sys
from logs.loggers.logger import logger_config
from app.core.config import settings


'''
    to run specific funtion: pytest -v tests/test_logs/test_log.py::TestLogger::test_logger_module
    to run specific class: pytest -v tests/test_logs/test_log.py::TestLogger
    to run specific file: pytest -v tests/test_logs/test_log.py
    to run the whole test: python -m pytest --import-mode=append
    
    to see full coverage test html information
    pytest --cov=tests/ --cov-report=html
    
'''

@pytest.fixture
def data():
    number = 10
    self_module = '__main__'
    module = 'tests.test_logs.test_log'
    
    return {
        "number": number,
        "self_module": self_module,
        "module": module
    }

@pytest.fixture
def logger(data):
    """Fixture to create a logger instance for tests."""
    return logger_config(data["self_module"])

@pytest.fixture(autouse=True)
def cleanup():
    """Ensure the log file exists before each test."""
    # Check if the log file exists; if not, create it
    log_file = os.path.join(settings.LOG_DIR, "logs.log")
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            pass  # Just create an empty file

class TestLogger:
    @pytest.mark.operation
    def test_logger_module(self, data):
        # Create logger instances
        logger_self = logger_config(data["self_module"])
        logger_module = logger_config(data["module"])

        # Check if the logger's name matches the module
        assert logger_self.logger.name == data["self_module"]
        assert logger_module.logger.name == data["module"]
        
    @pytest.mark.operation
    def test_error_logging(self, logger, capsys):
        logger.error("This is an ERROR message.")
        
        # Capture the console output
        captured = capsys.readouterr()
        
        # Assert that the error message is NOT printed on console
        assert "This is an ERROR message." not in captured.out
        log_file = os.path.join(settings.LOG_DIR, "logs.log")
        # Check if the error message is stored in the log file
        with open(log_file, 'r') as f:
            log_contents = f.read()
        
        assert "This is an ERROR message." in log_contents  # Ensure the error message is stored

    @pytest.mark.operation
    def test_critical_logging(self, logger, capsys):
        logger.critical("This is a CRITICAL message.")
        
        # Capture the console output
        captured = capsys.readouterr()
        
        # Assert that the critical message is NOT printed on console
        assert "This is a CRITICAL message." not in captured.out
        log_file = os.path.join(settings.LOG_DIR, "logs.log")
        # Check if the critical message is stored in the log file
        with open(log_file, 'r') as f:
            log_contents = f.read()
        
        assert "This is a CRITICAL message." in log_contents  # Ensure the critical message is stored

    @pytest.mark.operation
    def test_debug_logging(self, logger, capsys):
        logger.debug("This is a DEBUG message.")
        
        # Capture the console output
        captured = capsys.readouterr()
        
        # Assert that the debug message is NOT printed on console
        assert "This is a DEBUG message." in captured.out
        log_file = os.path.join(settings.LOG_DIR, "logs.log")
        # Check if the debug message is NOT stored in the log file
        with open(log_file, 'r') as f:
            log_contents = f.read()
        
        assert "This is a DEBUG message." in log_contents  # Ensure the debug message is not stored

    @pytest.mark.operation
    def test_info_logging(self, logger, capsys):
        logger.info("This is an INFO message.")
        
        # Capture the console output
        captured = capsys.readouterr()
        
        # Assert that the info message is NOT printed on console
        assert "This is an INFO message." in captured.out
        log_file = os.path.join(settings.LOG_DIR, "logs.log")
        # Check if the info message is NOT stored in the log file
        with open(log_file, 'r') as f:
            log_contents = f.read()
        
        assert "This is an INFO message." in log_contents  # Ensure the info message is not stored

    @pytest.mark.operation
    def test_warning_logging(self, logger, capsys):
        logger.warning("This is a WARNING message.")
        
        # Capture the console output
        captured = capsys.readouterr()
        
        # Assert that the warning message is NOT printed on console
        assert "This is a WARNING message." in captured.out
        log_file = os.path.join(settings.LOG_DIR, "logs.log")
        # Check if the warning message is NOT stored in the log file
        with open(log_file, 'r') as f:
            log_contents = f.read()
        
        assert "This is a WARNING message." in log_contents  # Ensure the warning message is not stored
