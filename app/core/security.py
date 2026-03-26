from fastapi import Header, HTTPException, Request
from app.core.config import settings
import logging

logger = logging.getLogger("yegi.security")

def verify_api_key(request: Request, x_api_key: str = Header(None)):
    client_ip = request.client.host
    origin = request.headers.get("origin")

    if not x_api_key:
        logger.warning(f"Missing API key | IP: {client_ip}")
        raise HTTPException(status_code=401, detail="API Key missing")

    for key_type, keys in settings.API_KEYS.items():
        if x_api_key in keys:

            logger.info(
                f"Access granted | type={key_type} | IP={client_ip} | origin={origin}"
            )

            if key_type == "frontend":
                if origin not in settings.FRONTEND_ORIGINS:
                    logger.warning(
                        f"Forbidden origin | type={key_type} | origin={origin} | IP={client_ip}"
                    )
                    raise HTTPException(status_code=403, detail="Forbidden origin")

            return key_type

    logger.warning(f"Invalid API key | IP: {client_ip}")
    raise HTTPException(status_code=401, detail="Invalid API Key")