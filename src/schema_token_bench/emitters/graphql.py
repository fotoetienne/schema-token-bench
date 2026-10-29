"""GraphQL SDL. Non-mutating operations go on Query, the rest on Mutation."""

from ..model import DATETIME_DOC, Enum, Field, Object, Operation, Schema, TypeRef
from .common import blocks, fits

SCALARS = {
    "string": "String",
    "id": "ID",
    "int": "Int",
    "float": "Float",
    "bool": "Boolean",
    "datetime": "DateTime",
}


def type_ref(ref: TypeRef, required: bool = True) -> str:
    name = SCALARS.get(ref.name, ref.name)
    if ref.is_list:
        name = f"[{name}!]"
    return f"{name}!" if required else name


def doc(text: str | None, indent: str = "") -> list[str]:
    return [f'{indent}"{text}"'] if text else []


def field(f: Field, indent: str = "  ") -> list[str]:
    return doc(f.doc, indent) + [f"{indent}{f.name}: {type_ref(f.type, f.required)}"]


def type_def(t: Object | Enum) -> str:
    if isinstance(t, Enum):
        head = f"enum {t.name} {{"
        body = [line for v in t.values for line in doc(v.doc, "  ") + [f"  {v.name}"]]
    else:
        head = f"{'input' if t.is_input else 'type'} {t.name} {{"
        body = [line for f in t.fields for line in field(f)]
    return "\n".join(doc(t.doc) + [head, *body, "}"])


def operation(op: Operation) -> list[str]:
    returns = type_ref(op.returns)
    has_docs = any(p.doc for p in op.params)
    args = ", ".join(f"{p.name}: {type_ref(p.type, p.required)}" for p in op.params)
    line = f"  {op.name}({args}): {returns}"
    if fits(line, has_docs):
        sig = [line]
    else:
        params = [line for p in op.params for line in field(p, "    ")]
        sig = [f"  {op.name}(", *params, f"  ): {returns}"]
    return doc(op.doc, "  ") + sig


def root(name: str, ops: list[Operation]) -> str:
    if not ops:
        return ""
    return "\n".join([f"type {name} {{", *[l for op in ops for l in operation(op)], "}"])


def datetime_scalar(schema: Schema) -> str:
    if not schema.uses_scalar("datetime"):
        return ""
    return "\n".join(doc(DATETIME_DOC if schema.has_docs else None) + ["scalar DateTime"])


def emit(schema: Schema) -> str:
    return blocks(
        [
            datetime_scalar(schema),
            *[type_def(t) for t in schema.types],
            root("Query", [op for op in schema.operations if not op.is_mutation]),
            root("Mutation", [op for op in schema.operations if op.is_mutation]),
        ]
    )
