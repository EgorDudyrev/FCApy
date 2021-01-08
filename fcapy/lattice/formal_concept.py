from collections.abc import Iterable
import json


class FormalConcept:
    JSON_BOTTOM_PLACEHOLDER = {"Inds": (-2,), "Names": ("BOTTOM_PLACEHOLDER",)}

    def __init__(self, extent_i, extent, intent_i, intent, measures=None, context_hash=None):
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

        assert len(self._extent_i) == len(self._extent),\
            "FormalConcept.__init__ error. extent and extent_i are of different sizes"
        assert len(self._intent_i) == len(self._intent), \
            "FormalConcept.__init__ error. intent and intent_i are of different sizes"

        self._support = len(self._extent_i)
        self.measures = measures if measures is not None else {}
        self._context_hash = context_hash

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

    @property
    def support(self):
        return self._support

    @property
    def context_hash(self):
        return self._context_hash

    def __eq__(self, other):
        if self._context_hash != other.context_hash:
            raise NotImplementedError('FormalConcept error. Cannot compare concepts from different contexts')

        if self._support != other.support:
            return False

        return self <= other

    def __hash__(self):
        return hash((tuple(sorted(self._extent_i)), tuple(sorted(self._intent_i))))

    def __le__(self, other):
        if self._context_hash != other.context_hash:
            raise NotImplementedError('FormalConcept error. Cannot compare concepts from different contexts')

        if self._support > other.support:
            return False

        extent_other = set(other.extent_i)
        for g_i in self._extent_i:
            if g_i not in extent_other:
                return False
        return True

    def __lt__(self, other):
        if self._context_hash != other.context_hash:
            raise NotImplementedError('FormalConcept error. Cannot compare concepts from different contexts')

        if self._support >= other.support:
            return False

        return self <= other

    def to_dict(self):
        concept_info = dict()
        concept_info['Ext'] = {"Inds": self._extent_i, "Names": self._extent, "Count": len(self._extent_i)}
        concept_info['Int'] = {"Inds": self._intent_i, "Names": self._intent, "Count": len(self._intent_i)}
        concept_info['Supp'] = self.support
        for k, v in self.measures.items():
            concept_info[k] = v
        concept_info['Context_Hash'] = self._context_hash
        return concept_info

    @classmethod
    def from_dict(cls, data):
        if data["Int"] == "BOTTOM":
            data["Int"] = cls.JSON_BOTTOM_PLACEHOLDER
            #data["Int"] = {'Inds': [], "Names": []}

        c = FormalConcept(
            data['Ext']['Inds'], data['Ext'].get('Names', []),
            data['Int']['Inds'], data['Int'].get('Names', []),
            context_hash=data.get('Context_Hash')
        )

        for k, v in data.items():
            if k in ['Int', 'Ext']:
                continue
            c.measures[k] = v
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
