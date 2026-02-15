from typing import Dict, List


class ErrorValidator:
    """
    Handles error responses and warning validation
    within the PDF summarization pipeline.
    """

    def __init__(self) -> None:
        self._collected_warnings: List[str] = []

    # ---------------------------------
    # Error Handling
    # ---------------------------------

    def error(self, message: str) -> Dict[str, str]:
        """
        Returns a standardized error response dictionary.
        """
        return {
            "status": "error",
            "message": message
        }

    # ---------------------------------
    # Warning Handling
    # ---------------------------------

    def check_warnings(self, warnings: Dict[str, int]) -> None:
        """
        Checks section validation dictionary and collects warnings.

        Args:
            warnings: Dictionary where
                        0 = not identified
                        1 = identified
        """
        for section, status in warnings.items():
            if status == 0:
                self._collected_warnings.append(
                    f"Section '{section}' was not identified."
                )

    def get_warnings(self) -> List[str]:
        """
        Returns collected warnings.
        """
        return self._collected_warnings
