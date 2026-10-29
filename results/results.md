# Results

## Totals across all fixtures

| Format | Kind | Claude (claude-opus-5-5), documented | Claude (claude-opus-5-5), bare | OpenAI (o200k_base), documented | OpenAI (o200k_base), bare | Bytes, documented | Bytes, bare |
|---|---|--:|--:|--:|--:|--:|--:|
| GraphQL SDL | API description | 1,785 (0.40×) | 906 (0.28×) | 1,147 (0.36×) | 572 (0.24×) | 4,299 (0.32×) | 1,941 (0.20×) |
| Python type hints | Prompt notation | 1,907 (0.43×) | 1,039 (0.32×) | 1,242 (0.39×) | 662 (0.28×) | 5,042 (0.37×) | 2,536 (0.26×) |
| TypeScript | Prompt notation | 1,963 (0.44×) | 946 (0.29×) | 1,239 (0.39×) | 590 (0.25×) | 4,895 (0.36×) | 2,229 (0.23×) |
| Protobuf / gRPC | API description | 2,562 (0.58×) | 1,732 (0.53×) | 1,515 (0.47×) | 977 (0.41×) | 5,908 (0.44×) | 3,604 (0.38×) |
| JSON Schema (YAML) | API description | 2,975 (0.67×) | 2,047 (0.62×) | 2,168 (0.68×) | 1,521 (0.64×) | 9,108 (0.67×) | 5,811 (0.61×) |
| JSON Schema (minified) | API description | 3,059 (0.69×) | 2,135 (0.65×) | 1,844 (0.58×) | 1,237 (0.52×) | 7,907 (0.58×) | 4,792 (0.50×) |
| JSON Schema | API description | 4,419 (1.00×) | 3,282 (1.00×) | 3,197 (1.00×) | 2,381 (1.00×) | 13,567 (1.00×) | 9,571 (1.00×) |

## Per fixture

### Claude (claude-opus-5-5) tokens

| Format | Kind | user (documented) | commerce (documented) | calendar (documented) | user (bare) | commerce (bare) | calendar (bare) | documented total | bare total | documented vs JSON Schema | bare vs JSON Schema |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GraphQL SDL | API description | 118 | 780 | 887 | 49 | 357 | 500 | 1785 | 906 | 0.40× | 0.28× |
| Python type hints | Prompt notation | 129 | 822 | 956 | 77 | 414 | 548 | 1907 | 1039 | 0.43× | 0.32× |
| TypeScript | Prompt notation | 136 | 869 | 958 | 53 | 369 | 524 | 1963 | 946 | 0.44× | 0.29× |
| Protobuf / gRPC | API description | 147 | 977 | 1438 | 92 | 568 | 1072 | 2562 | 1732 | 0.58× | 0.53× |
| JSON Schema (YAML) | API description | 155 | 1223 | 1597 | 93 | 763 | 1191 | 2975 | 2047 | 0.67× | 0.62× |
| JSON Schema (minified) | API description | 162 | 1235 | 1662 | 105 | 778 | 1252 | 3059 | 2135 | 0.69× | 0.65× |
| JSON Schema | API description | 243 | 1762 | 2414 | 168 | 1196 | 1918 | 4419 | 3282 | 1.00× | 1.00× |

### OpenAI (o200k_base) tokens

| Format | Kind | user (documented) | commerce (documented) | calendar (documented) | user (bare) | commerce (bare) | calendar (bare) | documented total | bare total | documented vs JSON Schema | bare vs JSON Schema |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GraphQL SDL | API description | 82 | 509 | 556 | 35 | 234 | 303 | 1147 | 572 | 0.36× | 0.24× |
| TypeScript | Prompt notation | 92 | 555 | 592 | 37 | 236 | 317 | 1239 | 590 | 0.39× | 0.25× |
| Python type hints | Prompt notation | 87 | 543 | 612 | 50 | 271 | 341 | 1242 | 662 | 0.39× | 0.28× |
| Protobuf / gRPC | API description | 99 | 612 | 804 | 61 | 348 | 568 | 1515 | 977 | 0.47× | 0.41× |
| JSON Schema (minified) | API description | 105 | 759 | 980 | 64 | 458 | 715 | 1844 | 1237 | 0.58× | 0.52× |
| JSON Schema (YAML) | API description | 123 | 894 | 1151 | 77 | 573 | 871 | 2168 | 1521 | 0.68× | 0.64× |
| JSON Schema | API description | 187 | 1277 | 1733 | 129 | 869 | 1383 | 3197 | 2381 | 1.00× | 1.00× |

### Bytes (UTF-8)

| Format | Kind | user (documented) | commerce (documented) | calendar (documented) | user (bare) | commerce (bare) | calendar (bare) | documented total | bare total | documented vs JSON Schema | bare vs JSON Schema |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GraphQL SDL | API description | 298 | 1851 | 2150 | 107 | 777 | 1057 | 4299 | 1941 | 0.32× | 0.20× |
| TypeScript | Prompt notation | 357 | 2101 | 2437 | 131 | 850 | 1248 | 4895 | 2229 | 0.36× | 0.23× |
| Python type hints | Prompt notation | 368 | 2104 | 2570 | 202 | 1007 | 1327 | 5042 | 2536 | 0.37× | 0.26× |
| Protobuf / gRPC | API description | 380 | 2244 | 3284 | 212 | 1167 | 2225 | 5908 | 3604 | 0.44× | 0.38× |
| JSON Schema (minified) | API description | 475 | 3210 | 4222 | 239 | 1716 | 2837 | 7907 | 4792 | 0.58× | 0.50× |
| JSON Schema (YAML) | API description | 555 | 3756 | 4797 | 293 | 2155 | 3363 | 9108 | 5811 | 0.67× | 0.61× |
| JSON Schema | API description | 794 | 5379 | 7394 | 490 | 3424 | 5657 | 13567 | 9571 | 1.00× | 1.00× |
