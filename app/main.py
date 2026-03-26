from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
import app.workers.job_worker

import logging
import time
import uuid

setup_logging()
logger = logging.getLogger("yegi.access")

app = FastAPI(
    title="YEGI API",
    version="0.2.0",
    redirect_slashes=False
)


app.add_middleware(
    CORSMiddleware,
    #allow_origins=["*"],
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    request.state.request_id = request_id

    logger.info(f"[{request_id}] START {request.method} {request.url.path}")

    try:
        response = await call_next(request)

    except Exception as e:
        duration = round(time.time() - start_time, 2)
        logger.error(
            f"[{request_id}] ERROR {request.method} {request.url.path} "
            f"time={duration}s error={str(e)}"
        )
        raise

    duration = round(time.time() - start_time, 2)

    logger.info(
        f"[{request_id}] END {request.method} {request.url.path} "
        f"status={response.status_code} time={duration}s"
    )

    return response

app.include_router(api_router, prefix="/api")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Unhandled exception: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/health")
def health():
    return {"status": "ok"}
