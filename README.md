# schema-token-bench

How many tokens does it take to describe the same schema to an LLM in JSON Schema, GraphQL SDL, Protobuf/gRPC, TypeScript, or Python type hints?

Each schema is defined once in a format-neutral model ([`fixtures.py`](src/schema_token_bench/fixtures.py)) and rendered into every format, so all formats describe the same types, fields, enums, and operations. Claude token counts come from the [`count_tokens`](https://docs.claude.com/en/docs/build-with-claude/token-counting) API, and OpenAI counts come from `tiktoken`.

## Results

Totals across the three fixtures. The ratio in parentheses is relative to pretty-printed JSON Schema. "Documented" has descriptions on types, fields, and operations; "bare" has none.

<!-- results:start -->
| Format | Kind | Claude (claude-opus-5-5), documented | Claude (claude-opus-5-5), bare | OpenAI (o200k_base), documented | OpenAI (o200k_base), bare | Bytes, documented | Bytes, bare |
|---|---|--:|--:|--:|--:|--:|--:|
| GraphQL SDL | API description | 1,785 (0.40×) | 906 (0.28×) | 1,147 (0.36×) | 572 (0.24×) | 4,299 (0.32×) | 1,941 (0.20×) |
| Python type hints | Prompt notation | 1,907 (0.43×) | 1,039 (0.32×) | 1,242 (0.39×) | 662 (0.28×) | 5,042 (0.37×) | 2,536 (0.26×) |
| TypeScript | Prompt notation | 1,963 (0.44×) | 946 (0.29×) | 1,239 (0.39×) | 590 (0.25×) | 4,895 (0.36×) | 2,229 (0.23×) |
| Protobuf / gRPC | API description | 2,562 (0.58×) | 1,732 (0.53×) | 1,515 (0.47×) | 977 (0.41×) | 5,908 (0.44×) | 3,604 (0.38×) |
| JSON Schema (YAML) | API description | 2,975 (0.67×) | 2,047 (0.62×) | 2,168 (0.68×) | 1,521 (0.64×) | 9,108 (0.67×) | 5,811 (0.61×) |
| JSON Schema (minified) | API description | 3,059 (0.69×) | 2,135 (0.65×) | 1,844 (0.58×) | 1,237 (0.52×) | 7,907 (0.58×) | 4,792 (0.50×) |
| JSON Schema | API description | 4,419 (1.00×) | 3,282 (1.00×) | 3,197 (1.00×) | 2,381 (1.00×) | 13,567 (1.00×) | 9,571 (1.00×) |
<!-- results:end -->

Per-fixture tables: [`results/results.md`](results/results.md). Raw numbers: [`results/results.json`](results/results.json). Every generated file is in [`generated/`](generated/), so you can read exactly what was counted.

### Takeaways

- **GraphQL SDL is the most compact format overall**, at about 0.4× the tokens of JSON Schema with docs and under 0.3× without. The two prompt notations, TypeScript and Python, are close behind, so a standard format costs nothing extra here.
- **Minifying JSON Schema or converting it to YAML saves a third to a half.** That's the whitespace and punctuation. The repeated `"type"`, `"properties"`, and `"required"` keys are still there.
- **Protobuf falls in between.** Field numbers, prefixed enum values, and the request/response message every RPC needs all cost tokens. It falls furthest behind on the `calendar` tools fixture, at about 1.6× GraphQL's tokens.
- **Descriptions narrow the gap.** Prose costs about the same in every format, so the more documented a schema is, the less the notation matters.
- **The tokenizers mostly agree.** Claude's tokenizer produces more tokens than `o200k_base` for the same text, and the ranking is the same with one exception. YAML beats minified JSON under Claude, and minified JSON wins under `o200k_base`.

My read: if you write the prompt yourself, describe types in GraphQL SDL or TypeScript. Models know both well, and they cost less than half as much as JSON Schema. If an API makes you send JSON Schema, as tool-calling APIs do, minifying it is the cheapest fix.

## What's being compared

| Fixture | Contents |
|---|---|
| `user` | One object type with five fields |
| `commerce` | Seven types with nested objects, lists, an enum, and optional fields |
| `calendar` | Seven agent tools with parameters and return types, plus the types they use |

The formats come in two kinds. **API description** formats are what people publish APIs in: JSON Schema, GraphQL SDL, and Protobuf. **Prompt notations** are TypeScript and Python type hints. Nobody publishes an API in them, but they're a common way to describe one to a model. OpenAI's open-weight gpt-oss models, for example, see tool definitions as TypeScript-style declarations in the [harmony format](https://cookbook.openai.com/articles/openai-harmony).

| Format | Kind | Rendering |
|---|---|---|
| JSON Schema | API description | Draft 2020-12, 2-space indent. Types go under `$defs`. Operations are Anthropic-style tool definitions with `name`, `description`, and `input_schema`, plus an `output_schema`. Both schemas reference the shared `$defs`. |
| JSON Schema (minified) | API description | Same document, no whitespace. |
| JSON Schema (YAML) | API description | Same document, in YAML. This is how most OpenAPI specs are written. |
| GraphQL SDL | API description | Read operations go on `Query`, writes on `Mutation`. Object-valued arguments use `input` types. |
| Protobuf / gRPC | API description | proto3 following the [style guide](https://protobuf.dev/programming-guides/style/): `snake_case` fields, prefixed enum values with an `UNSPECIFIED` zero, and a `FooRequest` message per RPC. |
| TypeScript | Prompt notation | `interface`s, string-literal unions for enums, and `declare function name(args: {...}): Result` signatures. |
| Python type hints | Prompt notation | `TypedDict` classes, `Literal` aliases for enums, and stub functions with Google-style docstrings. |

The bare `user` fixture in three of them:

```graphql
scalar DateTime

type User {
  id: ID!
  name: String!
  email: String
  age: Int
  createdAt: DateTime!
}
```

```ts
type DateTime = string;

interface User {
  id: string;
  name: string;
  email?: string;
  age?: number;
  createdAt: DateTime;
}
```

```json
{"$defs":{"User":{"type":"object","properties":{"id":{"type":"string"},"name":{"type":"string"},"email":{"type":"string"},"age":{"type":"integer"},"createdAt":{"type":"string","format":"date-time"}},"required":["id","name","createdAt"]}}}
```

## Methodology and fairness

- **Idiomatic output.** Each format uses its own naming, so `createdAt` in GraphQL is `created_at` in Protobuf and Python. Docs use each format's syntax: `"..."` in GraphQL, `/** ... */` in TypeScript, `//` in Protobuf, docstrings and `#` comments in Python, and `description` in JSON Schema. Signatures go on one line if they fit in 80 columns and have no per-parameter docs, as prettier and black would format them.
- **The formats don't carry identical information.** proto3 has no way to mark a field required, so Protobuf leaves that out. JSON Schema documents enum values with `oneOf` + `const`, because `enum` has no per-value descriptions.
- **Timestamps.** JSON Schema uses `format: date-time`, Protobuf uses `google.protobuf.Timestamp`, and Python uses `datetime`. GraphQL and TypeScript have no built-in date type, so each declares a `DateTime` alias once.
- **No `$schema` or `additionalProperties: false`** in JSON Schema. LLM tool definitions usually leave out `$schema`. Strict tool use requires `additionalProperties: false`, which would make JSON Schema even bigger.
- **Shared types aren't repeated.** MCP and most real tool definitions inline the referenced types into every tool's schema. That makes JSON Schema even larger than shown here.
- **Message overhead is subtracted.** `count_tokens` counts a full user message, so the benchmark measures a one-token message once per model and subtracts the difference.
- **Validity is tested.** [`tests/test_formats.py`](tests/test_formats.py) checks that every output is valid in its own language using the JSON Schema meta-schema, `graphql-core`, `protoc`, `tsc --strict`, and running the Python. It also checks that every type, field, enum value, and operation shows up in every format.

## Running it

Requires [uv](https://docs.astral.sh/uv/).

```sh
export ANTHROPIC_API_KEY=...
uv run schema-token-bench                     # Claude (claude-opus-5-5) + tiktoken o200k_base
uv run schema-token-bench --model claude-opus-5-5 --model claude-sonnet-4-6   # compare Claude tokenizers
uv run schema-token-bench --no-claude          # offline, tiktoken only
uv run pytest                                  # validity checks (protoc and bunx tests skip if not installed)
```

A run regenerates `generated/`, writes `results/`, and updates the table above. Claude counts are cached in `.cache/`.

## Adding a format or fixture

- To add a format, write an `emit(schema) -> str` function in [`src/schema_token_bench/emitters/`](src/schema_token_bench/emitters/) and register it in [`emitters/__init__.py`](src/schema_token_bench/emitters/__init__.py). Add a validity test.
- To add a fixture, add a `Schema` to [`fixtures.py`](src/schema_token_bench/fixtures.py) and append it to `ALL`. List types in dependency order.

## License

MIT
