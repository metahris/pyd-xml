

class PydanticXMLError(Exception):
    """Base class for all pyd-xml errors."""
    pass


class EncodeError(PydanticXMLError):
    """Raised when encoding a Pydantic model to XML fails."""

    def __init__(self, model_name: str, field_name: str | None = None, message: str = ""):
        detail = f"Failed to encode model '{model_name}'"
        if field_name:
            detail += f" (field: '{field_name}')"
        if message:
            detail += f": {message}"
        super().__init__(detail)


class DecodeError(PydanticXMLError):
    """Raised when decoding XML to a Pydantic model fails."""

    def __init__(self, model_name: str, field_name: str | None = None, message: str = ""):
        detail = f"Failed to decode XML into model '{model_name}'"
        if field_name:
            detail += f" (field: '{field_name}')"
        if message:
            detail += f": {message}"
        super().__init__(detail)


class XMLValidationError(PydanticXMLError):
    """Raised when the XML structure does not match the model definition."""

    def __init__(self, tag: str, expected: str):
        super().__init__(f"Invalid XML tag '{tag}', expected '{expected}'")


class XMLParsingError(PydanticXMLError):
    """Raised when parsing invalid or malformed XML."""

    def __init__(self, message: str):
        super().__init__(f"Failed to parse XML: {message}")
