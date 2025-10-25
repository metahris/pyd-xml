from types import UnionType
from typing import get_origin, get_args, Union

from lxml import etree
from pydantic import BaseModel

from .exceptions import DecodeError, XMLParsingError


def resolve_field_type(annotation):
    """Return the underlying usable type from annotations (handles Optional, list, etc)."""
    origin = get_origin(annotation)
    if origin is None:
        return annotation
    if origin in (list, tuple, set):
        return get_args(annotation)[0]
    if origin in (UnionType, Union):
        args = [a for a in get_args(annotation) if a is not type(None)]
        return args[0] if args else None
    return origin


def xml_to_model(model_class: type[BaseModel], element: etree.Element) -> BaseModel:
    """Decode XML element to a Pydantic model instance."""
    try:
        data = {}

        for name, field in model_class.model_fields.items():
            meta = field.json_schema_extra or {}
            xml_name = meta.get("xml_name") or name
            field_type = resolve_field_type(field.annotation)

            # Attribute
            if meta.get("xml_attr"):
                value = element.get(xml_name)
                data[name] = field_type(value) if value is not None else None
                continue

            # Text
            if meta.get("xml_text"):
                text = (element.text or "").strip()
                data[name] = field_type(text) if text else None
                continue

            # Children
            children = element.findall(xml_name)
            if not children:
                data[name] = None
                continue

            # List
            if get_origin(field.annotation) == list:
                inner_type = resolve_field_type(field.annotation)
                items = []
                for child in children:
                    if isinstance(inner_type, type) and issubclass(inner_type, BaseModel):
                        items.append(xml_to_model(inner_type, child))
                    else:
                        items.append(inner_type(child.text))
                data[name] = items
                continue

            # Nested model
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                data[name] = xml_to_model(field_type, children[0])
                continue

            # Primitive field
            value = children[0].text
            data[name] = field_type(value) if value is not None else None

        return model_class(**data)

    except etree.XMLSyntaxError as e:
        raise XMLParsingError(str(e)) from e
    except Exception as e:
        raise DecodeError(model_class.__name__, message=str(e)) from e
