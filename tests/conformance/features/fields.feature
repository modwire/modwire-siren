Feature: Siren fields

  Rule: A field type is one of the official Siren input types

    Scenario: Fields serialize every permitted type
      Given public Siren fields for every permitted type
      When they are serialized
      Then their types are the permitted Siren field types

    Scenario: A field without a type serializes as text
      Given a public Siren field without a type
      When it is serialized
      Then its type is "text"

    Scenario: A field with an unsupported type is rejected
      Given a public Siren field with an unsupported type
      When it is created
      Then creation is rejected

  Rule: Selectable values preserve their client state

    Scenario: A field serializes selectable value objects
      Given a public radio field with selectable values
      When it is serialized
      Then the field has its selectable values

  Rule: Field names are unique within an action

    Scenario: Duplicate field names are rejected
      Given a public Siren action with two fields named "title"
      When it is created
      Then creation is rejected
