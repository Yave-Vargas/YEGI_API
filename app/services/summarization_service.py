from app.controllers.api_controller import APIController


class SummarizationService:
    def summarize(
        self,
        file_path: str,
        model: str,
        options_dict: dict,
        language: str,
        header_weights: dict,
    ):

        controller = APIController(
            file_path=file_path,
            model=model,
            options=options_dict,
            language=language,
            header_weights=header_weights,
        )

        respuesta = controller.process()

        return respuesta
