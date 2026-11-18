"""Compact SDL: a notation designed for this benchmark to cost as few tokens as
possible while staying readable without a legend. Go-style `name type` fields
with no indentation, `type?` for optional, `type[]` for lists, lowercase
built-in scalars, enums as unions, and `#` docs at the end of the line, or on
the line above for types and operations."""

from ..model import Enum, Field, Object, Operation, Schema, TypeRef
from .common import blocks, fits


def type_ref(ref: TypeRef) -> str:
    return f"{ref.name}[]" if ref.is_list else ref.name


def comment(text: str | None) -> list[str]:
    return [f"# {text}"] if text else []


def trailing(text: str | None) -> str:
    return f" # {text}" if text else ""


def member(f: Field) -> str:
    return f"{f.name} {type_ref(f.type)}{'' if f.required else '?'}"


def members(fields: list[Field]) -> list[str]:
    return [member(f) + trailing(f.doc) for f in fields]


def type_def(t: Object | Enum) -> str:
    if isinstance(t, Enum):
        has_docs = any(v.doc for v in t.values)
        line = f"{t.name} = " + " | ".join(v.name for v in t.values)
        if fits(line, has_docs):
            body = [line]
        else:
            body = [f"{t.name} =", *[f"| {v.name}{trailing(v.doc)}" for v in t.values]]
    else:
        body = [f"{t.name} {{", *members(t.fields), "}"]
    return "\n".join(comment(t.doc) + body)


def operation(op: Operation) -> str:
    returns = type_ref(op.returns)
    has_docs = any(p.doc for p in op.params)
    line = f"{op.name}(" + ", ".join(member(p) for p in op.params) + f") {returns}"
    if fits(line, has_docs):
        sig = [line]
    else:
        sig = [f"{op.name}(", *members(op.params), f") {returns}"]
    return "\n".join(comment(op.doc) + sig)


def emit(schema: Schema) -> str:
    return blocks([*[type_def(t) for t in schema.types], *[operation(op) for op in schema.operations]])
