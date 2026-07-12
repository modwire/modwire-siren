# Modwire Siren UI Profile

Status: **Approved — implementation authorized**  
Profile version: `1.0-draft`  
Profile identifier: `https://raw.githubusercontent.com/modwire/modwire-siren/main/docs/siren-ui-profile/README.md`
Schema: [`schema/profile.schema.json`](schema/profile.schema.json)

This document specifies a Siren profile for communicating semantic presentation,
interaction, and update hints without communicating framework components. It is the
approved design authority for the Python and npm implementations. The Python producer,
validation, discovery, and OpenAPI projection contract is implemented by `modwire-siren`;
the independent npm implementations remain separate delivery projects.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and
**MAY** are to be interpreted as described by RFC 2119 and RFC 8174 when, and only
when, they appear in capitals.

## 1. Goals

The profile enables a conforming client to:

1. render useful nested interfaces without knowing application routes;
2. select local components from semantic roles rather than server-selected names;
3. construct and submit forms from advertised Siren actions;
4. navigate and load related entities from Siren relations;
5. respond predictably to mutations, long-running operations, and problems;
6. degrade to ordinary Siren when profile semantics are unknown; and
7. expose the same entity graph and affordances through graphical and MCP clients.

The profile does not standardize colors, CSS, visual component libraries, browser
routing, application authorization, or business-domain vocabularies.

## 2. Compatibility with Siren

A profiled representation MUST remain a Siren representation. Profile metadata is
carried in an embedded Siren entity rather than unknown members on ordinary Siren
entities, actions, links, or fields.

The root entity MUST advertise the profile with both:

- a link whose `rel` contains `profile` and whose `href` is the profile identifier;
- the media type parameter
  `application/vnd.siren+json; profile="https://raw.githubusercontent.com/modwire/modwire-siren/main/docs/siren-ui-profile/README.md"`.

### Profile entity

The root entity MUST contain exactly one embedded profile entity with:

```json
{
  "class": ["modwire-ui-profile"],
  "rel": ["https://raw.githubusercontent.com/modwire/modwire-siren/main/docs/siren-ui-profile/README.md#profile-entity"],
  "properties": {"...": "profile metadata"},
  "entities": [],
  "actions": [],
  "links": []
}
```

An ordinary Siren client MAY ignore this sub-entity. A profile-aware client MUST
ignore profile metadata when the profile identifier or major version is unsupported
and MUST continue processing the base Siren document.

The embedded profile entity is control metadata and MUST NOT be presented as
application content unless a diagnostic client explicitly requests it.

## 3. Conformance classes

### 3.1 Producer

A conforming producer MUST emit schema-valid profile metadata, MUST omit unavailable
actions, and MUST ensure every metadata reference resolves within the containing
Siren entity.

### 3.2 Headless client

A conforming headless client MUST validate profile metadata, normalize the entity
graph deterministically, expose selection diagnostics, and retain access to the
unmodified Siren document.

### 3.3 Renderer

A conforming renderer MUST consume the normalized UI tree rather than interpreting
wire metadata independently. It MUST provide generic fallbacks for every required
node kind and MUST meet the accessibility requirements in section 13.

### 3.4 Extension

A conforming extension vocabulary MUST use an absolute URI as its identifier,
document fallback behavior, publish a schema, and define whether unknown values are
ignorable. It MUST NOT redefine a term owned by this profile version.

## 4. Profile metadata document

The embedded profile entity's `properties` object is the profile metadata document.
It has these members:

| Member | Requirement | Meaning |
| --- | --- | --- |
| `profile` | REQUIRED | Exact profile identifier. |
| `language` | OPTIONAL | BCP 47 language of literal presentation strings. |
| `presentation` | REQUIRED | Root entity presentation semantics. |
| `properties` | OPTIONAL | Metadata keyed by root property name. |
| `relations` | OPTIONAL | Metadata keyed by relation value. |
| `actions` | OPTIONAL | Metadata keyed by Siren action name. |
| `extensions` | OPTIONAL | Extension values keyed by absolute vocabulary URI. |

Unknown members MUST make the profile metadata invalid. Invalid profile metadata
MUST be reported and ignored as a unit; it MUST NOT make the base Siren document
unusable.

