import re

class TextPreprocessor:
    """
    Cleans and structures extracted academic text
    before sending it to the LLM.
    """

    def __init__(self, extracted_text: str):

        self.original_text = extracted_text
        self.cleaned_text = extracted_text

        self.warnings = {
            "repeated_headers_removed": False,
            "abstract_detected": False,
            "references_removed": False,
            "page_numbers_removed": False,
        }

    # ----------------------------------
    # Public Pipeline
    # ----------------------------------

    def run_pipeline(self) -> None:
        self._remove_margins()
        self._remove_sections()
        self._remove_inline_citations()
        self._rebuild_paragraphs()
        self._normalize_case()

    # ----------------------------------
    # Step 1 - Remove repeated margins
    # ----------------------------------

    def _remove_margins(self) -> None:

        lines = self.cleaned_text.split("\n")
        frequency = {}

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            normalized = re.sub(r"\d+", "", stripped)
            normalized = re.sub(r"\s+", " ", normalized).lower()
            frequency[normalized] = frequency.get(normalized, 0) + 1

        filtered = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if re.fullmatch(r"\d+", stripped):
                self.warnings["page_numbers_removed"] = True
                continue

            normalized = re.sub(r"\d+", "", stripped)
            normalized = re.sub(r"\s+", " ", normalized).lower()

            if frequency.get(normalized, 0) > 1:
                self.warnings["repeated_headers_removed"] = True
                continue

            filtered.append(line)

        self.cleaned_text = "\n".join(filtered).strip()

    # ----------------------------------
    # Step 2 - Remove abstract & references
    # ----------------------------------

    def _remove_sections(self) -> None:

        text = self.cleaned_text

        # Detect abstract
        if re.search(r"\b(abstract|resumen)\b", text, re.IGNORECASE):
            self.warnings["abstract_detected"] = True

        # Trim everything before Introduction
        intro_match = re.search(r"\bintroduction\b", text, re.IGNORECASE)
        if intro_match:
            text = text[intro_match.start():]

        # Remove references section
        ref_match = re.search(
            r"\b(references|bibliography)\b[\s\S]*$",
            text,
            re.IGNORECASE
        )

        if ref_match:
            text = text[:ref_match.start()]
            self.warnings["references_removed"] = True

        self.cleaned_text = text.strip()

    # ----------------------------------
    # Step 3 - Remove citations & noise
    # ----------------------------------

    def _remove_inline_citations(self) -> None:

        text = self.cleaned_text

        # Emails
        text = re.sub(r"\S+@\S+", "", text)

        # IEEE style [1], [2-4]
        text = re.sub(r"\[\d+(?:[-,]\d+)*\]", "", text)

        # APA style (Author, 2020)
        text = re.sub(r"\([A-Za-z\s,&]+,\s*\d{4}\)", "", text)

        # Remove figure/table mentions
        text = re.sub(
            r"\b(figure|table|equation|fig\.?|tab\.?)\s*\d*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        self.cleaned_text = text.strip()

    # ----------------------------------
    # Step 4 - Rebuild paragraphs
    # ----------------------------------

    def _rebuild_paragraphs(self) -> None:

        text = self.cleaned_text

        # Fix hyphen line breaks
        text = re.sub(r"-\s*\n", "", text)

        # Join broken lines inside paragraphs
        text = re.sub(r"\n(?=[a-z])", " ", text)

        # Normalize multiple line breaks
        text = re.sub(r"\n{2,}", "\n\n", text)

        # Remove extra spaces
        text = re.sub(r" {2,}", " ", text)

        self.cleaned_text = text.strip()

    # ----------------------------------
    # Step 5 - Normalize case
    # ----------------------------------

    def _normalize_case(self) -> None:
        self.cleaned_text = self.cleaned_text.lower()
