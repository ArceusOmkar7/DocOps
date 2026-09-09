"""Pytest configuration and cleanup fixtures to keep development database clean."""

import asyncio
import pytest
from sqlalchemy import delete
from app.db.engine import async_session_factory
from app.models.organization import Organization
from app.models.client import Client


@pytest.fixture(autouse=True, scope="session")
def cleanup_test_data():
    """Autouse fixture that runs once per test session and cleans up test organizations."""
    yield
    # Clean up test organizations created by pytest tests
    async def _cleanup():
        async with async_session_factory() as db:
            await db.execute(delete(Organization).where(Organization.slug.startswith("test-org-")))
            await db.execute(delete(Client).where(Client.name == "General Client"))
            await db.commit()

    asyncio.run(_cleanup())
