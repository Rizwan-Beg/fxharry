"""
Industrial-grade logging configuration for IBKR streaming service.
Provides file rotation, structured logging, and detailed connection tracking.
"""

import logging
import logging.handlers
import os
import time
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "ibkr_streaming", log_dir: str = "logs") -> logging.Logger:
    """
    Setup industrial-grade logger with file rotation (no console output).
    All logs are written to files only.
    
    Args:
        name: Logger name
        log_dir: Directory to store log files
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Detailed formatter for file logs with microseconds
    class MicrosecondFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            t = time.strftime('%Y-%m-%d %H:%M:%S', ct)
            s = '%s.%03d' % (t, record.msecs)
            return s
    
    file_formatter = MicrosecondFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    )
    
    # Rotating file handler - 10MB per file, keep 10 backup files
    log_file = log_path / f"ibkr_streaming_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_file),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler - DISABLED (logs only to files)
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)
    # console_handler.setFormatter(console_formatter)
    
    # Error file handler - separate file for errors only
    error_log_file = log_path / f"ibkr_streaming_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        filename=str(error_log_file),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Add handlers to logger (only file handlers, no console)
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)  # Disabled - logs only to files
    logger.addHandler(error_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name (defaults to 'ibkr_streaming')
        
    Returns:
        Logger instance
    """
    if name is None:
        name = "ibkr_streaming"
    return setup_logger(name)

