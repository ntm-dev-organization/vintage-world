from quart import Quart, redirect, request, session, render_template, send_from_directory, url_for, jsonify, Blueprint
import requests
from dotenv import load_dotenv

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
