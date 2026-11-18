"""Every generated file must be valid in its own language, and every format
must mention every type, field, and operation from the fixture."""

import ast
import json
import re
import shutil
import subprocess
from dataclasses import replace

import pytest
import yaml
from graphql import build_schema, validate_schema
from jsonschema import Draft202012Validator

from schema_token_bench.cli import VARIANTS, render
from schema_token_bench.fixtures import ALL
from schema_token_bench.model import (
    Enum,
    EnumValue,
    Field,
    Object,
    Operation,
    Schema,
    TypeRef,
    pascal,
    snake,
)

CASES = [(s, v) for s in ALL for v in VARIANTS]
IDS = [f"{s.name}-{v}" for s, v in CASES]


@pytest.fixture(params=CASES, ids=IDS)
def outputs(request) -> tuple[Schema, dict[str, str]]:
    schema, variant = request.param
    return VARIANTS[variant](schema), render(schema, variant)


def check_json_schema(doc: dict) -> None:
    Draft202012Validator.check_schema(doc)
    for tool in doc.get("tools", []):
        # Tools reference shared types, so validate them with $defs in scope.
        for key in ("input_schema", "output_schema"):
            Draft202012Validator.check_schema({"$defs": doc["$defs"], **tool[key]})


def test_jsonschema(outputs):
    _, out = outputs
    pretty = json.loads(out["jsonschema"])
    assert json.loads(out["jsonschema-min"]) == pretty
    assert yaml.safe_load(out["jsonschema-yaml"]) == pretty
    check_json_schema(pretty)


def test_graphql(outputs):
    schema, out = outputs
    built = build_schema(out["graphql"])
    if schema.operations:
        assert validate_schema(built) == []


def test_python(outputs):
    _, out = outputs
    code = out["python"]
    ast.parse(code)
    exec(compile(code, "<generated>", "exec"), {})  # noqa: S102 -- our own generated stubs


@pytest.mark.skipif(not shutil.which("protoc"), reason="protoc not installed")
def test_protobuf(outputs, tmp_path):
    schema, out = outputs
    (tmp_path / f"{schema.name}.proto").write_text(out["protobuf"])
    subprocess.run(
        ["protoc", f"-I{tmp_path}", "--descriptor_set_out=/dev/null", f"{schema.name}.proto"],
        check=True,
        capture_output=True,
        cwd=tmp_path,
    )


@pytest.mark.skipif(not shutil.which("bunx"), reason="bunx not installed")
def test_typescript(outputs, tmp_path):
    schema, out = outputs
    path = tmp_path / f"{schema.name}.d.ts"
    path.write_text(out["typescript"])
    result = subprocess.run(
        ["bunx", "-p", "typescript", "tsc", "--noEmit", "--strict", "--lib", "es2022", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def parse_compact(text: str) -> tuple[list[Object | Enum], list[Operation]]:
    """Compact SDL has no parser of its own, so read it back into the model."""
    types: list[Object | Enum] = []
    ops: list[Operation] = []
    doc = None
    body: list | None = None  # members of the open `{`, `(`, or multi-line enum

    def ref(spec: str) -> TypeRef:
        return TypeRef(spec.removesuffix("[]"), spec.endswith("[]"))

    def split(line: str) -> tuple[str, str | None]:
        code, _, comment = line.partition(" # ")
        return code, comment or None

    def member(line: str) -> Field:
        code, doc = split(line)
        name, spec = code.split(" ")
        return Field(name, ref(spec.removesuffix("?")), not spec.endswith("?"), doc)

    for line in text.splitlines():
        if line.startswith("# "):
            doc = line[2:]
            continue
        if line.startswith("| "):
            body.append(EnumValue(*split(line[2:])))
        elif line in ("", "}"):
            body = None
        elif line.startswith(") "):
            ops[-1].returns = ref(line[2:])
            body = None
        elif body is not None:
            body.append(member(line))
        elif m := re.fullmatch(r"(\w+) \{", line):
            types.append(Object(m[1], [], doc))
            body = types[-1].fields
        elif m := re.fullmatch(r"(\w+) =( .*)?", line):
            values = [EnumValue(v) for v in m[2].strip().split(" | ")] if m[2] else []
            types.append(Enum(m[1], values, doc))
            body = None if values else types[-1].values
        elif m := re.fullmatch(r"(\w+)\((.*)\) (\S+)", line):
            params = [member(p) for p in m[2].split(", ")] if m[2] else []
            ops.append(Operation(m[1], params, ref(m[3]), doc))
        elif m := re.fullmatch(r"(\w+)\(", line):
            ops.append(Operation(m[1], [], TypeRef(""), doc))
            body = ops[-1].params
        else:
            raise ValueError(f"unparsed line: {line!r}")
        doc = None
    return types, ops


def test_compact_round_trips(outputs):
    """Every type, field, optionality, list, enum value, and doc can be read
    back. Only GraphQL's input/type and query/mutation splits are dropped."""
    schema, out = outputs
    types, ops = parse_compact(out["compact"])
    expected_types = [replace(t, is_input=False) if isinstance(t, Object) else t for t in schema.types]
    assert types == expected_types
    assert ops == [replace(op, is_mutation=False) for op in schema.operations]


def names(schema: Schema) -> dict[str, list[str]]:
    """Names each format must contain, in that format's naming convention."""
    camel = [t.name for t in schema.types]
    camel += [f.name for t in schema.types if isinstance(t, Object) for f in t.fields]
    camel += [op.name for op in schema.operations]
    camel += [p.name for op in schema.operations for p in op.params]
    values = [v.name for t in schema.types if isinstance(t, Enum) for v in t.values]
    types = [t.name for t in schema.types]
    fields = [f.name for t in schema.types if isinstance(t, Object) for f in t.fields]
    fields += [p.name for op in schema.operations for p in op.params]
    return {
        "jsonschema": camel + values,
        "graphql": camel + values,
        "compact": camel + values,
        "typescript": camel + values,
        "protobuf": types
        + [snake(n) for n in fields]
        + [pascal(op.name) for op in schema.operations]
        + values,
        "python": types + [snake(n) for n in fields] + [snake(op.name) for op in schema.operations] + values,
    }


def test_formats_are_complete(outputs):
    schema, out = outputs
    for fmt, expected in names(schema).items():
        missing = [n for n in expected if n not in out[fmt]]
        assert not missing, f"{fmt} is missing {missing}"
