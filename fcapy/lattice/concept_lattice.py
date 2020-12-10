from ..algorithms import concept_construction as cca, lattice_construction as lca


class ConceptLattice:
    def __init__(self, concepts=None, subconcepts_dict=None, superconcepts_dict=None):
        self._concepts = concepts

        if subconcepts_dict is not None and superconcepts_dict is None:
            superconcepts_dict = self.transpose_hierarchy(subconcepts_dict)
        if superconcepts_dict is not None and subconcepts_dict is None:
            subconcepts_dict = self.transpose_hierarchy(superconcepts_dict)

        self._subconcepts_dict = subconcepts_dict
        self._superconcepts_dict = superconcepts_dict

    @property
    def concepts(self):
        return self._concepts

    @property
    def subconcepts_dict(self):
        return self._subconcepts_dict

    @property
    def superconcepts_dict(self):
        return self._superconcepts_dict

    @staticmethod
    def from_context(context):
        concepts = cca.close_by_one(context)
        subconcepts_dict = lca.complete_comparison(concepts)
        return ConceptLattice(concepts=concepts, subconcepts_dict=subconcepts_dict)

    @staticmethod
    def transpose_hierarchy(hierarchy_dict):
        new_dict = {}
        for k, vs in hierarchy_dict.items():
            if k not in new_dict:
                new_dict[k] = []
            for v in vs:
                new_dict[v] = new_dict.get(v, []) + [k]
        return new_dict
