import fitz  # PyMuPDF

class PDFExtractor:
    """
    Responsible for extracting clean text from PDF files.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    # ----------------------------------
    # Validation
    # ----------------------------------

    def _validate_extension(self) -> bool:
        return self.file_path.lower().endswith(".pdf")

    # ----------------------------------
    # Public Method
    # ----------------------------------

    def extract_text(self) -> str:
        """
        Extracts textual content from a PDF file,
        excluding text inside tables.
        """

        if not self._validate_extension():
            raise ValueError("Invalid file format. Only PDF files are allowed.")

        try:
            with fitz.open(self.file_path) as doc:

                all_pages_text = []

                for page in doc:

                    tables = page.find_tables()
                    table_rects = [fitz.Rect(t.bbox) for t in tables]

                    blocks = page.get_text("blocks")
                    filtered_blocks = []

                    for block in blocks:
                        x0, y0, x1, y1, text, _, block_type = block
                        block_rect = fitz.Rect(x0, y0, x1, y1)

                        inside_table = any(
                            table_rect.contains(block_rect)
                            for table_rect in table_rects
                        )

                        if not inside_table and block_type == 0:
                            filtered_blocks.append(text.strip())

                    page_text = "\n".join(filtered_blocks).strip()

                    if page_text:
                        all_pages_text.append(page_text)

        except fitz.FileDataError:
            raise ValueError(
                f"File '{self.file_path}' is corrupted or not a valid PDF."
            )
        except Exception as e:
            raise ValueError(
                f"Could not open file '{self.file_path}'. Error: {str(e)}"
            )

        final_text = "\n".join(all_pages_text).strip()

        if not final_text:
            raise ValueError(
                f"File '{self.file_path}' does not contain extractable text."
            )

        return final_text
