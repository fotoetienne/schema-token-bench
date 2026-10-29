"""TypeScript declarations: interfaces, string-literal unions for enums, and
`declare function` signatures that take a single named-arguments object."""

from ..model import DATETIME_DOC, Enum, Field, Object, Operation, Schema, TypeRef
from .common import blocks, fits

SCALARS = {
    "string": "string",
    "id": "string",
    "int": "number",
    "float": "number",
    "bool": "boolean",
    "datetime": "DateTime",
}


def type_ref(ref: TypeRef) -> str:
    name = SCALARS.get(ref.name, ref.name)
    return f"{name}[]" if ref.is_list else name


def jsdoc(text: str | None, indent: str = "") -> list[str]:
    return [f"{indent}/** {text} */"] if text else []


def member(f: Field) -> str:
    return f"{f.name}{'' if f.required else '?'}: {type_ref(f.type)};"


def members(fields: list[Field], indent: str) -> list[str]:
    return [line for f in fields for line in jsdoc(f.doc, indent) + [indent + member(f)]]


def type_def(t: Object | Enum) -> str:
    if isinstance(t, Enum):
        has_docs = any(v.doc for v in t.values)
        line = f"type {t.name} = " + " | ".join(f'"{v.name}"' for v in t.values) + ";"
        if fits(line, has_docs):
            body = [line]
        else:
            alts = [l for v in t.values for l in jsdoc(v.doc, "  ") + [f'  | "{v.name}"']]
            body = [f"type {t.name} =", *alts[:-1], alts[-1] + ";"]
    else:
        body = [f"interface {t.name} {{", *members(t.fields, "  "), "}"]
    return "\n".join(jsdoc(t.doc) + body)


def operation(op: Operation) -> str:
    returns = type_ref(op.returns)
    has_docs = any(p.doc for p in op.params)
    args = " ".join(member(p) for p in op.params).rstrip(";")
    line = f"declare function {op.name}(args: {{ {args} }}): {returns};"
    if fits(line, has_docs):
        sig = [line]
    else:
        sig = [f"declare function {op.name}(args: {{", *members(op.params, "  "), f"}}): {returns};"]
    return "\n".join(jsdoc(op.doc) + sig)


def emit(schema: Schema) -> str:
    datetime = ""
    if schema.uses_scalar("datetime"):
        doc = jsdoc(DATETIME_DOC) if schema.has_docs else []
        datetime = "\n".join(doc + ["type DateTime = string;"])
    return blocks(
        [datetime, *[type_def(t) for t in schema.types], *[operation(op) for op in schema.operations]]
    )
