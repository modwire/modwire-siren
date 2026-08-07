from sirenity import SirenAdapterPolicy


class RootCapabilityPolicy:
    def select(self, operation_id, status, request, result):
        return SirenAdapterPolicy(
            representation="root",
            capabilities=frozenset({"reindex"}),
        )
