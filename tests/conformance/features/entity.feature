Feature: Siren entities

  Rule: A root entity exposes the official entity members

    Scenario: A root entity serializes its members
      Given a public root entity with official members
      When it is serialized
      Then it has its class, title, and properties
      And it has its sub-entities, actions, and links

  Rule: A root entity identifies its own URI with a self link

    Scenario: A root entity serializes a self link
      Given a public root entity with a self link
      When it is serialized
      Then it has a self link to its URI
