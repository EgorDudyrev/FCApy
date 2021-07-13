"""
This module provides a ConceptLattice class. It may be considered as the main module (and class) of lattice subpackage

"""
import json
from fcapy.algorithms import concept_construction as cca, lattice_construction as lca
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.lattice.pattern_concept import PatternConcept
from fcapy.mvcontext.mvcontext import MVContext
from fcapy.context.formal_context import FormalContext
from fcapy.poset.lattice import Lattice
from fcapy.utils import utils
import warnings
from itertools import product
from copy import deepcopy
from frozendict import frozendict

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['numpy']:
    import numpy as np


class ConceptLattice(Lattice):
    r"""A class used to represent Concept Lattice object from FCA theory

    Methods
    -------
    from_context(context, algo, ...):
       Construct a ConceptLattice from the given ``context`` by specified ``algo`` ('CbO','Sofia', 'RandomForest')
    calc_concepts_measures(measure, ...):
       Calculate interestingness ``measure`` of concepts in the ConceptLattice (like 'stability' or 'stability_bounds')
    trace_context(context, ...):
       Get the set of concepts from the ConceptLattice which describe objects from the given ``context``
    add_concept(new_concept):
       Add ``new_concept`` to the ConceptLattice
    remove_concept(concept_i):
       Remove a concept with ``concept_i`` index from the ConceptLattice

    Notes
    -----
    A ConceptLattice `L` = `{(A,B) | A \\subseteq G, B \\subseteq M, A'=B, B'=A}`
    is a set of Formal Concepts `(A,B)` contained in a Formal Context `K` = `(G, M, I)`

    A Formal Concept `(A,B)` denotes the pair of subset of objects `A` and subset of attributes `B`,
    s.t. objects `A` are all the objects described by attributes `B`
    and attributes `B` are all the attributes which describe objects `A`.

    The notion of Formal Context is described in the class `fcapy.context.formal_context.FormalContext`

    A ConceptLattice idea may be applied to Many Valued Context too
    (described in the class `fcapy.mvcontext.mvcontext.MVContext`)
    resolving a set of Pattern Concepts `(A, d)`
    where A is a subset of objects, d is a description from the ManyValuedContext
    s.t. objects `A` are all the objects described by desciption `d`
    and description `d` is the biggest (most precise) description of objects `A`

    """
    CLASS_NAME = 'ConceptLattice'

    def __init__(self, concepts, **kwargs):
        """Construct a ConceptLattice based on a set of ``concepts`` and ``**kwargs`` values

        Parameters
        ----------
        concepts: `list`[`FormalConcept` or `PatternConcept`]
        kwargs:
            subconcepts_dict: `dict`{`int`, `list`[`int`]}
                A dictionary with subconcept (order) relation on the ``concepts``
            superconcepts_dict: `dict`{`int`, `list`[`int`]}
                A dictionary with superconcept (inverse order) relation on the ``concepts``
        """

        super(ConceptLattice, self).__init__(concepts, self.concepts_leq_func, use_cache=True)

        subconcepts_dict = kwargs.get('subconcepts_dict')
        superconcepts_dict = kwargs.get('superconcepts_dict')
        if subconcepts_dict is not None or superconcepts_dict is not None:
            if subconcepts_dict is not None:
                subconcepts_dict = {c_i: set(subs_i) for c_i, subs_i in subconcepts_dict.items()}
            if superconcepts_dict is not None:
                superconcepts_dict = {c_i: set(sups_i) for c_i, sups_i in superconcepts_dict.items()}

            if superconcepts_dict is None:
                superconcepts_dict = self._transpose_hierarchy(subconcepts_dict)
            if subconcepts_dict is None:
                subconcepts_dict = self._transpose_hierarchy(superconcepts_dict)

            self._cache_direct_subelements = subconcepts_dict
            self._cache_direct_superelements = superconcepts_dict
            self._cache_subelements = self._closed_relation_cache_by_direct_cache(subconcepts_dict)
            self._cache_superelements = self._closed_relation_cache_by_direct_cache(superconcepts_dict)

        self._generators_dict = {}

    @property
    def superconcepts_dict(self):
        """A dictionary {`concept_index`: list of indexes of closest concepts bigger than concept `concept_index`}"""
        return self.direct_super_elements_dict

    @property
    def all_superconcepts_dict(self):
        """A dictionary {`concept_index`: list of indexes of all concepts bigger than concept `concept_index`}"""
        return self.super_elements_dict

    @property
    def subconcepts_dict(self):
        """A dictionary {`concept_index`: list of indexes of closest concepts smaller than concept `concept_index`}"""
        return self.direct_sub_elements_dict

    @property
    def all_subconcepts_dict(self):
        """A dictionary {`concept_index`: list of indexes of all concepts smaller than concept `concept_index`}"""
        return self.sub_elements_dict

    @property
    def concepts(self):
        """A list of concepts of the lattice"""
        return self._elements

    @property
    def top_concept_i(self):
        """An index of the top (the biggest) concept"""
        return self.top_element

    @property
    def top_concept(self):
        """The top (biggest) concept"""
        return self.concepts[self.top_concept_i]

    @property
    def bottom_concept_i(self):
        """An index of the bottom (the smallest) concept"""
        return self.bottom_element

    @property
    def bottom_concept(self):
        """The bottom (the smallest) concept"""
        return self.concepts[self.bottom_concept_i]

    @staticmethod
    def get_top_bottom_concepts_i(concepts, is_concepts_sorted=False):
        """Return the indexes of top and bottom concept from the list of ``concepts``

        Parameters
        ----------
        concepts: `list` of `FormalConcept` or `PatternConcept`
            A list of concepts to look for top (biggest) and bottom (smallest) concepts
        is_concepts_sorted: `bool`
            A flag whether the ``concepts`` are topologically sorted or they should be sorted inside the function
        Returns
        -------
        top_concept_i: `int`
            An index of the top (biggest) concept from the list of ``concepts``
        bottom_concept_i: `int`
            An index of the bottom (smallest) concept from the list of ``concepts``

        """
        if concepts is None:
            return None, None

        if is_concepts_sorted:
            top_concept_i, bottom_concept_i = 0, len(concepts) - 1
            multiple_top = concepts[1].support == concepts[top_concept_i].support
            multiple_bottom = concepts[-2].support == concepts[bottom_concept_i].support
        else:
            top_concept_i, bottom_concept_i = 0, 0
            multiple_top, multiple_bottom = False, False
            for i, c in enumerate(concepts[1:]):
                i += 1
                if c.support == concepts[top_concept_i].support:
                    multiple_top = True
                if c.support == concepts[bottom_concept_i].support:
                    multiple_bottom = True

                if c.support > concepts[top_concept_i].support:
                    top_concept_i = i
                    multiple_top = False

                if c.support < concepts[bottom_concept_i].support:
                    bottom_concept_i = i
                    multiple_bottom = False

        top_concept_i = None if multiple_top else top_concept_i
        bottom_concept_i = None if multiple_bottom else bottom_concept_i

        return top_concept_i, bottom_concept_i

    @classmethod
    def from_context(cls, context: FormalContext or MVContext, algo=None, **kwargs):
        """Return a `ConceptLattice` constructed on the ``context`` by algorithm ``algo``

        Parameters
        ----------
        context: 'FormalContext` or 'MVContext`
        algo: `str` in {'CbO', 'Sofia', 'RandomForest'}
        kwargs:
            Parameters used in CbO, Sofia and RandomForest algorithms from `fcapy.algorithms.concept_construction` module

        Returns
        -------
        ltc: `ConceptLattice`
            A concept lattice constructed on the ``context`` by algorithm ``algo``

        """
        if algo is None:
            algo = 'Sofia' if type(context) == MVContext else 'CbO'

        if algo in {'CbO', 'RandomForest'}:
            algo_func = {'CbO': cca.close_by_one, 'RandomForest': cca.random_forest_concepts}[algo]
            kwargs_used = utils.get_kwargs_used(kwargs, algo_func)
            concepts = algo_func(context, **kwargs_used)
            concepts = cls.sort_concepts(concepts)
            subconcepts_dict = lca.construct_lattice_by_spanning_tree(concepts, is_concepts_sorted=True)

            ltc = ConceptLattice(
                concepts=concepts, subconcepts_dict=subconcepts_dict
            )

        elif algo == 'Sofia':
            if type(context) == MVContext:
                kwargs_used = utils.get_kwargs_used(kwargs, cca.sofia_general)
                ltc = cca.sofia_general(context, **kwargs_used)
            else:
                kwargs_used = utils.get_kwargs_used(kwargs, cca.sofia_binary)
                ltc = cca.sofia_binary(context, **kwargs_used)

            # sort concepts in the same order as they have been created by CbO algorithm
            concepts_sorted = cls.sort_concepts(ltc.concepts)
            map_concept_i_sort = {c: c_sort_i for c_sort_i, c in enumerate(concepts_sorted)}
            map_i_isort = [map_concept_i_sort[ltc.concepts[c_i]] for c_i in range(len(ltc.concepts))]
            map_concept_i = {c: c_i for c_i, c in enumerate(ltc.concepts)}
            map_isort_i = [map_concept_i[concepts_sorted[c_i_sort]] for c_i_sort in range(len(ltc.concepts))]

            ltc._elements = concepts_sorted
            ltc._elements_to_index_map = {el: idx for idx, el in enumerate(concepts_sorted)}
            ltc._cache_leq = {}
            for cache_name in ['direct_subelements', 'subelements', 'direct_superelements', 'superelements']:
                cache_name = f"_cache_{cache_name}"
                ltc.__dict__[cache_name] = {
                    map_i_isort[c_i] : {map_i_isort[c1_i] for c1_i in ltc.__dict__[cache_name][c_i]}
                    for c_i in map_isort_i
                }

            ltc._generators_dict = {map_i_isort[c_i]: {map_i_isort[supc_i]: gen for supc_i, gen in gens_dict.items()}
                                    for c_i, gens_dict in ltc._generators_dict.items()}
            if ltc._cache_top_element is not None:
                ltc._cache_top_element = map_i_isort[ltc._cache_top_element]
            if ltc._cache_bottom_element is not None:
                ltc._cache_bottom_element = map_i_isort[ltc._cache_bottom_element]

        else:
            raise ValueError(f'ConceptLattice.from_context error. Algorithm {algo} is not supported.\n'
                             f'Possible values are: "CbO" (stands for CloseByOne), "Sofia", "RandomForest')
        return ltc

    @staticmethod
    def sort_concepts(concepts):
        """Return the topologically sorted set of concepts

        (ordered by descending of support, lexicographical order of extent indexes)

        """
        if concepts is None:
            return None
        return sorted(concepts, key=lambda c: (-len(c.extent_i), ','.join([str(g) for g in c.extent_i])))

    @staticmethod
    def from_json(path: str =None, json_data: str =None):
        """Read ConceptLattice from .json file .json formatted string data

        Parameters
        ----------
        path: `str`
            A path to .json file
        json_data: `str`
            A json encoded data

        Returns
        -------
        ltc: `ConceptLattice`

        """
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
            subconcepts_dict[arc['S']] = subconcepts_dict.get(arc['S'], set()) | {arc['D']}
        subconcepts_dict[bottom_concept_i] = set()

        ltc = ConceptLattice(
            concepts=concepts, subconcepts_dict=subconcepts_dict,
            top_concept_i=top_concept_i, bottom_concept_i=bottom_concept_i
        )
        return ltc

    def add_concept(self, new_concept: FormalConcept or PatternConcept):
        """Add concept ``new_concept`` into the lattice"""
        self.add(new_concept)

    def remove_concept(self, concept_i):
        """Remove concept ``concept_i`` into the lattice"""
        del self[concept_i]

    def calc_concepts_measures(self, measure: str, context: FormalContext or MVContext = None):
        """Calculate the values of ``measure`` for each concept in a lattice

        The calculated measure values are stored in ``measures`` property of each ``concept`` from ``ConceptLattice.concepts``

        Parameters
        ----------
        measure: `str` in ('LStab', 'UStab', 'stability_bounds', 'stability')
            The name of the measure to compute
        context: `FormalContext` or `MVContext`
            The context is used when calculating 'stability' measure
        Returns
        -------
        None

        """
        from fcapy.lattice import concept_measures as cms

        if measure in ('stability_bounds', 'LStab', 'UStab'):
            for c_i, c in enumerate(self.concepts):
                lb, ub = cms.stability_bounds(c_i, self)
                c.measures['LStab'] = lb
                c.measures['UStab'] = ub
        elif measure == 'stability':
            warnings.warn("Calculation of concept stability index takes exponential time. "
                          "One better use its approximate measure `stability_bounds`")
            assert context is not None, 'ConceptLattice.calc_concepts_measures failed. ' \
                                        'Please specify `context` parameter to calculate the stability'
            for c_i, c in enumerate(self.concepts):
                s = cms.stability(c_i, self, context)
                c.measures['Stab'] = s
        elif measure == 'target_entropy':
            for c_i, c in enumerate(self.concepts):
                c.measures[measure] = cms.target_entropy(c_i, self, context)
        elif measure == 'mean_information_gain':
            for c_i, c in enumerate(self.concepts):
                c.measures[measure] = cms.mean_information_gain(c_i, self)
        elif isinstance(measure, tuple) and len(measure) == 2:
            name, func = measure
            assert isinstance(name, str), 'Measure name should be a string'
            for c_i, c in enumerate(self.concepts):
                c.measures[name] = func(c_i, self, context)
        else:
            possible_measures = ['stability_bounds', 'LStab', 'UStab', 'stability',
                                 'target_entropy', 'mean_information_gain']
            raise ValueError(f'ConceptLattice.calc_concepts_measures. The given measure {measure} is unknown. ' +
                             f'Possible measure values are either strings: {",".join(possible_measures)}, ' 
                             f'or a pair (measure_name: str, measure_func: c_i, lattice, context -> float)')

    @classmethod
    def get_all_superconcepts_dict(cls, concepts, superconcepts_dict):
        """Return the transitively closed superconcept relation of ``concept`` from ``superconcepts_dict``

        The transitively closed superconcept relation of ``concept`` from ``superconcepts`` means the dict of type:
        {`child_concept_index`: `list` of indexes of all concepts bigger than the child}

        Parameters
        ----------
        concepts: `list` of `FormalConcept` or `PatternConcept`
            A list of concepts to compute relation on
        superconcepts_dict: `dict` of type {`int`: `list` of `int`}
            The superconcept relation of the `concepts (i.e. {`child_concept_index`: `list` of `parent_concept_index`})

        Returns
        -------
        all_superconcepts: `dict` of type {`int`: `list` of `int`}
            The transitively closed superconcept relation of ``concept`` from ``superconcepts_dict``

        """
        all_superconcepts = {}
        concepts_to_visit = sorted(range(len(concepts)), key=lambda c_i: -concepts[c_i].support)
        for c_i in concepts_to_visit:
            all_superconcepts[c_i] = superconcepts_dict[c_i].copy()
            for supc_i in superconcepts_dict[c_i]:
                all_superconcepts[c_i] |= all_superconcepts[supc_i]
        return all_superconcepts

    @classmethod
    def get_all_subconcepts_dict(cls, concepts, subconcepts_dict):
        """Return the transitively closed superconcept relation of ``concept`` from ``subconcepts_dict``

        The transitively closed subconcept relation of ``concept`` from ``subconcepts_dict`` means the dict of type:
        {`parent_concept_index`: `list` of indexes of all concepts smaller than the parent}

        Parameters
        ----------
        concepts: `list` of `FormalConcept` or `PatternConcept`
            A list of concepts to compute relation on
        subconcepts_dict: `dict` of type {`int`: `list` of `int`}
            The subconcept relation of the ``concepts`` (i.e. {`parent_concept_index`: `list` of `children_concept_index`})

        Returns
        -------
        all_subconcepts: `dict` of type {`int`: `list` of `int`}
            The transitively closed subconcept relation of ``concept`` from ``subconcepts_dict``

        """
        all_subconcepts = {}
        concepts_to_visit = sorted(list(range(len(concepts))), key=lambda c_i: concepts[c_i].support)
        for c_i in concepts_to_visit:
            all_subconcepts[c_i] = subconcepts_dict[c_i].copy()
            for subc_i in subconcepts_dict[c_i]:
                all_subconcepts[c_i] |= all_subconcepts[subc_i]
        return all_subconcepts

    def trace_context(self, context: FormalContext or MVContext,
                      use_object_indices=False, use_generators=False, use_tqdm=False, return_generators_extents=False):
        """Return the dictionaries which map an object from ``context`` to a set of bottom/all the concepts which cover it

        Parameters
        ----------
        context: `FormalContext` or `PatternContext`
            A Formal (or Pattern) Context to trace
        use_object_indices: `bool`
            A flag whether to return a dict with keys as object indices (if True) or object names (if False)
        use_generators: `bool`
            A flag whether to describe object of `context by closed concept intents (if False) or their generators (o/w)
        use_tqdm: `bool`
            A flag whether to visualize the progress of the algorithm with tqdm bar

        Returns
        -------
        object_bottom_concepts: `dict` of type {`int`: `list` of `int`}
            Dictionary which maps each object from the ``context`` to a subset of the smallest concepts
            from the ConceptLattice which describe this object
        object_traced_concepts: `dict` of type {`int`: `list` of `int`}
            Dictionary which maps each object from the ``context`` to a subset of all the concepts
            from the ConceptLattice which describe this object

        """
        concept_extents = {}
        if return_generators_extents:
            generators_extents = []

        def stored_extension(concept_i, use_generators, superconcept_i=None):
            if not use_generators:
                if concept_i not in concept_extents:
                    concept_extents[concept_i] = set(context.extension_i(self.concepts[concept_i].intent_i))
                extent = concept_extents[concept_i]
            else:
                if concept_i not in concept_extents:
                    concept_extents[concept_i] = {}

                if concept_i == self.top_concept_i:
                    gen = self._generators_dict[concept_i]
                    concept_extents[concept_i] = set(context.extension_i(gen))
                    extent = concept_extents[concept_i]

                    if return_generators_extents:
                        gen_stat = {'superconcept_i': None, 'concept_i': concept_i, 'ext_': tuple(extent),
                                    'gen': frozendict(gen)}
                        generators_extents.append(gen_stat)
                elif superconcept_i is None:
                    # it is assumed that the function with superconcept_i=None will be called after
                    # all generators (concept_i, superconcept_i) are computed.
                    # Thus concept_extents[concept_i][None] = context.extent(concept.intent_i)
                    extent = concept_extents[concept_i][None]
                else:
                    if superconcept_i not in concept_extents[concept_i]:
                        condgens = self._generators_dict[concept_i][superconcept_i]
                        ext_ = set()
                        ext_sup = stored_extension(concept_i=superconcept_i, use_generators=use_generators)#[superconcept_i] self._concepts[superconcept_i].extent_i
                        if False: #LIB_INSTALLED['numpy']:
                            ext_sup = np.array(tuple(ext_sup))
                        else:
                            ext_sup = frozenset(ext_sup)

                        for gen in condgens:
                            new_ext = context.extension_i(gen, ext_sup)
                            ext_ |= set(new_ext)
                            if False: #LIB_INSTALLED['numpy']:
                                 ext_sup = ext_sup[~np.isin(ext_sup, np.array(new_ext, dtype=ext_sup.dtype))]
                            else:
                                ext_sup = ext_sup - set(new_ext)

                            if return_generators_extents:
                                gen_stat = {'superconcept_i': superconcept_i, 'concept_i': concept_i,
                                            'ext_': tuple(new_ext), 'gen': frozendict(gen)}
                                generators_extents.append(gen_stat)

                            if len(ext_sup) == 0:
                                break

                        concept_extents[concept_i][superconcept_i] = ext_
                        concept_extents[concept_i][None] = concept_extents[concept_i].get(None, set()) | ext_
                    extent = concept_extents[concept_i][superconcept_i]
            return extent

        concepts_to_visit = [self.top_concept_i]
        object_bottom_concepts = {idx: set() for idx in range(context.n_objects)}
        object_traced_concepts = {idx: set() for idx in range(context.n_objects)}
        visited_concepts = set()

        for i in utils.safe_tqdm(range(len(self)), disable=not use_tqdm, desc='Iterate through concepts'):
            if len(concepts_to_visit) == 0:
                break

            c_i = concepts_to_visit.pop(0)
            extent = stored_extension(c_i, use_generators)
            visited_concepts.add(c_i)

            if use_generators:
                subconcepts_i = [k for k, gens_dict in self._generators_dict.items() if c_i in gens_dict]
            else:
                subconcepts_i = self.subconcepts_dict[c_i]

            subconcept_extents = set()
            for subconcept_i in subconcepts_i:
                subconcept_extents |= stored_extension(subconcept_i, use_generators, c_i)
            stopped_objects = extent - subconcept_extents

            for g_i in stopped_objects:
                object_bottom_concepts[g_i].add(c_i)
            for g_i in extent:
                object_traced_concepts[g_i].add(c_i)

            new_concepts = [subconcept_i for subconcept_i in subconcepts_i
                            if len(stored_extension(subconcept_i, use_generators, c_i)) > 0
                            and subconcept_i not in visited_concepts and subconcept_i not in concepts_to_visit]
            new_concepts = sorted(new_concepts, key=lambda c_i: -self.concepts[c_i].support)
            concepts_to_visit += new_concepts

        if not use_object_indices:
            object_bottom_concepts = {context.object_names[g_i]: concepts_i
                                      for g_i, concepts_i in object_bottom_concepts.items()}
            object_traced_concepts = {context.object_names[g_i]: concepts_i
                                      for g_i, concepts_i in object_traced_concepts.items()}

        if return_generators_extents:
            generators_extents = list(set([frozendict(ge) for ge in generators_extents]))
            output = object_bottom_concepts, object_traced_concepts, generators_extents
        else:
            output = object_bottom_concepts, object_traced_concepts
        return output

    def get_conditional_generators_dict(self, context: MVContext, use_tqdm=False, algo='exact'):
        """Return the conditional generators of concepts from the Concept Lattice

        WARNING: No comments for now. The notion of conditional generators is under construction
        """
        condgen_dict = dict()
        condgen_dict[self.top_concept_i] = {}

        assert algo in {'approximate', 'exact'}, f"Given algorithm '{algo}' is not supported. " \
                                                 f"Possible values are: 'approximate', 'exact'"


        concepts_sorted = self.sort_concepts(self.concepts)
        map_concept_i = {c: c_i for c_i, c in enumerate(self.concepts)}
        map_isort_i = [map_concept_i[concepts_sorted[c_i_sort]] for c_i_sort in range(len(self.concepts))]
        concepts_to_visit = map_isort_i

        if not LIB_INSTALLED['numpy'] or type(context) is not MVContext:
            supc_exts_i = [frozenset(context.extension_i(c.intent_i)) for c in self.concepts]
        else:
            supc_exts_i = [np.array(context.extension_i(c.intent_i)) for c in self.concepts]

        for c_i in utils.safe_tqdm(concepts_to_visit[1:], disable=not use_tqdm, desc='Calc conditional generators'):
            intent_i = self.concepts[c_i].intent_i

            superconcepts_i = self.superconcepts_dict[c_i]

            condgens = {}
            if algo == 'exact':
                if type(context) is MVContext:
                    for supc_i in utils.safe_tqdm(superconcepts_i, desc='Iterate superconcepts', leave=False, disable=not use_tqdm):
                        supc_ext_i = supc_exts_i[supc_i]
                        supc_int_i = self.concepts[supc_i].intent_i
                        ps_to_iterate = [ps_i for ps_i, descr in intent_i.items()
                                         if type(descr) != type(supc_int_i[ps_i]) or descr != supc_int_i[ps_i]]

                        condgens[supc_i] = context.get_minimal_generators(
                            intent_i, base_objects=supc_ext_i,
                            use_indexes=True, ps_to_iterate=ps_to_iterate)

                else:
                    for supc_i in superconcepts_i:
                        supc_ext_i = supc_exts_i[supc_i]
                        condgens[supc_i] = context.get_minimal_generators(
                            intent_i, base_objects=supc_ext_i, use_indexes=True)
            else:
                for supc_i in superconcepts_i:
                    condgens[supc_i] = context.generators_by_intent_difference(
                        intent_i, self.concepts[supc_i].intent_i)
            condgen_dict[c_i] = condgens

        return condgen_dict

    def get_concept_new_extent_i(self, concept_i):
        """Return the subset of objects indexes which are contained in ``concept_i`` but not its children concepts"""
        sbc_is = self.subconcepts_dict[concept_i]
        sbc_extents_i = {g_i for sbc_i in sbc_is for g_i in self.concepts[sbc_i].extent_i}
        new_extent_i = set(self.concepts[concept_i].extent_i) - sbc_extents_i
        return new_extent_i

    def get_concept_new_extent(self, concept_i):
        """Return the subset of objects which are contained in ``concept_i`` but not its children concepts"""
        sbc_is = self.subconcepts_dict[concept_i]
        sbc_extents = {g for sbc_i in sbc_is for g in self.concepts[sbc_i].extent}
        new_extent = set(self.concepts[concept_i].extent) - sbc_extents
        return new_extent

    def get_concept_new_intent_i(self, concept_i):
        """Return the subset of attributes indexes which are contained in ``concept_i`` but not its parent concepts"""
        spc_is = self.superconcepts_dict[concept_i]
        spc_intent_i = {m_i for spc_i in spc_is for m_i in self.concepts[spc_i].intent_i}
        new_intent_i = set(self.concepts[concept_i].intent_i) - spc_intent_i
        return new_intent_i

    def get_concept_new_intent(self, concept_i):
        """Return the subset of objects which are contained in ``concept_i`` but not its parent concepts"""
        spc_is = self.superconcepts_dict[concept_i]
        spc_intent = {m for spc_i in spc_is for m in self.concepts[spc_i].intent}
        new_intent = set(self.concepts[concept_i].intent) - spc_intent
        return new_intent

    def get_chains(self):
        """Return a list of chains of concept indexes from the ConceptLattice

        A chain of concept indexes is the list of concept indexes
        s.t. the first element of the chain is the index of top (biggest) concept
        each next element is a child of the previous one

        A list of chains covers covers all the concepts in the lattice

        Returns
        -------
        chain: `list` of `list` of `int`
            A list of chains of concept indexes from the ConceptLattice

        """
        return self._get_chains(self.concepts, self.superconcepts_dict)

    @classmethod
    def _get_chains(cls, concepts, superconcepts_dict, is_concepts_sorted=False):
        """Return a list of chains of concept indexes from the given set of ``concepts`` and ``superconcepts_dict``

        A chain of concept indexes is the list of concept indexes
        s.t. the first element of the chain is the index of top (biggest) concept
        each next element is a child of the previous one

        A list of chains covers covers all the concepts in the lattice

        Parameters
        ----------
        concepts: `list` of `FormalConcept` or `PatternConcept`
            A list of concepts of the lattice to compute the chains on
        superconcepts_dict: `dict` of type {`int`: `list` of `int`}
            A dict of superconcepts relation of the `concepts (i.e. {`child_concept_index`: `list` of `parent_concept_index`})
        is_concepts_sorted: `bool`
            A flag whether a list of ``concepts`` is sorted or not

        Returns
        -------
        chain: `list` of `list` of `int`
            A list of chains of concept indexes from the ConceptLattice

        """
        chains = []
        visited_concepts = set()

        n_concepts = len(concepts)

        if not is_concepts_sorted:
            concepts_sorted = cls.sort_concepts(concepts)
            map_concept_i_sort = {c: c_sort_i for c_sort_i, c in enumerate(concepts_sorted)}
            map_concept_i = {c: c_i for c_i, c in enumerate(concepts)}
            map_isort_i = [map_concept_i[concepts_sorted[c_i_sort]] for c_i_sort in range(n_concepts)]
            map_i_isort = [map_concept_i_sort[concepts[c_i]] for c_i in range(n_concepts)]

        while len(visited_concepts) < n_concepts:
            c_sort_i = n_concepts-1
            c_i = map_isort_i[c_sort_i] if not is_concepts_sorted else c_sort_i
            while c_i in visited_concepts:
                c_sort_i -= 1
                c_i = map_isort_i[c_sort_i] if not is_concepts_sorted else c_sort_i

            chain = []
            while True:
                chain.append(c_i)
                visited_concepts.add(c_i)
                if c_sort_i == 0:
                    break
                c_i = sorted(superconcepts_dict[c_i])[0]
                c_sort_i = map_i_isort[c_i] if not is_concepts_sorted else c_i
            chains.append(chain[::-1])
        return chains

    def to_json(self, path=None):
        """Convert (and possible save) a ConceptLattice in .json format

        Parameters
        ----------
        path: `str`
            A path to .json file

        Returns
        -------
        json_data: `str`
            ConceptLattice decoded in .json format (if ``path`` is None)
        None:
            (if ``path`` is not None)

        """
        assert len(self.concepts) >= 3,\
            'ConceptLattice.to_json error. The lattice should have at least 3 concepts to be saved in json'

        arcs = [{"S": s_i, "D": d_i} for s_i, d_is in self.subconcepts_dict.items() for d_i in d_is]

        lattice_metadata = {
            'Top': [self.top_concept_i], "Bottom": [self.bottom_concept_i],
            "NodesCount": len(self.concepts), "ArcsCount": len(arcs)
        }
        nodes_data = {"Nodes": [c.to_dict() for c in self.concepts]}
        arcs_data = {"Arcs": arcs}
        file_data = [lattice_metadata, nodes_data, arcs_data]
        json_data = json.dumps(file_data)

        if path is None:
            return json_data

        with open(path, "w") as f:
            f.write(json_data)

    def to_networkx(self, direction: str or None = 'down'):
        return self._to_networkx(direction, 'concept')

    @staticmethod
    def concepts_leq_func(a, b):
        return a <= b
