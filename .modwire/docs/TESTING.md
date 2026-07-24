# Testing

Test through published `modwire_siren` imports and observable Siren documents only—never private modules or internal state. The Modwire MCP tool, when available, is a reference consumer: inspect its advertised links and actions before using it.

Write cases in Auntie order: adversarial boundary, invariant, interruption, cleanup, recovery, then happy path. Run `make verify` before review.
