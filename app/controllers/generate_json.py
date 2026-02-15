from typing import Optional, Dict
import json


class JSONResponse:
    """
    Responsible for structuring the final response in JSON format.
    """

    def __init__(self, summary: Optional[str]) -> None:
        self.summary: str = (summary or "").strip()
        self.is_valid: bool = bool(self.summary)

        self.message: str = (
            "Summary generated successfully."
            if self.is_valid
            else "Error: Unable to generate the summary."
        )

    def to_dict(self) -> Dict[str, str]:
        """
        Returns the standardized response structure as a dictionary.
        """
        return {
            "summary": self.summary,
            "message": self.message
        }

    def to_json(self) -> str:
        """
        Returns the response serialized as a JSON string.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)
