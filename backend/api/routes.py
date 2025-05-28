from quart import Quart, redirect, request, session, render_template, send_from_directory, url_for, Blueprint
from dotenv import load_dotenv
from backend.api.produtos import listar_produtos

load_dotenv()

app = Quart(__name__, static_folder='frontend/static', template_folder='frontend/templates')
routes = Blueprint('routes', __name__)

@routes.route("/", methods=["GET", "POST"])
async def index():
    return await render_template("index.html")

@routes.route("/resell")
async def resell():
    return await render_template("resell.html")

@routes.route("/yourself")
async def yourself():
    return await render_template("yourself.html")

@routes.route("/soon")
async def soon():
    return await render_template("soon.html")

@routes.route('/frontend/static/<path:filename>')
async def static_files(filename):
    return await send_from_directory('frontend/static', filename)

#API

ADMIN_PASSWORD = "senha123"

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


@routes.route("/admin")
async def admin_painel():
    if not session.get("admin_logged_in"):
        return redirect(url_for("routes.admin_login"))

    produtos = listar_produtos()
    return await render_template("admin.html", produtos=produtos)

@routes.route("/admin/logout")
async def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.admin_login"))

