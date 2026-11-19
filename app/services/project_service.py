import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project
from app.schemas import ProjectCreate

logger = logging.getLogger(__name__)


async def _commit(session: AsyncSession, action: str) -> None:
    """Commit, and roll back + log if the database rejects the change."""
    try:
        await session.commit()
    except SQLAlchemyError:
        logger.exception("Database error while trying to %s", action)
        await session.rollback()
        raise


async def create_project(session: AsyncSession, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    session.add(project)
    await _commit(session, "create a project")
    await session.refresh(project)
    logger.info("Project created: id=%s", project.id)
    return project


async def list_projects(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Project]:
    logger.debug("Listing projects: skip=%s limit=%s", skip, limit)
    result = await session.execute(
        select(Project).order_by(Project.id).offset(skip).limit(limit)
    )
    projects = list(result.scalars().all())
    logger.debug("Found %s project(s)", len(projects))
    return projects


async def delete_project(session: AsyncSession, project_id: int) -> bool:
    project = await session.get(Project, project_id)
    if project is None:
        logger.warning("Delete requested for missing project: id=%s", project_id)
        return False
    await session.delete(project)
    await _commit(session, "delete a project")
    logger.info("Project deleted: id=%s", project_id)
    return True
