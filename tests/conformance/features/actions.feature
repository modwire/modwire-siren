Feature: Siren actions

  Rule: An action exposes its members

    Scenario: An action serializes its official members
      Given a public Siren action with official members
      When it is serialized
      Then the action has its official members

  Rule: An action method is constrained to the Siren HTTP methods

    Scenario: An action without a method serializes as GET
      Given a public Siren action without a method
      When it is serialized
      Then its method is "GET"

    Scenario: Actions serialize every permitted method
      Given public Siren actions for every permitted method
      When they are serialized
      Then their methods are the permitted Siren methods

    Scenario: An action with an unsupported method is rejected
      Given a public Siren action with an unsupported method
      When it is created
      Then creation is rejected

  Rule: Action names are unique within an entity

    Scenario: Duplicate action names are rejected
      Given a public Siren document with two actions named "update"
      When it is created
      Then creation is rejected

  Rule: An action with fields defaults to form encoding

    Scenario: An action with fields serializes its default type
      Given a public Siren action with fields and no type
      When it is serialized
      Then its type is "application/x-www-form-urlencoded"
