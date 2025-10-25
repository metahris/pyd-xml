from pydantic import BaseModel


def _model_dump_xml(model: BaseModel) -> dict:
    """Internal recursive dump — returns XML-like dict without root."""
    result = {}

    for name, field in model.__class__.model_fields.items():
        meta = field.json_schema_extra or {}
        value = getattr(model, name)

        if value is None and not meta.get("xml_include_none"):
            continue

        # Attribute
        if meta.get("xml_attr"):
            result[f"@{meta.get('xml_name') or name}"] = value
            continue

        # Text node
        if meta.get("xml_text"):
            result["#text"] = value
            continue

        # Nested model
        if isinstance(value, BaseModel):
            result[meta.get("xml_name") or name] = _model_dump_xml(value)
            continue

        # List
        if isinstance(value, list):
            items = [
                _model_dump_xml(v) if isinstance(v, BaseModel) else v
                for v in value
            ]
            result[meta.get("xml_name") or name] = items
            continue

        # Regular element
        result[meta.get("xml_name") or name] = value

    return result


def model_dump_xml(model: BaseModel) -> dict:
    """Dump model to a dict reflecting full XML structure (including root)."""
    tag_name = model.__class__.__name__
    return {tag_name: _model_dump_xml(model)}
