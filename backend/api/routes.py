import os
import base64
import httpx
from quart import Quart, redirect, request, session, render_template, send_from_directory, url_for, Blueprint, Response, abort, jsonify
from dotenv import load_dotenv
from backend.api.produtos import listar_produtos
from backend.db.database import async_session
from backend.db.models import LojaEstado, Status, CarrosselImagem
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError


load_dotenv()

app = Quart(__name__, static_folder='frontend/static', template_folder='frontend/templates')
routes = Blueprint('routes', __name__)

@routes.route("/", methods=["GET", "POST"])
async def index():
    return await render_template("index.html")

@routes.route("/soon")
async def soon():
    return await render_template("soon.html")

@routes.route("/csoon")
async def csoon():
    return await render_template("csoon.html")

@routes.route('/frontend/static/<path:filename>')
async def static_files(filename):
    return await send_from_directory('frontend/static', filename)

#API

ADMIN_PASSWORD = os.getenv("password")

@routes.route("/admin/login", methods=["GET", "POST"])
async def admin_login():
    if request.method == "POST":
        form = await request.form
        password = form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("routes.admin_painel"))
        else:
            return await render_template("admin_login.html", error="Palavra-passe incorreta.")

    return await render_template("admin_login.html")


@routes.route("/admin", methods=["GET", "POST"])
async def admin_painel():
    if not session.get("admin_logged_in"):
        return redirect(url_for("routes.admin_login"))

    produtos = await listar_produtos()
    produtos_dict = [produto.to_dict() for produto in produtos]
    return await render_template("admin.html", produtos=produtos_dict)

@routes.route("/admin/logout")
async def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.admin_login"))

# loja off/on

@routes.route("/api/loja/estado", methods=["GET"])
async def obter_estado_loja():
    async with async_session() as session:
        result = await session.execute(
            select(LojaEstado).where(LojaEstado.id == 1).options(selectinload(LojaEstado.status))
        )
        estado = result.scalars().first()

        if not estado or not estado.status:
            return Response("fechada", status=404, content_type="text/plain")

        aberta = estado.status.name == "on"
        return Response("aberta" if aberta else "fechada", status=200, content_type="text/plain")



@routes.route("/api/loja/estado", methods=["POST"])
async def atualizar_estado_loja():
    data = await request.get_json()
    if not data or "aberta" not in data:
        return Response("Erro: falta o campo 'aberta'", status=400, content_type="text/plain")

    aberta = data["aberta"]
    if not isinstance(aberta, bool):
        return Response("Erro: 'aberta' deve ser um booleano", status=400, content_type="text/plain")

    status_nome = "on" if aberta else "off"

    async with async_session() as session:
        result = await session.execute(select(Status).where(Status.name == status_nome))
        status_obj = result.scalars().first()

        if not status_obj:
            return Response(f"Erro: status '{status_nome}' não existe", status=500)

        result = await session.execute(select(LojaEstado).where(LojaEstado.id == 1))
        loja_estado = result.scalars().first()

        if loja_estado:
            loja_estado.status_id = status_obj.id
        else:
            loja_estado = LojaEstado(id=1, status_id=status_obj.id)
            session.add(loja_estado)

        await session.commit()

    return Response("Estado da loja atualizado com sucesso!", status=200, content_type="text/plain")

#carrousel
carrossel_api = Blueprint("carrossel_api", __name__, url_prefix="/api/carrossel")

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
if not IMGUR_CLIENT_ID:
    raise RuntimeError("Variavel IMGUR_CLIENT_ID não definida")

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

@carrossel_api.route("/carrouselimg", methods=["POST"])
async def adicionar_imagem():
    files = await request.files
    imagem = files.get("imagem")
    if not imagem or not imagem.filename:
        abort(400, "Imagem não enviada")

    img_bytes = imagem.read()
    url = await upload_to_imgur(img_bytes)
    if not url:
        abort(500, "Erro ao enviar imagem para Imgur.")

    nova_imagem = CarrosselImagem(url=url, filename=imagem.filename)
    async with async_session() as session:
        try:
            session.add(nova_imagem)
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            print("Erro ao guardar imagem no BD:", e)
            abort(500, "Erro ao guardar imagem no banco de dados")

    return jsonify({
        "id": nova_imagem.id,
        "url": url,
        "filename": imagem.filename
    })

@carrossel_api.route("/carrouselimg", methods=["GET"])
async def listar_imagens():
    async with async_session() as session:
        try:
            result = await session.execute(select(CarrosselImagem))
            imagens = result.scalars().all()

            return jsonify([
                {
                    "id": img.id,
                    "url": img.url,
                    "filename": img.filename
                } for img in imagens
            ])
        except SQLAlchemyError as e:
            print("Erro ao listar imagens do carrossel:", e)
            abort(500, "Erro ao listar imagens")

@carrossel_api.route("/carrouselimg/<int:id>", methods=["DELETE"])
async def remover_imagem(id):
    async with async_session() as session:
        try:
            imagem = await session.get(CarrosselImagem, id)
            if not imagem:
                abort(404, "Imagem não encontrada")

            await session.delete(imagem)
            await session.commit()
            return "", 204
        except SQLAlchemyError as e:
            await session.rollback()
            print("Erro ao remover imagem:", e)
            abort(500, "Erro ao remover imagem")