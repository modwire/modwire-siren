Feature: Siren relations

  Rule: A relation is an official token or URI

    Scenario: A link with an invalid relation is rejected
      Given a public link with an invalid relation
      When it is created
      Then creation is rejected

    Scenario: A link serializes a relation URI
      Given a public link with a relation URI
      When it is serialized
      Then the link has its relation URI

  Rule: Every relationship owner shares the official relation contract

    Scenario: An embedded representation serializes a relation URI
      Given a public embedded representation with a relation URI
      When it is serialized
      Then the embedded representation has its relation URI
