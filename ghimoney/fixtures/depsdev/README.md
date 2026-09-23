# deps.dev real fixtures (T-19A)

Every file here wraps a response body **actually observed** during T-19A
(`docs/DEPS_DEV_EMPIRICAL_VERIFICATION.md`), as `{"status": <int>, "body": <json-or-string>}`.
None of this data is invented.

The large `GetPackage` bodies (`t1_*`, `t5_*`, `t8_*`, `t10_*`) are **trimmed**:
the real response listed every published version (dozens to ~150 entries); only
a small, real subset is kept here, since evidence logic only reads the HTTP
status of this endpoint, never its content.

`t4_npm_express_dependencies.json` is also **trimmed**: the real graph had
~70 nodes; a real subset of 37 (31 `DIRECT` + 6 `INDIRECT`, plus `SELF`) is
kept, enough to exercise the DIRECT/INDIRECT counting logic. Tests assert
against this file's own counts (31/37), not against the original full graph.

Every other file is the complete, unmodified real body from its T-19A test.

| File | T-19A test | Real call |
|---|---|---|
| `t1_npm_lodash_package.json` | T1 (trimmed) | `GET /v3/systems/npm/packages/lodash` |
| `t3_npm_lodash_leaf_dependencies.json` | T3 | `GET .../lodash/versions/4.17.21:dependencies` |
| `t4_npm_express_dependencies.json` | T4 | `GET .../express/versions/4.19.2:dependencies` |
| `t5_pypi_requests_package.json` | T5 (trimmed) | `GET /v3/systems/pypi/packages/requests` |
| `t6_pypi_requests_version.json` | T6 | `GET .../requests/versions/2.31.0` |
| `t7_pypi_requests_dependencies.json` | T7 | `GET .../requests/versions/2.31.0:dependencies` |
| `t8_maven_guava_package.json` | T8 (trimmed) | `GET /v3/systems/maven/packages/com.google.guava%3Aguava` |
| `t9_maven_guava_dependencies.json` | T9 | `GET .../guava/versions/32.1.3-jre:dependencies` |
| `t10_go_pkgerrors_package.json` | T10 (trimmed) | `GET /v3/systems/go/packages/github.com%2Fpkg%2Ferrors` |
| `t11_go_pkgerrors_requirements.json` | T11 | `GET .../pkg%2Ferrors/versions/v0.9.1:requirements` |
| `t12_go_pkgerrors_dependencies_404.json` | T12 | `GET .../pkg%2Ferrors/versions/v0.9.1:dependencies` → 404 |
| `t13_cargo_serde_version.json` | T13 | `GET /v3/systems/cargo/packages/serde/versions/1.0.203` |
| `t14_cargo_serde_dependencies.json` | T14 | `GET .../serde/versions/1.0.203:dependencies` |
| `t15_npm_nonexistent_404.json` | T15 | `GET .../packages/this-package-does-not-exist-ghimoney-test-12345` → 404 |
| `t20a_npm_lodash_dependents.json` | T20A | `GET /v3alpha/systems/npm/packages/lodash/versions/4.17.21:dependents` |
| `t20a_pypi_requests_dependents.json` | T20A | `GET /v3alpha/systems/pypi/packages/requests/versions/2.31.0:dependents` |
| `t20a_maven_guava_dependents.json` | T20A | `GET /v3alpha/systems/maven/packages/com.google.guava%3Aguava/versions/32.1.3-jre:dependents` |
| `t20a_cargo_serde_dependents.json` | T20A | `GET /v3alpha/systems/cargo/packages/serde/versions/1.0.203:dependents` |
| `t20a_go_pkgerrors_dependents_404.json` | T20A | `GET .../go/.../pkg%2Ferrors/versions/v0.9.1:dependents` → 404 "dependents not found" |
| `t20a_npm_nonexistent_dependents_404.json` | T20A | `GET .../this-package-does-not-exist-ghimoney-test-12345/...:dependents` → 404 "dependents not found" (same message as the Go structural gap, hence ambiguous by body alone) |
