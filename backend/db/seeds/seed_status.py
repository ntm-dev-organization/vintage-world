import asyncio
from sqlalchemy.future import select
from backend.db.database import async_session
from backend.db.models import Status

async def seed_status():
    async with async_session() as session:
        existing = await session.execute(
            select(Status).where(Status.name.in_(["on", "off"]))
        )
        existing_status = existing.scalars().all()
        nomes_existentes = {s.name for s in existing_status}

        if "on" not in nomes_existentes:
            session.add(Status(name="on", description="Loja aberta"))
        if "off" not in nomes_existentes:
            session.add(Status(name="off", description="Loja fechada"))

        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_status())
