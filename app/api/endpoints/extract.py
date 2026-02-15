from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
from app.controllers.extract_headers import PDFSectionExtractor

router = APIRouter()

MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB

@router.post("/headers")
async def extract_headers(archivo_pdf: UploadFile = File(...)):

    file_content = await archivo_pdf.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The file exceeds the maximum allowed size of 30 MB."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(file_content)
        ruta_temp = temp.name

    try:
        extractor = PDFSectionExtractor("")
        headers = extractor.extract_pdf_headers(ruta_temp)

        return {
            "total": len(headers),
            "headers": headers
        }

    finally:
        os.remove(ruta_temp)
