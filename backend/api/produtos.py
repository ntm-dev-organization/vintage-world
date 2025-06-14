import os
import httpx
import base64
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from backend.db.database import async_session
from backend.db.models import Produto
from quart import Blueprint, request, redirect, abort, render_template
from backend.db.models import LojaEstado
from sqlalchemy.orm import selectinload

produtos_api = Blueprint("produtos_api", __name__ , url_prefix="/api/produtos")

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
if not IMGUR_CLIENT_ID:
    raise RuntimeError("Variavel nao esta definida")

async def upload_to_imgur(img_bytes: bytes) -> str:
    encoded_image = base64.b64encode(img_bytes).decode()

    headers = {
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
    }
    data = {
        "image": encoded_image,
        "type": "base64"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.imgur.com/3/image", headers=headers, data=data)

    if response.status_code == 200:
        json_resp = response.json()
        return json_resp['data']['link']
    else:
        print("Erro ao enviar imagem para Imgur:", response.text)
        return None

@produtos_api.route("/adicionar", methods=["POST"])
async def adicionar_produto():
    form = await request.form
    files = await request.files
    imagens = files.getlist("images")

    name = form.get("name", "").strip()
    category = form.get("category")
    stripe_num = form.get("stripe_product_id", "").strip()
    tipo = form.get("tipo_produto")
    stock = int(form.get("stock_quantity", 0))
    price = float(form.get("price_display", "0").replace(",", "."))

    if category not in ("yourself", "resell"):
        abort(400, "Categoria inválida")
    if category == "yourself" and tipo not in ("camisola", "calcas"):
        abort(400, "Tipo de produto inválido")

    sizes = []
    if category == "yourself":
        if tipo == "camisola":
            sizes = form.getlist("sizes")
        else:
            num = form.get("calcas_numero")
            if num:
                sizes = [str(int(num))]
    else:
        sizes = form.getlist("sizes")

    principal = None
    secundarias = []

    for idx, img in enumerate(imagens):
        if img and img.filename:
            img_bytes = img.read()
            url = await upload_to_imgur(img_bytes)
            if not url:
                abort(500, "Erro ao enviar imagem para Imgur.")
            if idx == 0:
                principal = url
            else:
                secundarias.append(url)

    novo = Produto(
        name=name,
        price=price,
        sizes=sizes,
        category=category,
        stripe_num=stripe_num,
        stock=stock,
        principal=principal,
        secundarias=secundarias
    )

    async with async_session() as s:
        try:
            s.add(novo)
            await s.commit()
        except SQLAlchemyError:
            await s.rollback()
            abort(500, "Erro a guardar produto no BD")

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
        if imagem_principal and imagem_principal.filename:
            img_bytes = imagem_principal.read()
            url = await upload_to_imgur(img_bytes)
            if not url:
                abort(500, "Erro ao enviar imagem principal para Imgur.")
            produto.principal = url

        novas_secundarias = arquivos.getlist("secundarias")
        if novas_secundarias:
            novas_urls = []
            for img in novas_secundarias:
                if img and img.filename:
                    img_bytes = img.read()
                    url = await upload_to_imgur(img_bytes)
                    if not url:
                        abort(500, "Erro ao enviar imagem secundária para Imgur.")
                    novas_urls.append(url)
            produto.secundarias = novas_urls

        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print("ERRO AO EDITAR PRODUTO:", e)
            return "Erro ao editar produto", 500

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
    
#produtos para o site

produtos_site = Blueprint("produtos_site", __name__)

@produtos_site.route("/produtos/<categoria>")
async def listar_por_categoria(categoria):
    if categoria not in ("resell", "yourself"):
        return abort(404)

    async with async_session() as session:
        try:
            result = await session.execute(select(Produto).where(Produto.category == categoria))
            produtos = result.scalars().all()
        except SQLAlchemyError as e:
            print("Erro a buscar produtos:", e)
            produtos = []

    return await render_template("product.html", produtos=produtos, categoria=categoria)

@produtos_site.route("/produto/<int:produto_id>")
async def mostrar_produto(produto_id):
    async with async_session() as session:
        produto = await session.get(Produto, produto_id)
        if not produto:
            return "Produto não encontrado", 404

        sizes = produto.sizes
        if isinstance(sizes, str):
            import json
            sizes = json.loads(sizes)

        return await render_template("product.html", produto=produto, sizes=sizes)
    
@produtos_site.route("/resell")
async def resell():
    async with async_session() as session:
        result = await session.execute(select(Produto).where(Produto.category == "resell"))
        produtos = result.scalars().all()

    return await render_template("resell.html", produtos=produtos)

@produtos_site.route("/yourself")
async def yourself():
    async with async_session() as session:
        result = await session.execute(
            select(LojaEstado).where(LojaEstado.id == 1).options(selectinload(LojaEstado.status))
        )
        estado = result.scalars().first()

        if not estado or not estado.status or estado.status.name != "on":
            return await render_template("soon.html")

        result = await session.execute(select(Produto).where(Produto.category == "resell"))
        produtos = result.scalars().all()

    return await render_template("yourself.html", produtos=produtos)