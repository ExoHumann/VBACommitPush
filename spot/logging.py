"""Logging configuration and factory for the spot package."""

import logging
import sys
from typing import Optional

# Global log level storage
_global_log_level = logging.INFO


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Create and configure a logger with consistent formatting.
    
    Args:
        name: Logger name. If None, uses the calling module's name.
        
    Returns:
        Configured logger instance with DEBUG, INFO, WARN, ERROR levels.
    """
    if name is None:
        # Get the caller's module name
        frame = sys._getframe(1)
        name = frame.f_globals.get('__name__', 'spot')
    
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Set level to global level or INFO if not set
    logger.setLevel(_global_log_level)
    for handler in logger.handlers:
        handler.setLevel(_global_log_level)
    
    return logger


def set_global_log_level(level: str) -> None:
    """
    Set the global log level for all loggers in the spot package.
    
    Args:
        level: Log level as string (DEBUG, INFO, WARN, ERROR)
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # Set level for root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Set level for spot package logger
    spot_logger = logging.getLogger('spot')
    spot_logger.setLevel(numeric_level)
    
    # Also set for all existing spot loggers
    for logger_name in logging.Logger.manager.loggerDict:
        if logger_name.startswith('spot'):
            logger = logging.getLogger(logger_name)
            logger.setLevel(numeric_level)
            for handler in logger.handlers:
                handler.setLevel(numeric_level)
    
    # Store the level globally for future loggers
    global _global_log_level
    _global_log_level = numeric_level


def configure_logging(verbose: bool = False, quiet: bool = False) -> None:
    """
    Configure logging based on verbosity flags.
    
    Args:
        verbose: If True, set to DEBUG level
        quiet: If True, set to ERROR level
    """
    if quiet:
        set_global_log_level('ERROR')
    elif verbose:
        set_global_log_level('DEBUG')
    else:
        set_global_log_level('INFO')