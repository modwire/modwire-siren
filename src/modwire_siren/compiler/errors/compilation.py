class SirenCompilationError(Exception):
    """Indicate an invalid or unsupported OpenAPI-to-Siren contract.

    `siren(openapi)` raises this stable public type when the OpenAPI document is invalid or its
    operations cannot be represented by official Siren. Required controls, unsupported parameter
    locations and HTTP methods, non-JSON bodies, and unmappable field schemas fail at startup.
    """
