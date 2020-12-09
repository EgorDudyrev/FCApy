from collections.abc import Iterable
import json


class FormalConcept:
    def __init__(self, extent_i, extent, intent_i, intent):
        def unify_iterable_type(value, name="", value_type=str):
            assert isinstance(value, Iterable) and type(value) != str, \
                f"FormalConcept.__init__. Given {name} value should be an iterable but not a string"
            assert all([type(v) == value_type for v in value]),\
                f"FormalConcept.__init__. Given {name} values should be of type {value_type}"
            return tuple(value)

        self._extent_i = unify_iterable_type(extent_i, "extent_i", value_type=int)
        self._extent = unify_iterable_type(extent, "extent", value_type=str)
        self._intent_i = unify_iterable_type(intent_i, "intent", value_type=int)
        self._intent = unify_iterable_type(intent, "intent", value_type=str)

    @property
    def extent_i(self):
        return self._extent_i

    @property
    def extent(self):
        return self._extent

    @property
    def intent_i(self):
        return self._intent_i

    @property
    def intent(self):
        return self._intent

    def __eq__(self, other):
        return set(self.extent) == set(other.extent)

    def __hash__(self):
        return hash(self._extent_i)

    def to_dict(self):
        concept_info = dict()
        concept_info['Ext'] = {"Inds": self._extent_i, "Names": self._extent, "Count": len(self._extent_i)}
        concept_info['Int'] = {"Inds": self._intent_i, "Names": self._intent, "Count": len(self._intent_i)}
        concept_info['Supp'] = len(self._extent_i)
        return concept_info

    @staticmethod
    def from_dict(data):
        c = FormalConcept(data['Ext']['Inds'], data['Ext']['Names'],
                          data['Int']['Inds'], data['Int']['Names'])
        return c

    def to_json(self, path=None):
        concept_info = self.to_dict()

        file_data = json.dumps(concept_info)
        if path is None:
            return file_data

        with open(path, 'w') as f:
            f.write(file_data)

    @classmethod
    def from_json(cls, path=None, json_data=None):
        assert path is not None or json_data is not None,\
            "FormalConcept.from_json error. Either path or data attribute should be given"

        if path is not None:
            with open(path, 'r') as f:
                json_data = f.read()
        data = json.loads(json_data)
        c = cls.from_dict(data)
        return c