Optional enhancement members are absent, never `null`. Before projection or consumption,
a conforming implementation applies the defaults declared by the normative JSON Schema.
The defaults provide a complete baseline profile: flow layout, empty metadata maps and
regions, generic text/supporting properties, manual one-valued relations, secondary
entity actions with `none` results, automatic fields, zero ordering, and non-sensitive,
non-optimistic behavior. Explicit metadata progressively replaces those defaults.

## 5. Presentation

`presentation.role` communicates the semantic purpose of the current entity. The
defined roles are:

- `detail`: one complete resource;
- `summary`: a compact representation used inside another view;
- `collection`: a set of related item entities;
- `dashboard`: multiple independently meaningful regions;
- `document`: ordered narrative content;
- `tree`: hierarchical entities;
- `form`: an action-oriented input surface.

`presentation.layout` MAY refine organization. Defined layout kinds are `flow`,
`grid`, `master-detail`, `tabs`, and `stack`. Layout is a hint. A renderer MAY choose
another visual arrangement while preserving content order, relationships, and
available actions.

Regions provide semantic grouping:

```json
{
  "id": "identity",
  "label": "Identity",
  "order": 10,
  "content": {
    "properties": ["slug", "title"],
    "relations": [],
    "actions": ["revise_record"]
  }
}
```

Region IDs MUST be unique. A property, relation, or action SHOULD appear in no more
than one region. Unassigned content MUST remain available through a deterministic
`other` fallback region.

## 6. Property presentation

Property metadata MAY contain:

- `label` and `description`: localized literal fallbacks;
- `message`: a localization message identifier;
- `order`: stable ascending presentation order;
- `group`: semantic grouping identifier;
- `format`: `text`, `number`, `date`, `datetime`, `duration`, `currency`, `percent`,
  `code`, `markdown`, `uri`, `image`, `status`, or `hidden`;
- `unit`: a unit or currency code interpreted with the format;
- `importance`: `primary`, `secondary`, or `supporting`;
- `sensitive`: whether generic diagnostics and persistence MUST redact the value.

`hidden` is a presentation hint, not an information-security mechanism. A producer
MUST NOT serialize a secret merely because its format is `hidden`.

Metadata MUST reference an existing property. Properties without metadata MUST be
retained and rendered by a generic fallback unless the application renderer
deliberately suppresses unknown domain data.

## 7. Relation presentation and nested entities

Relation metadata MAY define:

- `role`: `item`, `detail`, `navigation`, `supplementary`, `choice-source`,
  `progress`, or `problem`;
- `loading`: `embedded`, `eager`, `lazy`, or `manual`;
- `cardinality`: `one` or `many`;
- `label`, `message`, `order`, and `region`.

An embedded representation MUST be normalized recursively. An embedded link with
`loading: eager` or `loading: lazy` MAY be resolved by a client according to its
resource and network policy. `manual` MUST require an explicit user or agent action.

Clients MUST detect entity cycles by canonical self link. A repeated entity MUST be
represented as a reference node rather than recursively expanded without bound.

A producer MUST NOT use automatic loading hints to bypass authorization or expose a
URL that the current principal is not allowed to discover.

## 8. Action presentation

Action metadata MAY contain:

- `intent`: `primary`, `secondary`, `destructive`, `navigation`, or `background`;
- `placement`: `entity`, `collection`, `item`, `inline`, or `overflow`;
- `label`, `description`, `message`, `order`, and `region`;
- `confirmation`: structured confirmation semantics;
- `fields`: field metadata keyed by action field name;
- `result`: post-submission behavior.

Metadata MUST reference an advertised Siren action. The server MUST omit actions the
current principal or entity state cannot execute. Renderers MUST NOT treat hiding or
disabling an advertised action as authorization enforcement.

A destructive action MUST declare `intent: destructive` and SHOULD declare a
confirmation. Confirmation metadata MAY require an acknowledgement and MAY include
a message identifier. It MUST NOT contain executable code.

## 9. Field presentation

Field metadata MAY define:

- `widget`: `automatic`, `text`, `textarea`, `number`, `toggle`, `select`,
  `multi-select`, `date`, `datetime`, `file`, `code`, or `hidden`;
- `label`, `description`, `message`, `placeholder`, `order`, and `group`;
- `choices`: an inline or relation-backed choice source;
- `visibleWhen` and `enabledWhen`: safe declarative predicates.

The Siren field remains the authority for its name, wire type, current value, and
submission. Profile metadata MUST NOT change the wire name or introduce a value that
the action does not accept.

