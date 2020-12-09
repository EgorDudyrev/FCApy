from collections.abc import Iterable


class FormalConcept:
    def __init__(self, extent, intent):
        def unify_iterable_type(value, name="", value_type=str):
            assert isinstance(value, Iterable) and type(value) != str, \
                f"FormalConcept.__init__. Given {name} value should be an iterable but not a string"
            assert all([type(v) == value_type for v in value]),\
                f"FormalConcept.__init__. Given {name} values should be of type {value_type}"
            return tuple(value)

        self._extent = unify_iterable_type(extent, "extent")
        self._intent = unify_iterable_type(intent, "intent")

    @property
    def extent(self):
        return self._extent

    @property
    def intent(self):
        return self._intent

    def __eq__(self, other):
        return set(self.extent) == set(other.extent)

    def __hash__(self):
        return hash((self.extent, self.intent))
