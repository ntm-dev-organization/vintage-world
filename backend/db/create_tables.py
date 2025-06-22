import asyncio
from backend.db.database import engine, Base
from backend.db.models import CarrosselImagem, Produto, Status, LojaEstado

async def criar_tabelas():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    asyncio.run(criar_tabelas())

#comando: python -m backend.db.create_tables