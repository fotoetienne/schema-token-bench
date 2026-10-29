"""Python type hints: TypedDict classes, Literal aliases for enums, and stub
functions with Google-style docstrings."""

from ..model import Enum, Field, Object, Operation, Schema, TypeRef, snake
from .common import blocks, fits

SCALARS = {
    "string": "str",
    "id": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "datetime": "datetime",
}


def type_ref(ref: TypeRef) -> str:
    name = SCALARS.get(ref.name, ref.name)
    return f"list[{name}]" if ref.is_list else name


def trailing(doc: str | None) -> str:
    return f"  # {doc}" if doc else ""


def attribute(f: Field) -> str:
    t = type_ref(f.type)
    return f"    {snake(f.name)}: {t if f.required else f'NotRequired[{t}]'}{trailing(f.doc)}"


def type_def(t: Object | Enum) -> str:
    if isinstance(t, Enum):
        has_docs = any(v.doc for v in t.values)
        line = f"{t.name} = Literal[" + ", ".join(f'"{v.name}"' for v in t.values) + "]"
        if fits(line, has_docs):
            body = [line]
        else:
            body = [f"{t.name} = Literal[", *[f'    "{v.name}",{trailing(v.doc)}' for v in t.values], "]"]
        return "\n".join(([f"# {t.doc}"] if t.doc else []) + body)
    docstring = [f'    """{t.doc}"""', ""] if t.doc else []
    return "\n".join([f"class {t.name}(TypedDict):", *docstring, *[attribute(f) for f in t.fields]])


def param(p: Field) -> str:
    t = type_ref(p.type)
    return f"{snake(p.name)}: {t}" if p.required else f"{snake(p.name)}: {t} | None = None"


def operation(op: Operation) -> str:
    # Parameters with defaults must follow those without.
    params = sorted(op.params, key=lambda p: not p.required)
    returns = type_ref(op.returns)
    documented = [p for p in params if p.doc]
    line = f"def {snake(op.name)}({', '.join(param(p) for p in params)}) -> {returns}: ..."
    if not op.doc and fits(line, bool(documented)):
        return line
    head = f"def {snake(op.name)}({', '.join(param(p) for p in params)}) -> {returns}:"
    if not fits(head, False):
        head = "\n".join(
            [f"def {snake(op.name)}(", *[f"    {param(p)}," for p in params], f") -> {returns}:"]
        )
    if not op.doc:
        return head + " ..."
    doc = [op.doc]
    if documented:
        doc += ["", "Args:", *[f"    {snake(p.name)}: {p.doc}" for p in documented]]
    if len(doc) == 1:
        return f'{head}\n    """{op.doc}"""'
    return "\n".join([head, f'    """{doc[0]}', *[f"    {d}" if d else "" for d in doc[1:]], '    """'])


def imports(schema: Schema) -> str:
    typing = {"TypedDict"} if any(isinstance(t, Object) for t in schema.types) else set()
    if any(isinstance(t, Enum) for t in schema.types):
        typing.add("Literal")
    if any(not f.required for t in schema.types if isinstance(t, Object) for f in t.fields):
        typing.add("NotRequired")
    lines = ["from datetime import datetime"] if schema.uses_scalar("datetime") else []
    if typing:
        lines.append(f"from typing import {', '.join(sorted(typing))}")
    return "\n".join(lines)


def emit(schema: Schema) -> str:
    return blocks(
        [imports(schema), *[type_def(t) for t in schema.types], *[operation(op) for op in schema.operations]],
        blank_lines=2,  # PEP 8
    )
