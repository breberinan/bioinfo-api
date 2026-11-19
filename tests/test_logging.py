import logging

from app.core.logging import setup_logging


def test_setup_logging_sets_root_level():
    setup_logging("debug")
    assert logging.getLogger().level == logging.DEBUG
    setup_logging("INFO")
    assert logging.getLogger().level == logging.INFO


async def test_each_request_is_logged(client, caplog):
    with caplog.at_level(logging.INFO):
        await client.get("/health")
    assert "GET /health -> 200" in caplog.text
