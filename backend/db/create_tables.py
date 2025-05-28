import asyncio
from backend.db.database import engine  # o teu engine async
from backend.db.models import Base     # o Base do SQLAlchemy onde estão os modelos

async def criar_tabelas():
    async with engine.begin() as conn:
        # Esta linha cria as tabelas no banco se não existirem
        await conn.run_sync(Base.metadata.create_all)

    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    asyncio.run(criar_tabelas())
