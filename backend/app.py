from quart import Quart
import asyncio
from dotenv import load_dotenv
from routes import routes

load_dotenv()

app = Quart(__name__, static_folder='frontend/static', template_folder='frontend/templates')
app.secret_key = 'bananaazul'
app.register_blueprint(routes)

async def main():
    await asyncio.gather(
        app.run_task(host="0.0.0.0", port=5000),
    )

if __name__ == "__main__":
    asyncio.run(main())
