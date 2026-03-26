import logging
import time

from app.controllers.api_controller import APIController

logger = logging.getLogger("yegi.service")


class SummarizationService:
    def summarize(
        self,
        file_path: str,
        model: str,
        options_dict: dict,
        language: str,
        header_weights: dict,
        request_id: str = None,
    ):
        start_time = time.time()
        logger.info(
            f"[{request_id}] Start summarization | model={model} | language={language}"
        )

        try:
            controller = APIController(
                file_path=file_path,
                model=model,
                options=options_dict,
                language=language,
                header_weights=header_weights,
            )
            respuesta = controller.process()
            duration = round(time.time() - start_time, 2)
            logger.info(
                f"Summarization completed | model={model} | duration={duration}s"
            )
            return respuesta

        except Exception as e:
            duration = round(time.time() - start_time, 2)
            logger.error(
                f"Summarization failed | model={model} | duration={duration}s | error={str(e)}"
            )
            raise