import asyncio
from quart import Quart
from dotenv import load_dotenv
from backend.api.routes import routes as pages
from backend.api.routes import carrossel_api
from backend.api.produtos import produtos_api
from backend.api.produtos import produtos_site
from backend.api.produtos import cart_api

load_dotenv()

app = Quart(__name__, static_folder='frontend/static', template_folder='frontend/templates')
app.secret_key = 'bananaazul'
app.register_blueprint(pages)
app.register_blueprint(produtos_api)
app.register_blueprint(produtos_site)
app.register_blueprint(carrossel_api)
app.register_blueprint(cart_api)

async def main():
    await asyncio.gather(
        app.run_task(host="0.0.0.0", port=5000),
    )

if __name__ == "__main__":
    asyncio.run(main())
