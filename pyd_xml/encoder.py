from lxml import etree
from pydantic import BaseModel

from .exceptions import EncodeError


def model_to_xml(model: BaseModel, tag_name: str | None = None) -> etree.Element:
    """Convert a Pydantic model instance into an XML element."""
    try:
        # ✅ Pydantic v2 config support
        model_config = getattr(model.__class__, "model_config", None)
        config_tag = None
        if model_config and isinstance(model_config, dict):
            config_tag = model_config.get("xml_tag")

        # Priority: explicit arg > Config.xml_tag > auto camelCase
        tag_name = tag_name or config_tag or model.__class__.__name__
        element = etree.Element(tag_name)

        for name, field in model.__class__.model_fields.items():
            value = getattr(model, name)
            meta = field.json_schema_extra or {}
            xml_name = meta.get("xml_name") or name

            # Skip None unless explicitly included
            if value is None:
                if meta.get("xml_include_none"):
                    empty = etree.Element(xml_name)
                    element.append(empty)
                continue

            # Attribute
            if meta.get("xml_attr"):
                element.set(xml_name, str(value))
                continue

            # Text node
            if meta.get("xml_text"):
                element.text = str(value)
                continue

            # Nested model
            if isinstance(value, BaseModel):
                element.append(model_to_xml(value, xml_name))
                continue

            # List
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, BaseModel):
                        element.append(model_to_xml(item, xml_name))
                    else:
                        child = etree.Element(xml_name)
                        child.text = str(item)
                        element.append(child)
                continue

            # Regular element
            child = etree.Element(xml_name)
            child.text = str(value)
            element.append(child)

        return element

    except Exception as e:
        raise EncodeError(model.__class__.__name__, message=str(e)) from e
