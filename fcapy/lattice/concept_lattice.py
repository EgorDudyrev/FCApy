import json
from ..algorithms import concept_construction as cca, lattice_construction as lca
from .formal_concept import FormalConcept
import warnings


class ConceptLattice:
    def __init__(self, concepts=None, **kwargs):
        self._concepts = concepts

        subconcepts_dict = kwargs.get('subconcepts_dict')
        superconcepts_dict = kwargs.get('superconcepts_dict')
        if subconcepts_dict is not None and superconcepts_dict is None:
            superconcepts_dict = self.transpose_hierarchy(subconcepts_dict)
        if superconcepts_dict is not None and subconcepts_dict is None:
            subconcepts_dict = self.transpose_hierarchy(superconcepts_dict)
        self._subconcepts_dict = subconcepts_dict
        self._superconcepts_dict = superconcepts_dict

        top_concept_i = kwargs.get('top_concept_i')
        bottom_concept_i = kwargs.get('bottom_concept_i')
        if top_concept_i is None or bottom_concept_i is None:
            top_concept_i, bottom_concept_i = self.get_top_bottom_concepts_i(concepts)
        self._top_concept_i = top_concept_i
        self._bottom_concept_i = bottom_concept_i

    @property
    def concepts(self):
        return self._concepts

    @property
    def subconcepts_dict(self):
        return self._subconcepts_dict

    @property
    def superconcepts_dict(self):
        return self._superconcepts_dict

    @property
    def top_concept_i(self):
        return self._top_concept_i

    @property
    def top_concept(self):
        return self._concepts[self._top_concept_i] if self._top_concept_i is not None else None

    @property
    def bottom_concept_i(self):
        return self._bottom_concept_i

    @property
    def bottom_concept(self):
        return self._concepts[self._bottom_concept_i] if self._bottom_concept_i is not None else None

    @classmethod
    def from_context(cls, context):
        concepts = cls.sort_concepts(concepts=cca.close_by_one(context))
        subconcepts_dict = lca.complete_comparison(concepts)
        top_concept_i, bottom_concept_i = cls.get_top_bottom_concepts_i(concepts)

        ltc = ConceptLattice(
            concepts=concepts, subconcepts_dict=subconcepts_dict,
            top_concept_i=top_concept_i, bottom_concept_i=bottom_concept_i
        )
        return ltc

    @staticmethod
    def transpose_hierarchy(hierarchy_dict):
        new_dict = {}
        for k, vs in hierarchy_dict.items():
            if k not in new_dict:
                new_dict[k] = []
            for v in vs:
                new_dict[v] = new_dict.get(v, []) + [k]
        return new_dict

    @staticmethod
    def get_top_bottom_concepts_i(concepts):
        if concepts is None:
            return None, None

        top_concept_i, bottom_concept_i = 0, 0
        for i, c in enumerate(concepts):
            if c.support > concepts[top_concept_i].support:
                top_concept_i = i

            if c.support < concepts[bottom_concept_i].support:
                bottom_concept_i = i
        return top_concept_i, bottom_concept_i

    def to_json(self, path=None):
        assert len(self._concepts) >= 3,\
            'ConceptLattice.to_json error. The lattice should have at least 3 concepts to be saved in json'

        arcs = [{"S": s_i, "D": d_i} for s_i, d_is in self._subconcepts_dict.items() for d_i in d_is]

        lattice_metadata = {
            'Top': [self._top_concept_i], "Bottom": [self._bottom_concept_i],
            "NodesCount": len(self._concepts), "ArcsCount": len(arcs)
        }
        nodes_data = {"Nodes": [c.to_dict() for c in self._concepts]}
        arcs_data = {"Arcs": arcs}
        file_data = [lattice_metadata, nodes_data, arcs_data]
        json_data = json.dumps(file_data)

        if path is None:
            return json_data

        with open(path, "w") as f:
            f.write(json_data)

    @staticmethod
    def from_json(path=None, json_data=None):
        assert path is not None or json_data is not None,\
            "ConceptLattice.from_json error. Either path or json_data input parameters should be given"

        if path is not None:
            with open(path, 'r') as f:
                json_data = f.read()
        file_data = json.loads(json_data)
        lattice_metadata, nodes_data, arcs_data = file_data
        top_concept_i = lattice_metadata['Top'][0]
        bottom_concept_i = lattice_metadata['Bottom'][0]

        concepts = [FormalConcept.from_dict(c_dict) for c_dict in nodes_data['Nodes']]
        subconcepts_dict = {}
        for arc in arcs_data['Arcs']:
            subconcepts_dict[arc['S']] = subconcepts_dict.get(arc['S'], []) + [arc['D']]
        subconcepts_dict[bottom_concept_i] = []

        ltc = ConceptLattice(
            concepts=concepts, subconcepts_dict=subconcepts_dict,
            top_concept_i=top_concept_i, bottom_concept_i=bottom_concept_i
        )
        return ltc

    def __eq__(self, other):
        concepts_other = set(other.concepts)
        for c in self._concepts:
            if c not in concepts_other:
                return False
        return True

    def get_concept_new_extent_i(self, concept_i):
        sbc_is = self.subconcepts_dict[concept_i]
        sbc_extents_i = {g_i for sbc_i in sbc_is for g_i in self._concepts[sbc_i].extent_i}
        new_extent_i = set(self._concepts[concept_i].extent_i) - sbc_extents_i
        return new_extent_i

    def get_concept_new_extent(self, concept_i):
        sbc_is = self.subconcepts_dict[concept_i]
        sbc_extents = {g for sbc_i in sbc_is for g in self._concepts[sbc_i].extent}
        new_extent = set(self._concepts[concept_i].extent) - sbc_extents
        return new_extent

    def get_concept_new_intent_i(self, concept_i):
        spc_is = self.superconcepts_dict[concept_i]
        spc_intent_i = {m_i for spc_i in spc_is for m_i in self._concepts[spc_i].intent_i}
        new_intent_i = set(self._concepts[concept_i].intent_i) - spc_intent_i
        return new_intent_i

    def get_concept_new_intent(self, concept_i):
        spc_is = self.superconcepts_dict[concept_i]
        spc_intent = {m for spc_i in spc_is for m in self._concepts[spc_i].intent}
        new_intent = set(self._concepts[concept_i].intent) - spc_intent
        return new_intent

    def calc_concepts_measures(self, measure, context=None):
        from . import concept_measures as cms

        if measure in ('stability_bounds', 'LStab', 'UStab'):
            for c_i, c in enumerate(self._concepts):
                lb, ub = cms.stability_bounds(c_i, self)
                c.measures['LStab'] = lb
                c.measures['UStab'] = ub
        elif measure == 'stability':
            warnings.warn("Calculation of concept stability index takes exponential time. "
                          "One better use its approximate measure `stability_bounds`")
            assert context is not None, 'ConceptLattice.calc_concepts_measures failed. ' \
                                        'Please specify `context` parameter to calculate the stability'
            for c_i, c in enumerate(self._concepts):
                s = cms.stability(c_i, self, context)
                c.measures['Stab'] = s
        else:
            possible_measures = ['stability_bounds', 'LStab', 'UStab', 'stability']
            raise ValueError(f'ConceptLattice.calc_concepts_measures. The given measure {measure} is unknown. ' +
                             f'Possible measure values are: {",".join(possible_measures)}')

    @staticmethod
    def sort_concepts(concepts):
        return sorted(concepts, key=lambda c: (-len(c.extent_i), ','.join([str(g) for g in c.extent_i])))
