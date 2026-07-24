# Architecture configuration

`architecture.yaml` describes the source-tree boundaries and structural limits that Modwire checks. Adapt its paths and names before enforcing it in a project.

## Tags

Each tag gives a source-tree pattern a meaningful name. The example uses compact YAML mappings to keep the relationship visible:

```yaml
tags:
  - {name: &module_tag module, match: src/*}
  - {name: &shared_tag shared, match: src/shared}
```

`&module_tag` anchors the scalar value `module`; `*module_tag` inserts that same string elsewhere in the file. This avoids repeating tag names:

```yaml
rules:
  - {source: *module_tag, disallow: [*module_tag], allow: [*shared_tag], allow_same_match: true}
```

Anchor the `name` value, not the whole tag object. Rule `source` and `allow` fields, and flow `module_tag` and `layers` fields, accept tag-name strings rather than `{name, match}` objects.

## Rules and flow

Rules describe which tagged modules may depend on one another. Flow groups tags into a module realm and, when needed, orders its layers:

```yaml
flow:
  realms:
    - {name: backend, module_tag: *backend_module_tag, layers: [*api_tag, *application_tag, *infrastructure_tag, *domain_tag]}
```

Use aliases consistently when a tag name appears in more than one place. The supplied `architecture.yaml` is a complete, adaptable example; keep its shape limits only when they suit the project.
