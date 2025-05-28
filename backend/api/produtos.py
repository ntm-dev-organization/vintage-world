from quart import Blueprint, request, redirect
import os
import json

produtos_api = Blueprint("produtos_api", __name__)
UPLOAD_FOLDER = "frontend/static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ADMIN_PASSWORD = "senha123"

DB_PATH = "backend/db/products.json"

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

    produto = {
        "name": name,
        "price": price,
        "sizes": sizes,
        "category": category,
        "stripe_num": stripe_num,
        "stock": stock,
        "principal": principal,
        "secundarias": secundarias
    }

    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            try:
                produtos = json.load(f)
            except json.JSONDecodeError:
                produtos = []
    else:
        produtos = []

    produtos.append(produto)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=2, ensure_ascii=False)

    return redirect("/admin")


def listar_produtos():
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        return []

    with open(DB_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []