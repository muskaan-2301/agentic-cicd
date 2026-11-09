"""App settings. Values can be overridden with environment variables.

Later (Day 4) the fault-injection script will change some of these
values to simulate "bad config" failures.
"""
import os


class Config:
    MAX_TITLE_LENGTH = int(os.getenv("MAX_TITLE_LENGTH", "100"))
    MAX_TASKS = int(os.getenv("MAX_TASKS", "1000"))
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "50"))
    VALID_STATUSES = ("todo", "in_progress", "done")
    VALID_PRIORITIES = (1, 2, 3, 4, 5)
