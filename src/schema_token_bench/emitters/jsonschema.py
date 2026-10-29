"""JSON Schema (draft 2020-12). Shared types live in `$defs`; operations are
rendered as Anthropic-style tool definitions with an added `output_schema`."""

import json
from typing import Any

import yaml

from ..model import Enum, Field, Object, Schema, TypeRef

SCALARS: dict[str, dict[str, str]] = {
    "string": {"type": "string"},
    "id": {"type": "string"},
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "bool": {"type": "boolean"},
    "datetime": {"type": "string", "format": "date-time"},
}


def type_ref(ref: TypeRef) -> dict[str, Any]:
    item = dict(SCALARS[ref.name]) if ref.is_scalar else {"$ref": f"#/$defs/{ref.name}"}
    return {"type": "array", "items": item} if ref.is_list else item


def with_doc(schema: dict[str, Any], doc: str | None) -> dict[str, Any]:
    return {**schema, "description": doc} if doc else schema


def properties(fields: list[Field]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "type": "object",
        "properties": {f.name: with_doc(type_ref(f.type), f.doc) for f in fields},
    }
    required = [f.name for f in fields if f.required]
    if required:
        out["required"] = required
    return out


def type_def(t: Object | Enum) -> dict[str, Any]:
    if isinstance(t, Enum):
        if any(v.doc for v in t.values):
            body: dict[str, Any] = {
                "type": "string",
                "oneOf": [with_doc({"const": v.name}, v.doc) for v in t.values],
            }
        else:
            body = {"type": "string", "enum": [v.name for v in t.values]}
    else:
        body = properties(t.fields)
    return {"description": t.doc, **body} if t.doc else body


def document(schema: Schema) -> dict[str, Any]:
    doc: dict[str, Any] = {"$defs": {t.name: type_def(t) for t in schema.types}}
    if schema.operations:
        doc["tools"] = [
            {
                "name": op.name,
                **({"description": op.doc} if op.doc else {}),
                "input_schema": properties(op.params),
                "output_schema": type_ref(op.returns),
            }
            for op in schema.operations
        ]
    return doc


def emit_pretty(schema: Schema) -> str:
    return json.dumps(document(schema), indent=2) + "\n"


def emit_minified(schema: Schema) -> str:
    return json.dumps(document(schema), separators=(",", ":")) + "\n"


def emit_yaml(schema: Schema) -> str:
    return yaml.safe_dump(document(schema), sort_keys=False, allow_unicode=True)
