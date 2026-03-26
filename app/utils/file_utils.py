import uuid
from app.core.config import TEMP_DIR

def save_temp_file(file_content: bytes) -> str:
    file_path = TEMP_DIR / f"{uuid.uuid4()}.pdf"

    with open(file_path, "wb") as f:
        f.write(file_content)

    return str(file_path)