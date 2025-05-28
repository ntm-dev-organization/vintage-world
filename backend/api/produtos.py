from quart import Blueprint, request, redirect
import os
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from backend.db.database import async_session
from backend.db.models import Produto

produtos_api = Blueprint("produtos_api", __name__)

UPLOAD_FOLDER = "frontend/static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@produtos_api.route("/api/produtos/adicionar", methods=["POST"])
async def adicionar_produto():
    form = await request.form
    arquivos = await request.files
    imagens = arquivos.getlist("images")

    name = form.get("name")
    price = float(form.get("price"))
    sizes = form.getlist("sizes")
    category = form.get("category")
    stripe_num = form.get("stripe_product_id")
    stock = int(form.get("stock_quantity", 0))

    principal = None
    secundarias = []

    for idx, imagem in enumerate(imagens):
        if imagem:
            filename = imagem.filename
            caminho = os.path.join(UPLOAD_FOLDER, filename)
            await imagem.save(caminho)
            if idx == 0:
                principal = filename
            else:
                secundarias.append(filename)

    novo_produto = Produto(
        name=name,
        price=price,
        sizes=sizes,
        category=category,
        stripe_num=stripe_num,
        stock=stock,
        principal=principal,
        secundarias=secundarias
    )

    async with async_session() as session:
        try:
            session.add(novo_produto)
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            print("Erro ao guardar no DB:", e)
            return {"error": "Erro ao guardar no banco de dados"}, 500

    return redirect("/admin")


async def listar_produtos():
    async with async_session() as session:
        try:
            result = await session.execute(select(Produto))
            produtos = result.scalars().all()
            return produtos
        except SQLAlchemyError as e:
            print("Erro ao listar produtos:", e)
            return []