A relation-backed choice source identifies a relation plus property paths for its
option value and label. It MUST NOT provide an arbitrary fetch URL.

Predicates have exactly `path`, `operator`, and optional `value`. Defined operators
are `exists`, `equals`, `not-equals`, `in`, `not-in`, `truthy`, and `falsy`. Paths
MUST begin with `properties/` or `fields/` and MUST NOT escape those namespaces.
Predicates affect presentation only. Unsupported predicates evaluate to `false` and
produce a diagnostic.

## 10. Action results and state transitions

`result.mode` is one of:

- `replace`: replace the current entity with a returned Siren entity;
- `refresh`: follow declared relations after success;
- `navigate`: use a declared relation from the response;
- `monitor`: follow a progress relation until it reaches a terminal state;
- `none`: retain the current representation.

The result MAY list `relations` to refresh. These are relation values, never URLs.
The producer MUST include `self` when the current entity must be reloaded.

`result.optimistic` defaults to `false`. It MAY be `true` only for an idempotent or
safely reversible interaction whose optimistic transformation is completely defined
by the specification. Version 1 defines no generic optimistic transformation;
therefore conforming v1 producers MUST use `false`. This deliberately reserves the
capability without inventing unsafe client behavior.

For `monitor`, a successful response MUST advertise the configured progress relation.
The progress entity SHOULD expose a `status` property with `pending`, `running`,
`succeeded`, or `failed`. Clients MUST apply backoff and MUST honor transport-level
retry guidance.

## 11. Deterministic normalization

A headless client MUST normalize a profiled entity using this algorithm:

1. Parse the base Siren entity without modifying it.
2. Locate profile discovery and the embedded profile entity.
3. If discovery is unsupported, absent, ambiguous, or invalid, emit one profile
   diagnostic and construct a generic Siren tree.
4. Validate metadata against the schema for the discovered profile version.
5. Index properties, relations, actions, and fields by their Siren identities.
6. Reject dangling metadata references and duplicate Siren identities.
7. Create regions ordered by `(order, id)` and add an `other` region when required.
8. Create property nodes ordered by `(order, property-name)`.
9. Create relation nodes ordered by `(order, relation-value)` and recursively
   normalize embedded representations in document order.
10. Create action nodes ordered by `(order, action-name)` and field nodes ordered by
    `(order, field-name)`.
11. Resolve component semantics using section 12.
12. Return the UI tree, original Siren entity, profile metadata, and diagnostics.

Repeated normalization of identical input and supported-vocabulary configuration
MUST produce structurally identical output.

## 12. Component resolution

The server MUST NOT name a React, Vue, Svelte, Web Component, CSS class, or application
component. A renderer owns a local registry and resolves a component in this order:

1. application rule matching domain class plus semantic role;
2. application rule matching relation or action name plus semantic role;
3. profile rule matching semantic role, format, intent, or widget;
4. generic node-kind fallback;
5. diagnostic unsupported fallback.

The first match wins. Registration order MUST NOT affect results among rules of
different specificity. Equal-specificity ambiguity MUST produce a diagnostic and use
the generic fallback unless the local registry declares a deterministic priority.

Every resolution MUST expose the selected rule identifier and match reasons for
inspection by developers, tests, and MCP clients.

## 13. Accessibility

A renderer MUST:

- preserve meaningful source order independently of visual layout;
- provide programmatic labels for actions and fields;
- expose validation and problem messages to assistive technology;
- support keyboard operation for every advertised action;
- preserve focus predictably after replace, refresh, and navigation results;
- not rely on color alone for intent or status; and
- allow a destructive confirmation to be understood and cancelled.

Profile labels are fallbacks. A renderer remains responsible for platform-specific
accessibility semantics.

## 14. Localization

Literal strings are interpreted using the metadata document's `language`. `message`
identifiers MAY be resolved by a local message catalog. If resolution fails, the
literal label or description MUST be used. If neither exists, a deterministic label
MUST be derived from the Siren identity without changing that identity.

The server MUST NOT send executable message templates. Parameters, when introduced by
an extension vocabulary, MUST be data values and MUST be escaped by the renderer.

## 15. Security and privacy

- Authorization is server-authoritative. Unavailable actions MUST be absent.
- Profile conditions MUST NOT be used as access-control rules.
- Clients MUST apply their ordinary same-origin and transport policy to followed
  links and actions.
