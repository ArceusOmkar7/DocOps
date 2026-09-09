import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://project_agent:agentspassword@localhost/ai_docs_orch"

async def main():
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
        tables = [r[0] for r in result]
        print("TABLES:", tables)
        print()
        for t in ["organizations", "clients", "client_members", "documents", "workflows", "workflow_documents", "workflow_document_requirements"]:
            try:
                r = await session.execute(text(f"SELECT COUNT(*) FROM {t}"))
                count = r.scalar()
                print(f"  {t}: {count} rows")
                if count > 0 and count < 10:
                    rows = await session.execute(text(f"SELECT * FROM {t} LIMIT 5"))
                    cols = rows.keys()
                    for row in rows:
                        print(f"    {dict(zip(cols, row))}")
            except Exception as e:
                print(f"  {t}: ERROR - {e}")
    await engine.dispose()

asyncio.run(main())
