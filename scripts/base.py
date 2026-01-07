"""
Base utilities for scripts.

Provides common functionality for all scripts including
database session management, logging, and error handling.
"""

import logging
import sys
import time
from contextlib import contextmanager
from typing import Generator, Callable, Any

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def setup_logging(script_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging for a script.

    Args:
        script_name: Name of the script (used in log messages)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=level,
        format=f'%(asctime)s - {script_name} - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(script_name)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Automatically handles session cleanup and rollback on errors.

    Usage:
        with get_db_session() as session:
            # Use session here
            session.add(model)
            session.commit()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class RateLimiter:
    """
    Rate limiter to control API request frequency.

    Ensures that calls don't exceed a specified rate.
    """

    def __init__(self, max_calls: int, period: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed per period
            period: Time period in seconds (default: 1.0)
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def wait_if_needed(self):
        """Wait if necessary to respect the rate limit."""
        now = time.time()

        # Remove calls outside the current period
        self.calls = [call_time for call_time in self.calls if now - call_time < self.period]

        # If at max capacity, wait until the oldest call expires
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            # Remove the oldest call
            self.calls.pop(0)

        # Record this call
        self.calls.append(time.time())

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to rate limit a function.

        Usage:
            limiter = RateLimiter(max_calls=2, period=1.0)

            @limiter
            def my_api_call():
                # API call here
                pass
        """
        def wrapper(*args, **kwargs) -> Any:
            self.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper


def run_script(script_func, script_name: str):
    """
    Wrapper to run a script with proper error handling and logging.

    Args:
        script_func: The main script function to execute
        script_name: Name of the script (for logging)

    Usage:
        def main():
            # Your script logic here
            pass

        if __name__ == "__main__":
            run_script(main, "my_script")
    """
    logger = setup_logging(script_name)

    try:
        logger.info(f"Starting {script_name}")
        script_func()
        logger.info(f"Completed {script_name} successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in {script_name}: {str(e)}", exc_info=True)
        sys.exit(1)


async def run_async_script(script_func, script_name: str):
    """
    Wrapper to run a script with proper error handling and logging.

    Args:
        script_func: The main script function to execute
        script_name: Name of the script (for logging)

    Usage:
        def main():
            # Your script logic here
            pass

        if __name__ == "__main__":
            run_script(main, "my_script")
    """
    logger = setup_logging(script_name)

    try:
        logger.info(f"Starting {script_name}")
        await script_func()
        logger.info(f"Completed {script_name} successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in {script_name}: {str(e)}", exc_info=True)
        sys.exit(1)
