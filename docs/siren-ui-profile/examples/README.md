# Conformance example catalog

All examples under `valid/` are complete Siren representations. The conformance test extracts the
embedded profile entity and validates its `properties` against the normative schema. Files under
`invalid/` are profile metadata documents and must fail validation.

| Requirement | Fixture |
| --- | --- |
| Detail, regions, nested entity, lazy choices, editable form | `valid/entity-detail.json` |
| Collection, pagination, filtering, summaries, master-detail | `valid/collection.json` |
| Background and destructive actions, confirmation, monitor result | `valid/background-action.json` |
| Dependent fields and inline choices | `valid/conditional-form.json` |
| Localization identifiers and document presentation | `valid/localized-document.json` |
| Authorization-dependent action omission | `valid/authorized-actions.json` |
| Structured problem relation and sensitive property | `valid/problem.json` |
| Expected framework-neutral tree | `normalized/entity-detail.json` |
| Framework component injection rejected | `invalid/framework-component.json` |
| Arbitrary choice URL rejected | `invalid/arbitrary-choice-url.json` |
| Unsafe optimistic v1 result rejected | `invalid/optimistic-v1.json` |

## Ordinary Siren fallback

Every valid example remains navigable when its `modwire-ui-profile` embedded entity is ignored. An
ordinary client still sees root properties, embedded application entities, actions, and links. The
profile entity is control metadata and is not application content. Profile-aware clients must use
the same fallback whenever profile discovery or validation fails.

## Authorization fixture

`authorized-actions.json` represents a draft visible to an editor who may publish but may not
delete. The `publish` action is advertised and annotated; no delete action or delete metadata is
present. Client-side hiding is not part of the authorization proof—the unavailable affordance is
absent from the wire representation.
