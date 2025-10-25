from lxml import etree
from pydantic import BaseModel

from .decoder import xml_to_model
from .encoder import model_to_xml
from .exceptions import XMLParsingError
from .utils import model_dump_xml


class XMLModel(BaseModel):
    """Base class for XML-enabled Pydantic models."""

    def to_xml(self) -> etree.Element:
        """Encode model to XML element."""
        return model_to_xml(self)

    def to_xml_str(self, pretty: bool = True) -> str:
        """Encode model to XML string."""
        element = self.to_xml()
        return etree.tostring(element, pretty_print=pretty, encoding="unicode")

    def to_xml_dict(self) -> dict:
        """Dump model as XML-like dictionary."""
        return model_dump_xml(self)

    @classmethod
    def from_xml(cls, xml_str: str | etree.Element):
        """Decode XML string or element into a model instance."""
        try:
            element = etree.fromstring(xml_str) if isinstance(xml_str, str) else xml_str
            return xml_to_model(cls, element)
        except etree.XMLSyntaxError as e:
            raise XMLParsingError(str(e)) from e
