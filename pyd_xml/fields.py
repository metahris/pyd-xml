from pydantic import Field

def xml_field(
    *,
    attr: bool = False,
    text: bool = False,
    name: str | None = None,
    include_none: bool = False,
    **kwargs
):
    """Helper to define XML metadata for Pydantic fields."""
    return Field(
        json_schema_extra={
            "xml_attr": attr,
            "xml_text": text,
            "xml_name": name,
            "xml_include_none": include_none,
        },
        **kwargs
    )
