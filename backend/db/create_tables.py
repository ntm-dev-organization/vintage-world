import asyncio
from sqlalchemy import select
from backend.db.database import engine, async_session
from backend.db.models import Base, Status

async def criar_tabelas():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tabelas criadas com sucesso!")

async def inserir_status_default():
    async with async_session() as session:
        result = await session.execute(select(Status))
        status_existentes = result.scalars().all()

        if not status_existentes:
            session.add_all([
                Status(name="on", description="Loja aberta"),
                Status(name="off", description="Loja fechada")
            ])
            await session.commit()
            print("Estados 'on' e 'off' inseridos!")
        else:
            print("Estados já existem, nada foi inserido.")

async def main():
    await criar_tabelas()
    await inserir_status_default()

if __name__ == "__main__":
    asyncio.run(main())
