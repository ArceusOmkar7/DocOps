"""Script to clean up leftover test organizations and duplicate rows from dev database."""

import asyncio
from sqlalchemy import delete, select
from app.db.engine import async_session_factory
from app.models.organization import Organization
from app.models.client import Client


async def clean_db() -> None:
    async with async_session_factory() as db:
        # 1. Delete all organizations where slug is NOT 'default-org'
        # Cascades to all test clients, test workflows, test documents created during pytest
        stmt = delete(Organization).where(Organization.slug != "default-org")
        res = await db.execute(stmt)

        # 2. Delete any "General Client" created by fallback
        stmt_gen = delete(Client).where(Client.name == "General Client")
        await db.execute(stmt_gen)

        await db.commit()
        print("[CLEAN] Successfully removed test organizations and duplicate client rows!")


if __name__ == "__main__":
    asyncio.run(clean_db())
