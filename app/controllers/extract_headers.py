import re
from typing import List, Dict
from .pdf_extractor import PDFExtractor
from .text_preprocessor import TextPreprocessor


class PDFSectionExtractor:
    """
    Detects and structures academic sections from PDF-extracted text
    (IEEE / scientific articles in English and Spanish).

    - Relies on numbering formats such as: I, II, 1, 1.1, 2.3.4, etc.
    May fail if sections are not numbered.
    - Detects subsections (currently not used externally).
    - Filters figures, tables, equations, and noise.
    - Stops processing at References.
    """

    # =====================================================
    # BASE NUMBERING PATTERN
    # =====================================================

    SECTION_NUMBER_PATTERN = r"\d+(?:\.\d+)*|[IVXLCDM]+"

    # =====================================================
    # MAIN REGEX PATTERNS
    # =====================================================

    RE_ABSTRACT = re.compile(
        r"^(abstract|resumen)[\s—:-]",
        re.IGNORECASE
    )

    RE_KEYWORDS = re.compile(
        r"^(keywords|index terms|palabras clave)[\s—:-]",
        re.IGNORECASE
    )

    RE_SECTION = re.compile(
        rf"^({SECTION_NUMBER_PATTERN})[\.\)]?\s+.+",
        re.IGNORECASE
    )

    RE_SECTION_NUMBER_ONLY = re.compile(
        rf"^({SECTION_NUMBER_PATTERN})[\.\)]?$",
        re.IGNORECASE
    )

    RE_REFERENCES = re.compile(
        r"^(references|referencias)\s*$",
        re.IGNORECASE
    )

    # =====================================================
    # NOISE FILTERS
    # =====================================================

    RE_FIGURE_CAPTION = re.compile(
        r"^(fig|figure)\.?\s*\d+[\.:]?\s+.+",
        re.IGNORECASE
    )

    RE_TABLE_CAPTION = re.compile(
        r"^table\s*\d+[\.:]?\s+.+",
        re.IGNORECASE
    )

    RE_EQUATION = re.compile(
        r"^\(?\d+\)?$"
    )

    RE_FIGURE_INLINE = re.compile(
        r"^(fig|figure)\.?\s*\d+",
        re.IGNORECASE
    )

    RE_TABLE_INLINE = re.compile(
        r"^table\s*\d+",
        re.IGNORECASE
    )

    RE_AUTHOR = re.compile(
        r"^[a-záéíóúñ]+(\s+[a-záéíóúñ]+){1,3}$",
        re.IGNORECASE
    )

    RE_SECTION_TEXT_ONLY = re.compile(
        r"^(introduction|background|related work|methodology|methods|"
        r"dataset|data|experiments|results|discussion|conclusion|"
        r"future work|materials and methods|"
        r"trabajo relacionado|metodología|resultados|discusión|"
        r"conclusiones?)$",
        re.IGNORECASE
    )

    RE_URL = re.compile(
        r"https?://|www\.",
        re.IGNORECASE
    )

    RE_RQ_HEADER = re.compile(
        r"^(\d+)\.\s+rq\d+\s*:",
        re.IGNORECASE
    )

    # =====================================================
    # SEMANTIC LISTS
    # =====================================================

    NON_SECTION_KEYWORDS = {
        "figure", "fig", "table", "equation", "eq", "algorithm",
        "source", "note"
    }

    VALID_SECTION_STARTERS = {
        "introduction", "background", "related", "method", "methods",
        "methodology", "experiment", "experiments", "results",
        "discussion", "conclusion", "future", "dataset", "data",
        "materials", "evaluation", "trabajo", "metodología",
        "resultados", "discusión", "conclusiones"
    }

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.lines = self._prepare_lines()
        self.title = ""
        self.authors = ""
        self.sections: List[Dict] = []

    # =====================================================
    # NORMALIZATION
    # =====================================================

    def _prepare_lines(self) -> List[str]:
        return [
            line.strip()
            for line in self.raw_text.splitlines()
            if line.strip()
        ]

    # =====================================================
    # HELPERS
    # =====================================================

    def _numeric_depth(self, number: str) -> int:
        """Calculates numbering depth (1, 1.1, 1.1.1, etc.)."""
        return number.count(".") + 1

    def _looks_like_caption(self, line: str) -> bool:
        words = line.lower().split()

        if len(words) > 10:
            return True

        if any(w in self.NON_SECTION_KEYWORDS for w in words):
            return True

        if line.endswith("."):
            return True

        return False

    def _looks_like_section(self, line: str) -> bool:
        first_word = line.lower().split()[0]
        return first_word in self.VALID_SECTION_STARTERS

    # =====================================================
    # LINE CLASSIFICATION
    # =====================================================

    def classify_line(self, line: str) -> str:
        if self.RE_REFERENCES.match(line):
            return "references"

        if (
            self.RE_FIGURE_CAPTION.match(line)
            or self.RE_TABLE_CAPTION.match(line)
            or self.RE_FIGURE_INLINE.match(line)
            or self.RE_TABLE_INLINE.match(line)
            or self.RE_EQUATION.match(line)
        ):
            return "noise"

        if self.RE_RQ_HEADER.match(line):
            return "section"

        if self.RE_URL.search(line):
            return "noise"

        if self.RE_ABSTRACT.match(line):
            return "abstract"

        if self.RE_KEYWORDS.match(line):
            return "keywords"

        if self.RE_SECTION_NUMBER_ONLY.match(line):
            return "section_number"

        match = self.RE_SECTION.match(line)
        if match:
            if self._looks_like_caption(line):
                return "noise"

            number = match.group(1)

            if number.isalpha():  # Roman numerals
                return "section"

            depth = self._numeric_depth(number)
            return "section" if depth == 1 else "subsection"

        if self.RE_SECTION_TEXT_ONLY.match(line):
            if not self._looks_like_section(line):
                return "noise"
            return "section"

        return "content"

    # =====================================================
    # TITLE & AUTHORS
    # =====================================================

    def detect_title_and_authors(self, scan_limit: int = 15) -> None:
        title_lines = []
        authors = []

        for line in self.lines[:scan_limit]:
            label = self.classify_line(line)

            if label in {"abstract", "section"}:
                break

            if self.RE_AUTHOR.match(line) and title_lines:
                authors.append(line)
            else:
                title_lines.append(line)

        self.title = " ".join(title_lines).strip()
        self.authors = ", ".join(authors)

    # =====================================================
    # SECTION CONSTRUCTION
    # =====================================================

    def build_sections(self) -> None:
        current = {
            "type": "preamble",
            "header": None,
            "content": []
        }

        pending_section_number = None

        for line in self.lines:
            label = self.classify_line(line)

            if label == "references":
                break

            if label == "section_number":
                pending_section_number = line
                continue

            if label == "section":
                self.sections.append(current)

                header = (
                    f"{pending_section_number} {line}"
                    if pending_section_number else line
                )
                pending_section_number = None

                current = {
                    "type": "section",
                    "header": header,
                    "content": []
                }
                continue

            if label == "subsection":
                self.sections.append(current)
                current = {
                    "type": "subsection",
                    "header": line,
                    "content": []
                }
                continue

            if label == "noise":
                continue

            current["content"].append(line)

        self.sections.append(current)

    # =====================================================
    # PIPELINE
    # =====================================================

    def process(self) -> Dict:
        self.detect_title_and_authors()
        self.build_sections()

        return {
            "title": self.title,
            "authors": self.authors,
            "sections": self.sections
        }

    def extract_pdf_headers(self, pdf_path: str) -> List[str]:
        """
        Full pipeline:
        PDF → text extraction → cleaning → section detection → header extraction
        """

        # 1) Extract raw text
        extractor = PDFExtractor(pdf_path)
        extracted_text = extractor.extract_text()

        if not extracted_text.strip():
            raise ValueError("Failed to extract text from PDF.")

        # 2) Preprocessing
        preprocessor = TextPreprocessor(extracted_text)
        preprocessor.run_pipeline()
        clean_text = preprocessor.cleaned_text

        # 3) Section processing
        extractor = PDFSectionExtractor(clean_text)
        document = extractor.process()

        # 4) Return section headers only
        return [
            section["header"]
            for section in document.get("sections", [])
            if section.get("type") == "section" and section.get("header")
        ]
