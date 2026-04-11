from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
import tempfile
import os
import json
import uuid

from app.core.config import TEMP_DIR
from app.core.job_queue import create_job, get_job_result
from app.services.summarization_service import SummarizationService
from app.core.security import verify_api_key
from app.utils.file_utils import save_temp_file

import logging
logger = logging.getLogger("yegi.api")

router = APIRouter()

MAX_FILE_SIZE = 15 * 1024 * 1024

# HELPERS

def validate_file(file: UploadFile, file_size: int, api_key_type: str):
    if not file.filename.endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(400, "The file must be a valid PDF.")

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    if api_key_type == "public" and file_size > 10 * 1024 * 1024:
        raise HTTPException(403, "Public API limit exceeded (10MB max)")


def validate_params(temperature, top_p, num_predict):
    if num_predict > 2000:
        raise HTTPException(400, "num_predict too high")
    if temperature > 1:
        raise HTTPException(400, "temperature too high")
    if top_p > 1:
        raise HTTPException(400, "top_p too high")


def parse_header_weights(header_weights: str):
    try:
        data = json.loads(header_weights)

        if not isinstance(data, dict):
            raise ValueError("Must be a dictionary")

        for k, v in data.items():
            if not isinstance(v, (int, float)):
                raise ValueError(f"{k} must be numeric")
            if v < 0:
                raise ValueError(f"{k} cannot be negative")

        total = sum(data.values())

        if total == 0 and data:
            raise ValueError("At least one weight must be > 0")

        if total > 0:
            data = {k: (v / total) * 100 for k, v in data.items()}

        return data

    except Exception as e:
        raise HTTPException(400, f"Invalid header_weights: {str(e)}")

def build_options(
    temperature,
    top_p,
    repeat_penalty,
    repeat_last_n,
    num_predict,
    seed=None
):
    options = {
        "temperature": temperature,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "repeat_last_n": repeat_last_n,
        "num_predict": num_predict,
    }

    if seed is not None:
        options["seed"] = seed

    return options

# SYNC ENDPOINT
@router.post("/")
async def summarizer(
    request: Request,
    api_key_type: str = Depends(verify_api_key),
    archivo_pdf: UploadFile = File(...),
    model: str = Form("llama3.2:3b"),
    temperature: float = Form(0.1),
    top_p: float = Form(0.7),
    repeat_penalty: float = Form(1.1),
    repeat_last_n: int = Form(32),
    num_predict: int = Form(1000),
    seed: int | None = Form(None),
    language: str = Form("español"),
    header_weights: str = Form("{}"),
):
    request_id = request.state.request_id

    file_content = await archivo_pdf.read()
    file_size = len(file_content)

    validate_file(archivo_pdf, file_size, api_key_type)
    validate_params(temperature, top_p, num_predict)
    header_weights_dict = parse_header_weights(header_weights)

    ruta_archivo = save_temp_file(file_content)
    options_dict = build_options(
        temperature,
        top_p,
        repeat_penalty,
        repeat_last_n,
        num_predict,
        seed
    )

    service = SummarizationService()

    try:
        result = service.summarize(
            file_path=ruta_archivo,
            model=model,
            options_dict=options_dict,
            language=language,
            header_weights=header_weights_dict,
            request_id=request_id
        )
        return result

    except Exception as e:
        logger.error(f"[{request_id}] Summarization failed | error={str(e)}")
        raise HTTPException(500, "Internal server error")

    finally:
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
            logger.info("Temp file removed")

# Workers

@router.post("/async")
async def summarizer_async(
    request: Request,
    api_key_type: str = Depends(verify_api_key),
    archivo_pdf: UploadFile = File(...),
    model: str = Form("llama3.2:3b"),
    temperature: float = Form(0.1),
    top_p: float = Form(0.7),
    repeat_penalty: float = Form(1.1),
    repeat_last_n: int = Form(32),
    num_predict: int = Form(1000),
    seed: int | None = Form(None),
    language: str = Form("español"),
    header_weights: str = Form("{}"),
):
    request_id = request.state.request_id

    file_content = await archivo_pdf.read()
    file_size = len(file_content)

    validate_file(archivo_pdf, file_size, api_key_type)
    validate_params(temperature, top_p, num_predict)
    header_weights_dict = parse_header_weights(header_weights)

    ruta_archivo = save_temp_file(file_content)
    options_dict = build_options(
        temperature,
        top_p,
        repeat_penalty,
        repeat_last_n,
        num_predict,
        seed
    )

    job_id = create_job({
        "file_path": ruta_archivo,
        "model": model,
        "options_dict": options_dict,
        "language": language,
        "header_weights": header_weights_dict,
        "request_id": request_id
    })

    logger.info(f"[{request_id}] Job created | job_id={job_id}")

    return {"job_id": job_id}

@router.get("/result/{job_id}")
def get_result(job_id: str):
    return get_job_result(job_id)