from fastapi import APIRouter, HTTPException, Request
from app.controllers.llm_controller import LLMController

import logging

logger = logging.getLogger("yegi.api")

router = APIRouter()

@router.get("/")
async def get_models(request: Request):
    request_id = request.state.request_id
    logger.info(f"[{request_id}] Get models request")

    try:
        controller = LLMController()
        models = controller.list_available_models()

        default_model = "llama3.2:3b" if "llama3.2:3b" in models else (
            models["models"][0] if models else "Models Not Found"
        )

        logger.info(f"Models retrieved | count={len(models) if models else 0}")

        return {
            "default": default_model,
            "models": models
        }

    except Exception as e:
        logger.error(f"Get models failed | error={str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")