import modwire_siren


def test_root_api_is_intentionally_small_and_complete():
    assert modwire_siren.__all__ == [
        "ModwireSiren",
        "ModwireSirenFactory",
        "NinjaExtraSirenController",
        "OpenApiError",
        "SirenClient",
        "SirenClientError",
        "SirenEntityDecorator",
        "SirenEntityRequest",
        "SirenResponse",
        "SirenTransport",
        "__version__",
    ]


def test_feature_packages_are_not_barrels():
    import modwire_siren.contracts
    import modwire_siren.factories
    import modwire_siren.integrations
    import modwire_siren.openapi
    import modwire_siren.policies

    assert not hasattr(modwire_siren.contracts, "SirenEntity")
    assert not hasattr(modwire_siren.factories, "SirenEntityFactory")
    assert not hasattr(modwire_siren.integrations, "NinjaExtraSirenController")
    assert not hasattr(modwire_siren.openapi, "OpenApiCatalog")
    assert not hasattr(modwire_siren.policies, "SirenFieldTypeResolver")
