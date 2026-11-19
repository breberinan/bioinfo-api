import logging

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.schemas import ProjectCreate
from app.services.project_service import (
    create_project,
    delete_project,
    list_projects,
)


class FailingSession:
    """Stand-in session whose commit always fails."""

    def __init__(self):
        self.rolled_back = False

    def add(self, obj):
        pass

    async def commit(self):
        raise SQLAlchemyError("boom")

    async def rollback(self):
        self.rolled_back = True


async def test_create_project_saves_and_returns_project(session):
    project = await create_project(
        session, ProjectCreate(name="Exome study", description="Pilot")
    )
    assert project.id is not None
    assert project.name == "Exome study"
    assert project.created_at is not None


async def test_list_projects_respects_skip_and_limit(session):
    for name in ["A", "B", "C"]:
        await create_project(session, ProjectCreate(name=name))
    page = await list_projects(session, skip=1, limit=1)
    assert [p.name for p in page] == ["B"]


async def test_delete_project_removes_it(session):
    project = await create_project(session, ProjectCreate(name="Temp"))
    assert await delete_project(session, project.id) is True
    assert await list_projects(session) == []


async def test_delete_project_returns_false_when_missing(session, caplog):
    with caplog.at_level(logging.WARNING):
        assert await delete_project(session, 999) is False
    assert "missing project" in caplog.text


async def test_create_project_rolls_back_and_logs_on_database_error(caplog):
    failing = FailingSession()
    with caplog.at_level(logging.ERROR), pytest.raises(SQLAlchemyError):
        await create_project(failing, ProjectCreate(name="X"))
    assert failing.rolled_back is True
    assert "Database error" in caplog.text


async def test_logs_never_contain_project_name(session, caplog):
    with caplog.at_level(logging.DEBUG):
        await create_project(session, ProjectCreate(name="confidential-name"))
    assert "Project created" in caplog.text
    assert "confidential-name" not in caplog.text
