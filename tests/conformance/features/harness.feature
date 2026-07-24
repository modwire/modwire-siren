Feature: Conformance harness

  Scenario: A public Siren document is observable
    Given a public Siren document
    When it is serialized
    Then the serialized value is an object
