import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.events import router as events_router
from .api.stats import router as stats_router
from .database import init_db
from .honeypots.ftp import start_ftp_honeypot
from .honeypots.http import start_http_honeypot
from .honeypots.ssh import start_ssh_honeypot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialized")

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(start_ssh_honeypot()),
        loop.create_task(start_ftp_honeypot()),
        loop.create_task(start_http_honeypot()),
    ]
    logger.info("Honeypot services started")

    yield

    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(title="Canaris Honeypot", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)
app.include_router(stats_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "services": ["ssh", "ftp", "http"]}
