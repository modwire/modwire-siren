Feature: Siren sub-entities

  Rule: An embedded link identifies its relationship and target

    Scenario: An embedded link without an href is rejected
      Given a public embedded link without an href
      When it is created
      Then creation is rejected

  Rule: An embedded representation declares its relationship

    Scenario: An embedded representation without rel is rejected
      Given a public embedded representation without rel
      When it is created
      Then creation is rejected

  Rule: A sub-entity serializes its form

    Scenario: An embedded link serializes rel and href
      Given a public embedded link with rel "item" and an href
      When it is serialized
      Then the embedded link has rel "item" and its href

    Scenario: An embedded representation serializes rel
      Given a public embedded representation with rel "item"
      When it is serialized
      Then the embedded representation has rel "item"
