# pyd-xml

Easily serialize **Pydantic models** to and from **XML** --- with native
support for attributes, nested elements, lists, optional fields, and
type validation.

This library provides a natural XML integration layer for Pydantic
models, allowing full round-trip serialization between Python objects
and XML data.

## 📦 Installation

``` bash
pip install pyd-xml
```

## 🚀 Quick Start

Define your XML-serializable models by extending `XMLModel` and using
`xml_field` to control XML mapping:

``` python
from pyd_xml import XMLModel, xml_field

class Employee(XMLModel):
    id: int = xml_field(attr=True)            # Attribute
    role: str | None = xml_field(include_none=True)  # Optional field included as empty tag
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
```

Serialize your model to XML:

``` python
company = Company(
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

xml_str = company.to_xml_str()
print(xml_str)
```

Output:

``` xml
<Company id="1001">
  <name>TechCorp</name>
  <founded>2005</founded>
  <departments>
    <name>Engineering</name>
    <employees id="1">
      <name>Alice</name>
      <role>Developer</role>
      <salary>70000</salary>
    </employees>
    <employees id="2">
      <name>Bob</name>
      <role/>
      <salary>68000</salary>
    </employees>
  </departments>
  <departments>
    <name>HR</name>
    <employees id="3">
      <name>Eve</name>
      <role>HR Manager</role>
      <salary>60000</salary>
    </employees>
  </departments>
</Company>
```

## 🔁 Full Round Trip

Easily convert back from XML to Python objects:

``` python
decoded = Company.from_xml(xml_str)
assert decoded == company
```

## ⚙️ Utility Functions

You can also use the standalone helpers:

``` python
from pyd_xml import model_to_xml, xml_to_model

element = model_to_xml(company)
company2 = xml_to_model(Company, element)
```

## 🧩 Dictionary Representation

Convert models into a dictionary representation with XML semantics:

``` python
company_dict = company.to_xml_dict()
print(company_dict["Company"]["@id"])   # Attribute
print(company_dict["Company"]["name"])  # Element
```

## License

Licensed under the **Apache License 2.0**.

\-\--

## Author

**Mohamed Tahri** \<\`simotahri1@gmail.com\`\>
