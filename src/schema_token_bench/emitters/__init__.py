"""Registry of output formats. Add a format by appending a `Format` here."""

from collections.abc import Callable
from dataclasses import dataclass

from ..model import Schema
from . import graphql, jsonschema, protobuf, python, typescript

# Formats used to publish API definitions, vs. notations that are only a
# cheaper way to describe an API inside a prompt.
API = "API description"
PROMPT = "Prompt notation"


@dataclass(frozen=True)
class Format:
    key: str
    label: str
    kind: str
    extension: str
    emit: Callable[[Schema], str]


FORMATS = [
    Format("jsonschema", "JSON Schema", API, "json", jsonschema.emit_pretty),
    Format("jsonschema-min", "JSON Schema (minified)", API, "min.json", jsonschema.emit_minified),
    Format("jsonschema-yaml", "JSON Schema (YAML)", API, "yaml", jsonschema.emit_yaml),
    Format("graphql", "GraphQL SDL", API, "graphql", graphql.emit),
    Format("protobuf", "Protobuf / gRPC", API, "proto", protobuf.emit),
    Format("typescript", "TypeScript", PROMPT, "d.ts", typescript.emit),
    Format("python", "Python type hints", PROMPT, "py", python.emit),
]

BASELINE = "jsonschema"
