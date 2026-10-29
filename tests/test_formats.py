"""Every generated file must be valid in its own language, and every format
must mention every type, field, and operation from the fixture."""

import ast
import json
import shutil
import subprocess

import pytest
import yaml
from graphql import build_schema, validate_schema
from jsonschema import Draft202012Validator

from schema_token_bench.cli import VARIANTS, render
from schema_token_bench.fixtures import ALL
from schema_token_bench.model import Enum, Object, Schema, pascal, snake

CASES = [(s, v) for s in ALL for v in VARIANTS]
IDS = [f"{s.name}-{v}" for s, v in CASES]


@pytest.fixture(params=CASES, ids=IDS)
def outputs(request) -> tuple[Schema, dict[str, str]]:
    schema, variant = request.param
    return schema, render(schema, variant)


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