- Rich text MUST be sanitized by the renderer. `markdown` never implies trusted HTML.
- Sensitive properties and fields MUST be redacted from logs, persisted UI state,
  analytics, and diagnostics.
- Profile metadata MUST NOT contain executable JavaScript, HTML event handlers,
  framework component names, dynamic imports, or arbitrary fetch URLs.
- File actions remain subject to the action media type and client upload policy.

## 16. Problems and invalid profile data

Transport and application failures SHOULD use a structured problem document. A
client MUST preserve the complete remote problem and associate field violations with
matching action fields when possible.

Profile validation failures are non-fatal to base Siren processing. Diagnostics MUST
include a stable code, JSON Pointer, severity, and human-readable message. Defined
codes include:

- `profile.missing`
- `profile.ambiguous`
- `profile.unsupported`
- `profile.invalid`
- `profile.dangling-reference`
- `profile.duplicate-identity`
- `profile.component-ambiguity`
- `profile.predicate-unsupported`

## 17. Versioning

The profile URI identifies a major version. Additive schema changes MAY be published
within the same major only when older clients ignore them safely. Since this schema
rejects unknown members, an additive member requires a new schema revision and an
explicit capability mechanism before it can be considered compatible.

Removing or redefining vocabulary, changing normalization order, or changing fallback
behavior requires a new major profile URI.

Documents MUST declare exactly one major profile. A client MAY support multiple major
versions but MUST normalize each using that version's complete rules.

## 18. Independent implementation projects

After owner approval, implementations MUST be separated as follows:

| Project | Responsibility | Allowed dependency |
| --- | --- | --- |
| `modwire-siren` | Specification, schemas, Python Siren/profile contracts, OpenAPI projection | Pydantic and Python foundations |
| TypeScript Siren client | Wire parsing, validation, traversal, transport-independent action execution | Published schema/conformance artifacts |
| TypeScript UI runtime | Normalization, UI tree, predicates, component registry, state transitions | Published TypeScript Siren client |
| React renderer | React bindings and generic reference components | Published UI runtime; React as peer dependency |

Each npm package MUST live in its own repository and own its manifest, lockfile, CI,
tests, documentation, provenance, and SemVer release lifecycle. Monorepos, workspace
coupling, sibling checkouts, filesystem dependencies, and unpublished cross-project
source imports are forbidden.

Each npm repository MUST be initialized through the approved npm package scaffold before
implementation code is added. The scaffold preview and variables MUST be reviewed, generated-file
ownership MUST be explicit, and the applied result MUST be idempotent. The scaffold MUST establish
the package manifest, lockfile policy, source/test layout, TypeScript strictness, formatting and
linting, CI, npm provenance, release workflow, documentation baseline, package-content checks, and
clean-environment verification. Package tasks MAY extend these defaults but MUST NOT hand-assemble
or silently diverge from the approved scaffold contract.

Repository and npm package names are intentionally not normative and require owner
approval with this specification.

## 19. Conformance artifacts

This directory contains:

- `schema/profile.schema.json`: normative profile metadata schema;
- `examples/valid/`: valid complete Siren representations;
- `examples/invalid/`: metadata documents that MUST fail validation;
- `examples/normalized/`: expected framework-neutral UI trees.

Every normative rule MUST eventually be covered by a positive or negative fixture.
The initial draft corpus demonstrates the principal interaction shapes and establishes
the file contract; completeness is tracked in [`review-checklist.md`](review-checklist.md).

The schema `$id` is its immutable public source location in this repository:
`https://raw.githubusercontent.com/modwire/modwire-siren/main/docs/siren-ui-profile/schema/profile.schema.json`.

## 20. Approved decisions and deferred project naming

1. Profile, relation, and schema identifiers resolve to their public source files in
   `modwire/modwire-siren` through `raw.githubusercontent.com`.
2. Literal strings and message identifiers may coexist; section 14 defines fallback precedence.
3. `result.optimistic` remains reserved throughout v1.
4. V1 uses the constrained property paths defined in the schema; adopting a general pointer
   standard requires a later profile revision.
5. The conformance corpus remains in `modwire-siren` unless independent governance becomes
   necessary.
6. V1 has no client-driven presentation negotiation.
7. Exact repository names and npm scopes are intentionally deferred until each independent
   implementation project is created. Naming does not alter the normative package boundaries.

Implementation tasks MUST preserve these decisions. A normative change requires a specification
revision and renewed owner approval.
