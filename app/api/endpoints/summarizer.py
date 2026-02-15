from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile
import os
import json
from app.services.summarization_service import SummarizationService

router = APIRouter()

MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB

@router.post("/")
async def summarizer(
    archivo_pdf: UploadFile = File(...),
    model: str = Form(default="llama3.2:3b"),
    temperature: float = Form(default=0.5),
    top_p: float = Form(default=0.8),
    repeat_penalty: float = Form(default=1.1),
    repeat_last_n: int = Form(default=32),
    num_predict: int = Form(default=1000),
    language: str = Form(default="español"),
    header_weights: str = Form(default="{}"),
):

    if not archivo_pdf.filename.endswith(".pdf") or archivo_pdf.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF válido."
        )

    file_content = await archivo_pdf.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The file exceeds the maximum allowed size of 30 MB."
        )

    try:
        header_weights_dict = json.loads(header_weights)

        if not isinstance(header_weights_dict, dict):
            raise ValueError("header_weights must be a dictionary")

        for key, value in header_weights_dict.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"Weight for '{key}' must be numeric")

            if value < 0:
                raise ValueError(f"Weight for '{key}' cannot be negative")

        total_weight = sum(header_weights_dict.values())
        if total_weight == 0 and header_weights_dict:
            raise ValueError("At least one header weight must be greater than 0")

        if total_weight > 0:
            header_weights_dict = {
                key: (value / total_weight) * 100
                for key, value in header_weights_dict.items()
            }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid header_weights: {str(e)}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(file_content)
        ruta_archivo = temp.name

    options_dict = {
        "temperature": temperature,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "repeat_last_n": repeat_last_n,
        "num_predict": num_predict,
    }

    service = SummarizationService()

    try:
        respuesta = service.summarize(
            file_path=ruta_archivo,
            model=model,
            options_dict=options_dict,
            language=language,
            header_weights=header_weights_dict,
        )
        return respuesta

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error."
        )

    finally:
        os.remove(ruta_archivo)
