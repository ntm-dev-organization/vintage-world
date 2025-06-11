import os
from quart import Quart, redirect, request, session, render_template, send_from_directory, url_for, Blueprint, Response, abort
from dotenv import load_dotenv
from backend.api.produtos import listar_produtos
from backend.db.database import async_session
from backend.db.models import LojaEstado, Status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


load_dotenv()

app = Quart(__name__, static_folder='frontend/static', template_folder='frontend/templates')
routes = Blueprint('routes', __name__)

@routes.route("/", methods=["GET", "POST"])
async def index():
    return await render_template("index.html")

@routes.route("/yourself")
async def yourself():
    return await render_template("yourself.html")

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
'''
carrossel_routes = Blueprint('carrossel_routes', __name__)

@carrossel_routes.route('/api/carrossel/imagens', methods=['GET'])
async def listar_imagens():
    async with async_session() as session:
        result = await session.execute(select(CarouselImage))
        imagens = result.scalars().all()

    imagens_resumo = [
        {
            "id": img.id,
            "filename": img.filename,
            "url": f"/api/carrossel/imagens/{img.id}/img"
        }
        for img in imagens
    ]
    return jsonify(imagens_resumo)


@carrossel_routes.route('/api/carrossel/imagens', methods=['POST'])
async def adicionar_imagem():
    form = await request.form
    if 'imagem' not in form:
        return Response('Nenhuma imagem enviada', status=400)

    file = (await request.files)['imagem']
    if file.filename == '':
        return Response('Ficheiro inválido', status=400)

    # Validação simples do content-type
    if not file.content_type.startswith('image/'):
        return Response('Formato de imagem não suportado', status=400)

    data = await file.read()
    nova_imagem = CarouselImage(
        id=str(uuid.uuid4()),
        filename=file.filename,
        content_type=file.content_type,
        data=data
    )

    async with async_session() as session:
        session.add(nova_imagem)
        await session.commit()

    return Response('Imagem adicionada com sucesso!', status=200)


@carrossel_routes.route('/api/carrossel/imagens/<imagem_id>/img', methods=['GET'])
async def servir_imagem(imagem_id):
    async with async_session() as session:
        imagem = await session.get(CarouselImage, imagem_id)
        if not imagem:
            return Response('Imagem não encontrada', status=404)

        return Response(imagem.data, content_type=imagem.content_type)


@carrossel_routes.route('/api/carrossel/imagens/<imagem_id>', methods=['DELETE'])
async def remover_imagem(imagem_id):
    async with async_session() as session:
        imagem = await session.get(CarouselImage, imagem_id)
        if not imagem:
            return Response('Imagem não encontrada', status=404)
        await session.delete(imagem)
        await session.commit()
    return Response('Imagem removida', status=200)
    '''