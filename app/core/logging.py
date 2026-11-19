import logging.config

# Third-party libraries can print query values (user data) at DEBUG level,
# so we keep them quiet unless something goes wrong.
NOISY_LIBRARIES = ("aiosqlite", "sqlalchemy.engine", "asyncpg")


def setup_logging(level: str = "INFO") -> None:
    """Send all application logs to stdout in one consistent format."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {name: {"level": "WARNING"} for name in NOISY_LIBRARIES},
            "root": {"level": level.upper(), "handlers": ["console"]},
        }
    )
