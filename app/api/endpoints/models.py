from fastapi import APIRouter
from app.controllers.llm_controller import LLMController

router = APIRouter()

@router.get("/")
async def get_models():
    controller = LLMController()
    models = controller.list_available_models()

    default_model = "llama3.2:3b" if "llama3.2:3b" in models else (
        models["models"][0] if models else "Models Not Found"
    )

    return {
        "default": default_model,
        "models": models
    }
