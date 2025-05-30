from quart import Blueprint, request, redirect
import os
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from backend.db.database import async_session
from backend.db.models import Produto

produtos_api = Blueprint("produtos_api", __name__ , url_prefix="/api/produtos")

UPLOAD_FOLDER = "frontend/static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@produtos_api.route("/adicionar", methods=["POST"])
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

@produtos_api.route("/editar/<int:produto_id>", methods=["GET", "POST"])
async def editar_produto(produto_id):
    form = await request.form
    print("sizes recebidos:", form.getlist("sizes"))
    arquivos = await request.files

    async with async_session() as session:
        produto = await session.get(Produto, produto_id)
        if not produto:
            return "Produto não encontrado", 404

        produto.name = form.get("name", produto.name)
        produto.price = float(form.get("price", produto.price))
        produto.category = form.get("category", produto.category)
        produto.sizes = form.getlist("sizes") or produto.sizes
        produto.stock = int(form.get("stock_quantity", produto.stock))

        imagem_principal = arquivos.get("principal")
        if imagem_principal:
            filename = imagem_principal.filename
            caminho = os.path.join(UPLOAD_FOLDER, filename)
            await imagem_principal.save(caminho)
            produto.principal = filename

        novas_secundarias = arquivos.getlist("secundarias")
        if novas_secundarias:
            novas = []
            for img in novas_secundarias:
                filename = img.filename
                caminho = os.path.join(UPLOAD_FOLDER, filename)
                await img.save(caminho)
                novas.append(filename)
            produto.secundarias = novas

        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print("ERRO AO EDITAR PRODUTO:", e)
            return "Erro ao editar produto", 5000

    return redirect("/admin")


@produtos_api.route("/remover/<int:produto_id>", methods=["DELETE"])
async def remover_produto(produto_id):
    async with async_session() as session:
        produto = await session.get(Produto, produto_id)
        if not produto:
            return {"error": "Produto não encontrado"}, 404
        
        await session.delete(produto)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            return {"error": f"Erro ao remover produto: {str(e)}"}, 500
        
        return {"success": True}

@produtos_api.route("/api/produtos/ids", methods=["GET"])
async def listar_ids():
    async with async_session() as session:
        result = await session.execute(select(Produto.id))
        ids = result.scalars().all()
        return {"ids": ids}