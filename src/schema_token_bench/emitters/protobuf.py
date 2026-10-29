"""Protocol Buffers (proto3) with a gRPC service, following the protobuf style
guide: snake_case fields, prefixed enum values with an UNSPECIFIED zero, and a
request message per RPC. proto3 has no `required`, so required-ness is not
expressed."""

from ..model import Enum, Field, Operation, Schema, TypeRef, pascal, snake
from .common import blocks

SCALARS = {
    "string": "string",
    "id": "string",
    "int": "int32",
    "float": "double",
    "bool": "bool",
    "datetime": "google.protobuf.Timestamp",
}


def type_name(ref: TypeRef) -> str:
    return SCALARS.get(ref.name, ref.name)


def comment(text: str | None, indent: str = "") -> list[str]:
    return [f"{indent}// {text}"] if text else []


def message(name: str, fields: list[Field], doc: str | None = None) -> str:
    body = []
    for i, f in enumerate(fields, 1):
        label = "repeated " if f.type.is_list else ""
        body += comment(f.doc, "  ") + [f"  {label}{type_name(f.type)} {snake(f.name)} = {i};"]
    return "\n".join(comment(doc) + [f"message {name} {{", *body, "}"])


def enum(t: Enum) -> str:
    prefix = snake(t.name).upper()
    body = [f"  {prefix}_UNSPECIFIED = 0;"]
    for i, v in enumerate(t.values, 1):
        body += comment(v.doc, "  ") + [f"  {prefix}_{v.name} = {i};"]
    return "\n".join(comment(t.doc) + [f"enum {t.name} {{", *body, "}"])


def response_type(op: Operation) -> str:
    """Return a message type directly; wrap lists and scalars in a response."""
    if op.returns.is_scalar or op.returns.is_list:
        return f"{pascal(op.name)}Response"
    return op.returns.name


def response_message(op: Operation) -> str:
    if response_type(op) == op.returns.name:
        return ""
    if op.returns.is_list:
        name = snake(op.returns.name) + "s"
    else:
        name = "result"
    return message(response_type(op), [Field(name, op.returns)])


def service(schema: Schema) -> list[str]:
    if not schema.operations:
        return []
    rpcs = []
    for op in schema.operations:
        rpcs += comment(op.doc, "  ")
        rpcs.append(f"  rpc {pascal(op.name)}({pascal(op.name)}Request) returns ({response_type(op)});")
    out = ["\n".join([f"service {pascal(schema.name)}Service {{", *rpcs, "}"])]
    for op in schema.operations:
        out.append(message(f"{pascal(op.name)}Request", op.params))
        out.append(response_message(op))
    return out


def emit(schema: Schema) -> str:
    header = f'syntax = "proto3";\n\npackage {schema.name};'
    imports = 'import "google/protobuf/timestamp.proto";' if schema.uses_scalar("datetime") else ""
    types = [enum(t) if isinstance(t, Enum) else message(t.name, t.fields, t.doc) for t in schema.types]
    return blocks([header, imports, *types, *service(schema)])
