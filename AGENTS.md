# Delivery policy

After the user accepts completed work, update the linked GitHub issue and Project status. Merged pull requests must close their issue with `Fixes #<issue>`; then confirm the head branch is deleted remotely and prune its local tracking branch. Keep only protected long-lived branches unless instructed otherwise.

# Public-contract testing

The live `mcp__modwire__modwire` tool is a reference consumer: inspect advertised links and actions before executing them. Test this package only through its published `modwire_siren` imports and observable Siren documents; never cross the castle walls with private-module imports or assertions about internal state. Apply Auntie order: adversarial boundary, invariant, interruption, cleanup, and recovery cases come before the happy path.
