from .base import XMLModel
from .decoder import xml_to_model
from .encoder import model_to_xml
from .exceptions import (
    PydanticXMLError,
    EncodeError,
    DecodeError,
    XMLValidationError,
    XMLParsingError,
)
from .fields import xml_field
from .utils import model_dump_xml

__all__ = [
    # Core class
    "XMLModel",

    # Field helper
    "xml_field",

    # Conversion helpers
    "model_to_xml",
    "xml_to_model",
    "model_dump_xml",

    # Exceptions
    "PydanticXMLError",
    "EncodeError",
    "DecodeError",
    "XMLValidationError",
    "XMLParsingError",
]
