import functools
import logging
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class Timer:
    """with bloki ichidagi kod qancha vaqt olganini o'lchaydi."""

    def __init__(self, label: str):
        self.label = label
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        logger.info(
            "[%s] bajarilish vaqti: %.4f soniya", self.label, self.elapsed
        )

    @property
    def elapsed(self) -> float:
        """Ketingan umumiy vaqtni (soniyada) qaytaradi."""
        if self.start_time is None:
            return 0.0
        if self.end_time is None:
            return time.perf_counter() - self.start_time
        return self.end_time - self.start_time


def timed(func: Callable) -> Callable:
    """Funksiya bajarilish vaqtini o'lchab logga/ekranga yozuvchi dekorator."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with Timer(func.__name__):
            return func(*args, **kwargs)

    return wrapper