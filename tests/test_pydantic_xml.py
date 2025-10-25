import pytest
from lxml import etree

from pyd_xml import (
    XMLModel,
    xml_field,
    model_to_xml,
    xml_to_model,
    EncodeError,
    DecodeError,
    XMLParsingError,
)


# -----------------------------
# ✅ Fixtures
# -----------------------------

class Employee(XMLModel):
    id: int = xml_field(attr=True)
    role: str | None = xml_field(include_none=True)
    name: str
    salary: float


class Department(XMLModel):
    name: str
    employees: list[Employee]


class Company(XMLModel):
    id: int = xml_field(attr=True)
    name: str
    founded: int
    departments: list[Department]


@pytest.fixture
def company_instance():
    return Company(
        id=1001,
        name="TechCorp",
        founded=2005,
        departments=[
            Department(
                name="Engineering",
                employees=[
                    Employee(id=1, name="Alice", role="Developer", salary=70000),
                    Employee(id=2, name="Bob", role=None, salary=68000),
                ],
            ),
            Department(
                name="HR",
                employees=[
                    Employee(id=3, name="Eve", role="HR Manager", salary=60000),
                ],
            ),
        ],
    )


# -----------------------------
# ✅ Tests
# -----------------------------

def test_model_to_xml_structure(company_instance):
    xml_el = company_instance.to_xml()
    assert isinstance(xml_el, etree._Element)
    assert xml_el.tag == "Company"
    assert xml_el.get("id") == "1001"
    assert xml_el.find("name").text == "TechCorp"

    departments = xml_el.findall("departments")
    assert len(departments) == 2
    assert departments[0].find("employees").get("id") == "1"


def test_to_xml_str(company_instance):
    xml_str = company_instance.to_xml_str()
    assert "<Company id=" in xml_str
    assert "<name>TechCorp</name>" in xml_str
    assert "<role/>" in xml_str  # Because include_none=True


def test_round_trip(company_instance):
    xml_str = company_instance.to_xml_str()
    decoded = Company.from_xml(xml_str)
    assert isinstance(decoded, Company)
    assert decoded == company_instance


def test_model_dump_xml_includes_root(company_instance):
    dumped = company_instance.to_xml_dict()
    assert "Company" in dumped
    company_data = dumped["Company"]

    # Check top-level attributes and elements
    assert company_data["@id"] == 1001
    assert company_data["name"] == "TechCorp"
    assert isinstance(company_data["departments"], list)
    assert company_data["departments"][0]["name"] == "Engineering"


def test_model_dump_xml_handles_none_field():
    emp = Employee(id=5, name="Bob", role=None, salary=50000)
    dumped = emp.to_xml_dict()
    assert "Employee" in dumped
    emp_data = dumped["Employee"]
    assert emp_data["@id"] == 5
    assert emp_data["role"] is None  # Because xml_include_none=True


def test_model_to_xml_and_back(company_instance):
    """Full encode → decode → encode round-trip consistency test."""
    xml1 = company_instance.to_xml_str()
    model2 = Company.from_xml(xml1)
    xml2 = model2.to_xml_str()
    assert etree.tostring(etree.fromstring(xml1)) == etree.tostring(etree.fromstring(xml2))


def test_model_to_xml_function(company_instance):
    """Ensure standalone function behaves same as model.to_xml()."""
    el = model_to_xml(company_instance)
    assert etree.tostring(el, encoding="unicode").startswith("<Company")


def test_xml_to_model_function(company_instance):
    xml_str = company_instance.to_xml_str()
    element = etree.fromstring(xml_str)
    decoded = xml_to_model(Company, element)
    assert decoded == company_instance


# -----------------------------
# ⚠️ Error handling tests
# -----------------------------

def test_invalid_xml_raises_parsing_error():
    bad_xml = "<Company><name>Test</name>"  # Missing closing tag
    with pytest.raises(XMLParsingError):
        Company.from_xml(bad_xml)


def test_invalid_field_type_raises_decode_error():
    """Force an invalid type conversion (e.g. string where int expected)."""
    bad_xml = """
    <Company id="notanumber">
        <name>Test</name>
        <founded>2000</founded>
        <departments></departments>
    </Company>
    """
    with pytest.raises(DecodeError):
        Company.from_xml(bad_xml)


def test_encode_error(monkeypatch, company_instance):
    """Force EncodeError by simulating a crash inside the encoder."""
    from pyd_xml import encoder

    # Define a fake encoder that always raises ValueError
    def fake_model_to_xml(_):
        raise ValueError("Simulated encoding failure")

    # Monkeypatch the real encoder with the fake one
    monkeypatch.setattr(encoder, "model_to_xml", fake_model_to_xml)

    # Expect your custom EncodeError to be raised
    with pytest.raises(EncodeError):
        company_instance.to_xml()
