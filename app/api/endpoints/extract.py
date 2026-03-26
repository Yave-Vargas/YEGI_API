from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import os
import uuid

from app.controllers.extract_headers import PDFSectionExtractor
from app.core.config import TEMP_DIR
from app.utils.file_utils import save_temp_file

import logging

logger = logging.getLogger("yegi.api")

router = APIRouter()

MAX_FILE_SIZE = 15 * 1024 * 1024  # limit

@router.post("/headers")
async def extract_headers(request: Request, archivo_pdf: UploadFile = File(...)):
    
    request_id = request.state.request_id
    logger.info(f"[{request_id}] Extract headers request | file={archivo_pdf.filename}")

    file_content = await archivo_pdf.read()
    file_size = len(file_content)

    logger.info(f"[{request_id}] File loaded | size={file_size}")

    if not archivo_pdf.filename.endswith(".pdf") or archivo_pdf.content_type != "application/pdf":
        raise HTTPException(400, "The file must be a valid PDF.")

    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File too large | size={file_size}")
        raise HTTPException(
            status_code=413,
            detail="The file exceeds the maximum allowed size of 15 MB."
        )

    ruta_temp = save_temp_file(file_content)

    logger.info(f"Temp file created")

    try:
        extractor = PDFSectionExtractor("")
        headers = extractor.extract_pdf_headers(ruta_temp)

        logger.info(f"Headers extracted | count={len(headers)}")

        return {
            "total": len(headers),
            "headers": headers
        }

    except Exception as e:
        logger.error(f"Extract headers failed | error={str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        if os.path.exists(ruta_temp):
            os.remove(ruta_temp)
            logger.info("Temp file removed")