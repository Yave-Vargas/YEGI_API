from .pdf_extractor import PDFExtractor
from .text_preprocessor import TextPreprocessor
from .llm_controller import LLMController
from .generate_json import JSONResponse
from .error_validator import ErrorValidator

class APIController:
    """
    Main controller responsible for orchestrating
    the PDF summarization pipeline.
    """

    def __init__(
        self,
        file_path: str,
        model: str,
        options: dict,
        language: str = "spanish",
        header_weights: dict | None = None,
    ):
        self.file_path = file_path
        self.model = model
        self.options = options
        self.language = language
        self.header_weights = header_weights or {}

        self.extracted_text = ""
        self.cleaned_text = ""
        self.summary = ""
        self.warnings = []
        self.response = {}

    # -----------------------------
    # Validation
    # -----------------------------

    def _validate_pdf(self) -> bool:
        return self.file_path.lower().endswith(".pdf")

    # -----------------------------
    # Main Process
    # -----------------------------

    def process(self) -> dict:
        """
        Executes the full summarization pipeline.
        """

        validator = ErrorValidator()

        if not self._validate_pdf():
            return validator.error("Invalid file. Only PDF files are allowed.")

        # 1️ Extract PDF text
        try:
            extractor = PDFExtractor(self.file_path)
            self.extracted_text = extractor.extract_text()
        except Exception as e:
            return validator.error(f"PDF extraction failed: {str(e)}")

        # 2️ Preprocess text
        preprocessor = TextPreprocessor(self.extracted_text)
        preprocessor.run_pipeline()

        self.cleaned_text = preprocessor.cleaned_text
        self.warnings = preprocessor.warnings
        validator.check_warnings(self.warnings)

        # 3 LLM Inference
        llm_controller = LLMController(
            text=self.cleaned_text,
            model=self.model,
            options=self.options,
            language=self.language,
            header_weights=self.header_weights
        )

        llm_result = llm_controller.run_inference()

        if llm_result.get("status") == "error":
            return validator.error(llm_result.get("message"))

        self.summary = llm_result.get("summary", "")

        # 4 Build JSON response
        builder = JSONResponse(self.summary)
        self.response = builder.to_dict()

        self.response["warnings"] = self.warnings
        self.response["language"] = self.language

        return self.response
