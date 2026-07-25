class SirenProjectionError(Exception):
    """Indicate a Siren projection failure for the supplied request context.

    `engine.project(context)` raises this stable public type when the context cannot select a
    concrete resource, capability, route, or path value for a Siren response.
    """
