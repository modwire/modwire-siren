# Owner review checklist

The proposal is not approved until every checkbox has an explicit owner decision.

## Standard boundary

- [x] The embedded profile entity is the approved metadata carrier.
- [x] The profile link plus media-type parameter is the approved discovery mechanism.
- [x] Unknown or invalid profile metadata falls back to ordinary Siren.
- [x] Server vocabulary remains semantic and framework-independent.

## Interaction model

- [x] Entity roles and layout hints are sufficient but not overly visual.
- [x] Property formats and sensitivity rules are acceptable.
- [x] Relation loading semantics are safe and complete.
- [x] Action intent, confirmation, and result behavior are acceptable.
- [x] Field widgets, choice sources, and predicates remain declarative and safe.
- [x] Optimistic behavior remains reserved in v1.

## Client behavior

- [x] Normalization ordering is deterministic and intuitive.
- [x] Component resolution belongs entirely to local renderer registries.
- [x] Generic fallback behavior is sufficient for unknown application vocabulary.
- [x] Diagnostics are complete enough for UI and MCP clients.

## Quality attributes

- [x] Authorization remains server-authoritative.
- [x] Accessibility requirements are normative at the right layer.
- [x] Localization fallback is deterministic.
- [x] Security and sensitive-data requirements are adequate.
- [x] Major-version compatibility policy is acceptable.

## Project boundaries

- [x] The specification and Python implementation remain in `modwire-siren`.
- [x] Every npm package is an independent repository and release project.
- [x] TypeScript Siren client and UI runtime are separate packages.
- [x] React renderer is separate and treats React as a peer dependency.
- [x] No implementation repository is created before specification approval.
- [x] Every npm repository starts from the approved, reviewed, idempotent npm package scaffold.

## Naming and ownership

- [x] Approve the profile URI.
- [x] Approve the relation URI.
- [x] Keep npm organization/scope and final package names non-normative until repository creation.
- [x] Keep conformance artifacts in `modwire-siren` unless independent governance becomes necessary.

## Approval record

Owner: 9orky  
Decision: `approved`  
Approved profile revision: local `1.0-draft` specification  
Date: 2026-07-12  
Conditions or requested changes: npm packages must be independent projects; the specification and Python implementation remain in `modwire-siren`.
