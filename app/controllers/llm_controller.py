import ollama
from langdetect import detect, LangDetectException


class LLMController:
    """
    Handles interaction with Ollama LLM
    for academic summarization.
    """

    SUPPORTED_LANGUAGES = {
        "spanish": "es",
        "english": "en",
    }

    def __init__(
        self,
        text: str = "",
        model: str = "llama3.2:3b",
        options: dict | None = None,
        language: str = "spanish",
        header_weights: dict | None = None,
    ):
        self.text = text
        self.model = model
        self.options = options or {}
        self.language = self._normalize_language(language)
        self.header_weights = header_weights or {}
        self.summary = ""
    
    # ----------------------------------
    # Language Normalization
    # ----------------------------------

    def _normalize_language(self, language: str) -> str:
        language = language.lower()

        if language in ("es", "spa", "spanish", "español"):
            return "spanish"
        elif language in ("en", "eng", "english"):
            return "english"

        raise ValueError(f"Unsupported language: {language}")
    

    # ----------------------------------
    # Header Normalization
    # ----------------------------------

    def _format_header_weights(self) -> str:
        if not self.header_weights:
            return ""

        formatted = "\nSection priority weights:\n"

        for header, percentage in self.header_weights.items():
            formatted += f"- {header}: {round(percentage, 2)}% importance\n"

        return formatted

    # ----------------------------------
    # Model Validation
    # ----------------------------------

    def _validate_model(self) -> bool:
        try:
            models = ollama.list()
            available = [m.model for m in models.models]
            return self.model in available
        except Exception:
            return False

    # ----------------------------------
    # Prompt Builder
    # ----------------------------------

    def _build_prompt(self, max_tokens: int, translation: bool = False) -> str:

        extra_instructions = ""

        if self.header_weights:
            formatted_weights = self._format_header_weights()

            extra_instructions += (
                "\nThe article contains user-prioritized sections.\n"
                "Adjust the summary emphasis proportionally.\n"
                "Do NOT explicitly list the headers in the final output.\n"
                f"{formatted_weights}\n"
            )

        # Translation mode
        if translation:
            if self.language == "spanish":
                return (
                    "Translate the following text into Spanish faithfully and accurately. "
                    "Do not summarize, rephrase, or add new information."
                )
            else:
                return (
                    "Translate the following text into English faithfully and accurately. "
                    "Do not summarize, rephrase, or add new information."
                )

        # Summary generation
        if self.language == "spanish":
            return (
                "You are a scientific summarization model.\n"
                "Generate an academic summary in Spanish.\n\n"
                f"The summary must be clear, self-contained, and within approximately {max_tokens} tokens.\n\n"
                "Mandatory rules:\n"
                "- Third person\n"
                "- No invented information\n"
                "- No opinions\n"
                "- Do not mention figures or tables\n\n"
                "Integrate naturally:\n"
                "- Research problem\n"
                "- Methodology\n"
                "- Main results\n"
                "- Conclusions\n"
                f"{extra_instructions}\n"
                "IMPORTANT: The final output must be only in Spanish."
            )

        else:
            return (
                "You are a scientific summarization model.\n"
                "Generate an academic summary in English.\n\n"
                f"The summary must be clear, self-contained, and within approximately {max_tokens} tokens.\n\n"
                "Mandatory rules:\n"
                "- Third person\n"
                "- No invented information\n"
                "- No opinions\n"
                "- Do not mention figures or tables\n\n"
                "Integrate naturally:\n"
                "- Research problem\n"
                "- Methodology\n"
                "- Main results\n"
                "- Conclusions\n"
                f"{extra_instructions}\n"
                "IMPORTANT: The final output must be only in English."
            )

    # ----------------------------------
    # Ollama Interaction
    # ----------------------------------

    def _run_chat(self, system_prompt: str, user_text: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            options=self.options,
        )

        return response["message"]["content"]

    # ----------------------------------
    # Main Inference
    # ----------------------------------

    def run_inference(self) -> dict:

        if not self._validate_model():
            return {
                "status": "error",
                "message": f"Model '{self.model}' not available in Ollama.",
            }

        try:
            max_tokens = self.options.get("num_predict", 300)

            system_prompt = self._build_prompt(max_tokens)

            self.summary = self._run_chat(system_prompt, self.text)

            # Language detection
            try:
                detected_lang = detect(self.summary)
            except LangDetectException:
                detected_lang = None

            expected_lang = self.SUPPORTED_LANGUAGES[self.language]

            if detected_lang != expected_lang:

                translation_prompt = self._build_prompt(max_tokens, translation=True)
                self.summary = self._run_chat(translation_prompt, self.summary)

                try:
                    detected_lang = detect(self.summary)
                except LangDetectException:
                    detected_lang = None

                if detected_lang != expected_lang:
                    return {
                        "status": "warning",
                        "summary": self.summary,
                        "message": f"Language mismatch. Expected {expected_lang}, detected {detected_lang}",
                    }

            return {
                "status": "success",
                "summary": self.summary,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"LLM inference failed: {str(e)}",
            }

    # ----------------------------------
    # Utility
    # ----------------------------------

    def list_available_models(self) -> list | dict:
        try:
            models = ollama.list()
            return [m.model for m in models.models]
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not retrieve models: {str(e)}",
            }
