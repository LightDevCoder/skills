# v0.2.0 limitations

[中文记录](LIMITATIONS.zh-CN.md)

- `evals.json` is a semantic regression fixture, not an executed model-evaluation harness; it is reviewed as spec coverage.
- Fresh installation verification tests CLI discovery and structure in clean, isolated environments; live host refresh and model runtime execution on specific proprietary agents remain host-dependent and are not claimed beyond CLI discovery.
- Name collisions: Light approved Ports are self-contained and do not depend on `mattpocock/skills`. However, installing both collections into the same physical destination directory without namespace scoping may result in filename collisions depending on host precedence rules. Project-scoped installation is recommended when managing multiple collections.
