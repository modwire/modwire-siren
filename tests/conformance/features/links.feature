Feature: Siren links

  Rule: A link describes a navigational transition

    Scenario: A link serializes its relationship and target
      Given a public link with rel "self" and an href
      When it is serialized
      Then the link has rel "self" and its href

    Scenario: A link without rel is rejected
      Given a public link without rel
      When it is created
      Then creation is rejected

  Rule: A link target is a URI

    Scenario: A link with a non-URI href is rejected
      Given a public link with a non-URI href
      When it is created
      Then creation is rejected
