"""Format-neutral schema model. Every emitter renders from these types."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

SCALARS = {"string", "int", "float", "bool", "id", "datetime"}

# Formats without a built-in timestamp type declare an alias carrying this doc.
DATETIME_DOC = "ISO 8601 date-time string."


@dataclass(frozen=True)
class TypeRef:
    name: str
    is_list: bool = False

    @classmethod
    def parse(cls, spec: str) -> TypeRef:
        if spec.startswith("[") and spec.endswith("]"):
            return cls(spec[1:-1], is_list=True)
        return cls(spec)

    @property
    def is_scalar(self) -> bool:
        return self.name in SCALARS


@dataclass
class Field:
    name: str
    type: TypeRef
    required: bool = True
    doc: str | None = None


@dataclass
class EnumValue:
    name: str
    doc: str | None = None


@dataclass
class Enum:
    name: str
    values: list[EnumValue]
    doc: str | None = None


@dataclass
class Object:
    name: str
    fields: list[Field]
    doc: str | None = None
    # GraphQL needs `input` types for object-valued arguments.
    is_input: bool = False


@dataclass
class Operation:
    name: str
    params: list[Field]
    returns: TypeRef
    doc: str | None = None
    is_mutation: bool = False


@dataclass
class Schema:
    name: str
    summary: str
    types: list[Object | Enum] = field(default_factory=list)
    operations: list[Operation] = field(default_factory=list)

    def type(self, name: str) -> Object | Enum:
        for t in self.types:
            if t.name == name:
                return t
        raise KeyError(name)

    def uses_scalar(self, scalar: str) -> bool:
        refs = [f.type for t in self.types if isinstance(t, Object) for f in t.fields]
        refs += [p.type for op in self.operations for p in op.params]
        refs += [op.returns for op in self.operations]
        return any(r.name == scalar for r in refs)

    @property
    def has_docs(self) -> bool:
        objs = [t for t in self.types if isinstance(t, Object)]
        return any(
            [t.doc for t in self.types]
            + [f.doc for t in objs for f in t.fields]
            + [op.doc for op in self.operations]
        )

    def without_docs(self) -> Schema:
        def strip_fields(fields: list[Field]) -> list[Field]:
            return [Field(f.name, f.type, f.required) for f in fields]

        types: list[Object | Enum] = []
        for t in self.types:
            if isinstance(t, Enum):
                types.append(Enum(t.name, [EnumValue(v.name) for v in t.values]))
            else:
                types.append(Object(t.name, strip_fields(t.fields), is_input=t.is_input))
        ops = [
            Operation(op.name, strip_fields(op.params), op.returns, is_mutation=op.is_mutation)
            for op in self.operations
        ]
        return Schema(self.name, self.summary, types, ops)


def f(name: str, spec: str, doc: str | None = None, *, required: bool = True) -> Field:
    return Field(name, TypeRef.parse(spec), required, doc)


def opt(name: str, spec: str, doc: str | None = None) -> Field:
    return f(name, spec, doc, required=False)


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def pascal(name: str) -> str:
    return name[0].upper() + name[1:]
