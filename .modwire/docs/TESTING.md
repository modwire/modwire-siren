# Testing

- Test only published `modwire_siren` imports and observable Siren documents, never private modules or state. When
  available, inspect the Modwire MCP tool's advertised links and actions before using it as a reference consumer.
- Use Auntie order: adversarial boundary, invariant, interruption, cleanup, recovery, happy path. Run `make verify`
  before review.
