import asyncio
from sqlalchemy import select
from backend.db.database import async_session
from backend.db.models import LojaEstado, Status

async def seed_loja_estado():
    async with async_session() as session:
        # Pega o status 'off' como objeto ORM
        result = await session.execute(select(Status).where(Status.name == "off"))
        status_off = result.scalars().first()

        if not status_off:
            print("Status 'off' não encontrado. Executa primeiro o seed_status.py")
            return

        # Cria estado inicial da loja
        loja_estado = LojaEstado(status_id=status_off.id)
        session.add(loja_estado)
        await session.commit()
        print("Estado inicial da loja criado com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed_loja_estado())

#comando: python -m backend.db.seeds.seed_loja_estado 
