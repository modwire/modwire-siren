from modwire_siren import SirenAdapterPolicy


class DjangoSirenPolicy:
    def __call__(self, operation_id, status, request, result):
        return SirenAdapterPolicy(capabilities=frozenset({operation_id}))


django_siren_policy = DjangoSirenPolicy()
