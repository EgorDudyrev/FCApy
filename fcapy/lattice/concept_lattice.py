"""
This module provides a ConceptLattice class. It may be considered as the main module (and class) of lattice subpackage

"""
import json

from typing import Tuple, Union, Optional, List, Dict, Set, Collection

from fcapy.algorithms import concept_construction as cca, lattice_construction as lca
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.lattice.pattern_concept import PatternConcept
from fcapy.mvcontext.mvcontext import MVContext
from fcapy.context.formal_context import FormalContext
from fcapy.poset.lattice import Lattice
from fcapy.utils import utils
from fcapy.mvcontext import pattern_structure as PS
import warnings
from frozendict import frozendict

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['numpy']:
    import numpy as np
    from numpy.typing import NDArray


class ConceptLattice(Lattice):
    """A class used to represent Concept Lattice object from FCA theory

    Properties
    ----------
    concepts: List[Union[FormalConcept, PatternConcept]]
        A list of concepts in the lattice
    measures: Dict[str, np.typing.NDArray]
        Dictionary with precomputed interestingness measures values of concepts

    Methods
    -------
    from_context(context, algo, ...):
       Construct a ConceptLattice from the given ``context`` by specified ``algo`` ('CbO','Sofia', 'RandomForest')
    calc_concepts_measures(measure, ...):
       Calculate interestingness ``measure`` of concepts in the ConceptLattice (like 'stability' or 'stability_bounds')
    trace_context(context, ...):
       Get the set of concepts from the ConceptLattice which describe objects from the given ``context``
    add(new_concept):
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
    elements: List[FormalConcept or PatternConcept]

    def __init__(self, concepts: List[FormalConcept or PatternConcept], **kwargs):
        """Construct a ConceptLattice based on a set of ``concepts`` and ``**kwargs`` values

        Parameters
        ----------
        concepts: `list`[`FormalConcept` or `PatternConcept`]
        kwargs:
            children_dict: `dict`{`int`, `list`[`int`]}
                A dictionary with children relation (preceding concepts) on ``concepts``
            parents_dict: `dict`{`int`, `list`[`int`]}
                A dictionary with parents relation (succeeding concepts)  on ``concepts``
            is_monotone: bool
                A flag whether lattice contains antimonotone (default) or monotone concepts
        """
        assert not (kwargs.get('children_dict') is not None and kwargs.get('parents_dict') is not None),\
            'Specify either "children_dict" or "parents_dict", not both at the same time'

        children_dict = kwargs.get('children_dict')
        if kwargs.get('parents_dict') is not None:
            children_dict = self._transpose_hierarchy(kwargs['parents_dict'])
        children_dict = {k: frozenset(vs) for k, vs in children_dict.items()} if children_dict is not None else None

        super(ConceptLattice, self).__init__(
            concepts,
            use_cache=True, children_dict=children_dict
        )
        self._generators_dict = {}
        self._is_monotone = kwargs.get('is_monotone', False)

    @property
    def T(self):
        assert isinstance(self[0], FormalConcept),\
            'ConceptLattice.T error. Can only transpose lattices of formal concepts'

        concepts_t = [FormalConcept(c.intent_i, c.intent, c.extent_i, c.extent,
                                    context_hash=-c.context_hash if c.context_hash else None)
                      for c in self.elements]
        return ConceptLattice(concepts_t, children_dict=self.parents_dict)

    @property
    def measures(self) -> Dict[str, NDArray]:
        """The dictionary containing all precomputed interestingness measures of concepts"""
        meas_dict = {}
        for i, c in enumerate(self):
            for k, v in c.measures.items():
                if k not in meas_dict:
                    meas_dict[k] = [None] * i

                meas_dict[k].append(v)
        meas_dict = {k: np.array(vs) for k, vs in meas_dict.items()}
        assert len(set([len(vs) for vs in meas_dict.values()])) == 1 or len(meas_dict) == 0
        return meas_dict

    @property
    def is_monotone(self):
        return self._is_monotone

    @staticmethod
    def get_top_bottom_concepts_i(
            concepts: List[FormalConcept or PatternConcept],
            is_concepts_sorted: bool = False
    ) -> Tuple[Optional[int], Optional[int]]:
        """Return the indexes of top and bottom concept from the list of ``concepts``

        Parameters
        ----------
        concepts: `list` of `FormalConcept` or `PatternConcept`
            A list of concepts to look for top (biggest) and bottom (smallest) concepts
        is_concepts_sorted: `bool`
            A flag whether the ``concepts`` are topologically sorted or they should be sorted inside the function
        Returns
        -------
        top_concept: `int`
            An index of the top (biggest) concept from the list of ``concepts``
        bottom_concept: `int`
            An index of the bottom (smallest) concept from the list of ``concepts``

        """
        # TODO: Refactor the function. Is it even needed?
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
    def from_context(
            cls,
            context: Union[FormalContext, MVContext],
            algo: Optional[str] = None,
            is_monotone: bool = False,
            **kwargs
    ) -> 'ConceptLattice':
        """Return a `ConceptLattice` constructed on the ``context`` by algorithm ``algo``

        Parameters
        ----------
        context: 'FormalContext` or 'MVContext`
        algo: `str` in {'CbO', 'Sofia', 'RandomForest'}
        is_monotone: bool
            Whether to build antimonotone lattice (if False, default) or monotone concept lattice
        kwargs:
            Parameters used in CbO, Sofia and RandomForest algorithms from `fcapy.algorithms.concept_construction` module

        Returns
        -------
        ltc: `ConceptLattice`
            A concept lattice constructed on the ``context`` by algorithm ``algo``

        """
        if is_monotone:
            return cls._from_context_monotone(context, algo, **kwargs)

        if algo is None:
            algo = 'CbO' if type(context) == MVContext else 'Lindig'

        if algo in {'CbO', 'RandomForest'}:
            algo_func = {'CbO': cca.close_by_one, 'RandomForest': cca.random_forest_concepts}[algo]
            kwargs_used = utils.get_kwargs_used(kwargs, algo_func)
            concepts = algo_func(context, **kwargs_used)
            concepts = cls.sort_concepts(concepts)
            subconcepts_dict = lca.construct_lattice_by_spanning_tree(concepts, is_concepts_sorted=True)

            ltc = ConceptLattice(
                concepts=concepts, subconcepts_dict=subconcepts_dict
            )

        elif algo in {'Sofia', 'Lindig'}:
            if algo == 'Sofia':
                algo_func = cca.sofia_general if type(context) == MVContext else cca.sofia_binary
            elif algo == 'Lindig':
                algo_func = cca.lindig_algorithm
            else:
                raise NotImplementedError("Error. Some unknown algo seen")

            kwargs_used = utils.get_kwargs_used(kwargs, algo_func)
            ltc = algo_func(context, **kwargs_used)

            # sort concepts in the same order as they have been created by CbO algorithm
            concepts_sorted = cls.sort_concepts(list(ltc))
            map_concept_i_sort = {c: c_sort_i for c_sort_i, c in enumerate(concepts_sorted)}
            map_i_isort = [map_concept_i_sort[ltc[c_i]] for c_i in range(len(ltc))]

            ltc._elements = concepts_sorted
            ltc._elements_to_index_map = {el: idx for idx, el in enumerate(concepts_sorted)}
            ltc._cache_leq = {}
            for cache_name in ['children', 'descendants', 'parents', 'ancestors']:
                cache_name = f"_cache_{cache_name}"
                ltc.__dict__[cache_name] = {
                    map_i_isort[i]: {map_i_isort[rel] for rel in relatives}
                    for i, relatives in ltc.__dict__[cache_name].items()
                }

            ltc._generators_dict = {map_i_isort[c_i]: {map_i_isort[supc_i]: gen for supc_i, gen in gens_dict.items()}
                                    for c_i, gens_dict in ltc._generators_dict.items()}
            if ltc._cache_top is not None:
                ltc._cache_top = map_i_isort[ltc._cache_top]
            if ltc._cache_bottom is not None:
                ltc._cache_bottom = map_i_isort[ltc._cache_bottom]

        else:
            raise ValueError(f'ConceptLattice.from_context error. Algorithm {algo} is not supported.\n'
                             f'Possible values are: "CbO" (stands for CloseByOne), "Sofia", "RandomForest", "Lindig"')
        return ltc

    @classmethod
    def _from_context_monotone(cls, context: FormalContext, algo: str, **kwargs) -> 'ConceptLattice':
        if not isinstance(context, FormalContext):
            raise NotImplementedError('Monotone concept lattice can only be constructed on Formal Contexts (for now)')

        L = ConceptLattice.from_context(~context, algo=algo, is_monotone=False, **kwargs)
        obj_idxs = set(range(context.n_objects))
        ctx_hash = context.hash_fixed()
        obj_names = context.object_names

        new_concepts = []
        for i, c in enumerate(L):
            new_ext_i = sorted(obj_idxs - set(c.extent_i))

            c_new = FormalConcept(
                extent_i=new_ext_i,
                extent=[obj_names[g_i] for g_i in new_ext_i],
                intent_i=c.intent_i,
                intent=[m[4:] if m.startswith('not ') else f'not {m}' for m in c.intent],
                context_hash=ctx_hash,
                is_monotone=True,
            )
            new_concepts.append(c_new)

        L = ConceptLattice(new_concepts, children_dict=L.children_dict, is_monotone=True)
        return L

    @staticmethod
    def sort_concepts(
            concepts: List[FormalConcept or PatternConcept]
    ) -> Optional[List[FormalConcept or PatternConcept]]:
        """Return the topologically sorted set of concepts

        (ordered by descending of support, lexicographical order of extent indexes)

        """
        if concepts is None:
            return None
        return sorted(concepts, key=lambda c: (-len(c.extent_i), ','.join([str(g) for g in c.extent_i])))

    def calc_concepts_measures(self, measure: str, context: FormalContext or MVContext = None):
        """Calculate the values of ``measure`` for each concept in a lattice

        The calculated measure values are stored in ``measures`` property
        of each ``concept`` from ``ConceptLattice.elements``

        Parameters
        ----------
        measure: `str` in {'stability_bounds', 'LStab', 'UStab', 'stability', 'target_entropy', 'mean_information_gain'}
            The name of the measure to compute
        context: `FormalContext` or `MVContext`
            The context is used when calculating 'stability' measure
        Returns
        -------
        None

        """
        # TODO: Reflect these measures in the docstring
        possible_measures = ['stability_bounds', 'LStab', 'UStab', 'stability',
                             'target_entropy', 'mean_information_gain']

        from fcapy.lattice import concept_measures as cms

        if measure in ('stability_bounds', 'LStab', 'UStab'):
            for c_i, c in enumerate(self):
                lb, ub = cms.stability_bounds(c_i, self)
                c.measures['LStab'] = lb
                c.measures['UStab'] = ub
        elif measure == 'stability':
            warnings.warn("Calculation of concept stability index takes exponential time. "
                          "One better use its approximate measure `stability_bounds`")
            assert context is not None, 'ConceptLattice.calc_concepts_measures failed. ' \
                                        'Please specify `context` parameter to calculate the stability'
            for c_i, c in enumerate(self):
                s = cms.stability(c_i, self, context)
                c.measures['Stab'] = s
        elif measure == 'target_entropy':
            for c_i, c in enumerate(self):
                c.measures[measure] = cms.target_entropy(c_i, self, context)
        elif measure == 'mean_information_gain':
            for c_i, c in enumerate(self):
                c.measures[measure] = cms.mean_information_gain(c_i, self)
        elif isinstance(measure, tuple) and len(measure) == 2:
            name, func = measure
            assert isinstance(name, str), 'Measure name should be a string'
            for c_i, c in enumerate(self):
                c.measures[name] = func(c_i, self, context)
        else:
            raise ValueError(f'ConceptLattice.calc_concepts_measures. The given measure {measure} is unknown. ' +
                             f'Possible measure values are either strings: {",".join(possible_measures)}, ' 
                             f'or a pair (measure_name: str, measure_func: c_i, lattice, context -> float)')

    @classmethod
    def get_all_superconcepts_dict(
            cls,
            concepts: List[FormalConcept or PatternConcept],
            parents_dict: Dict[int, Collection[int]]
    ) -> Dict[int, List[int]]:
        """Return the transitively closed superconcept relation of ``concept`` from ``parents_dict``

        The transitively closed superconcept relation of ``concept`` from ``superconcepts`` means the dict of type:
        {`child_concept_index`: `list` of indexes of all concepts bigger than the child}

        Parameters
        ----------
        concepts: `list` of `FormalConcept` or `PatternConcept`
            A list of concepts to compute relation on
        parents_dict: `dict` of type {`int`: `list` of `int`}
            The superconcept relation of the `concepts (i.e. {`child_concept_index`: `list` of `parent_concept_index`})

        Returns
        -------
        ancestors: `dict` of type {`int`: `list` of `int`}
            The transitively closed parents relation of ``concept`` from ``parents_dict``

        """
        # TODO: Refactor the function. Is it even needed?
        ancestors = {}
        concepts_to_visit = sorted(range(len(concepts)), key=lambda c_i: -concepts[c_i].support)
        for c_i in concepts_to_visit:
            ancestors[c_i] = parents_dict[c_i].copy()
            for supc_i in parents_dict[c_i]:
                ancestors[c_i] |= ancestors[supc_i]
        return ancestors

    @classmethod
    def get_all_subconcepts_dict(
            cls,
            concepts: List[Union[FormalConcept, PatternConcept]],
            children_dict: Dict[int, Collection[int]]
    ) -> Dict[int, List[int]]:
        """Return the transitively closed children relation of ``concept`` from ``children_dict``

        The transitively closed children relation of ``concept`` from ``children_dict`` means the dict of type:
        {`parent_concept_index`: `list` of indexes of all concepts smaller than the parent}

        Parameters
        ----------
        concepts: `list` of `FormalConcept` or `PatternConcept`
            A list of concepts to compute relation on
        children_dict: `dict` of type {`int`: `list` of `int`}
            The children relation of the ``concepts`` (i.e. {`parent_concept_index`: `list` of `children_concept_index`})

        Returns
        -------
        descendants: `dict` of type {`int`: `list` of `int`}
            The transitively closed children relation of ``concept`` from ``children_dict``

        """
        # TODO: Refactor the function. Is it even needed?
        descendants = {}
        concepts_to_visit = sorted(list(range(len(concepts))), key=lambda c_i: concepts[c_i].support)
        for c_i in concepts_to_visit:
            descendants[c_i] = children_dict[c_i].copy()
            for subc_i in children_dict[c_i]:
                descendants[c_i] |= descendants[subc_i]
        return descendants

    def trace_context(
            self,
            context: Union[FormalContext, MVContext],
            use_object_indices: bool = False,
            use_generators: bool = False,
            use_tqdm: bool = False,
            return_generators_extents: bool = False
    ) -> Tuple[Dict[int, List[int]], Dict[int, List[int]], List[frozendict]]:
        """Return the dictionaries which map an object from ``context`` to a set of bottom/all the concepts which cover it

        Parameters
        ----------
        context: `FormalContext` or `PatternContext`
            A Formal (or Pattern) Context to trace
        use_object_indices: `bool`
            A flag whether to return a dict with keys as object indices (if True) or object names (if False)
        use_generators: `bool`
            A flag whether to describe object of `context` by closed concept intents (if False) or their generators (o/w)
        use_tqdm: `bool`
            A flag whether to visualize the progress of the algorithm with tqdm bar
        return_generators_extents: `bool`
            A flag whether to add generators extents statistics in the output

        Returns
        -------
        object_bottom_concepts: `dict` of type {`int`: `list` of `int`}
            Dictionary which maps each object from the ``context`` to a subset of the smallest concepts
            from the ConceptLattice which describe this object
        object_traced_concepts: `dict` of type {`int`: `list` of `int`}
            Dictionary which maps each object from the ``context`` to a subset of all the concepts
            from the ConceptLattice which describe this object
        generators_extents: `list` of `dict`
            A list of dictionaries containing information about generators ran while tracing.

        """
        if self.is_monotone:
            raise NotImplementedError('Tracing lattice of monotone concepts is not yet supported')

        concept_extents = {}
        if return_generators_extents:
            generators_extents = []

        def stored_extension(concept_i, use_generators, superconcept_i=None):
            if not use_generators:
                if concept_i not in concept_extents:
                    concept_extents[concept_i] = set(context.extension_i(self[concept_i].intent_i))
                extent = concept_extents[concept_i]
            else:
                if concept_i not in concept_extents:
                    concept_extents[concept_i] = {}

                if concept_i == self.top:
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

        concepts_to_visit = [self.top]
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
                subconcepts_i = self.children_dict[c_i]

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
            new_concepts = sorted(new_concepts, key=lambda c_i: -self[c_i].support)
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

    def get_conditional_generators_dict(
            self,
            context: MVContext,
            use_tqdm: bool = False,
            algo: str = 'exact'
    ) -> Dict[int, Dict[int, List[frozendict]]]:
        """Return the conditional generators of concepts from the Concept Lattice

        WARNING: No comments for now. The notion of conditional generators is under construction
        """
        condgen_dict = dict()
        condgen_dict[self.top] = {}

        assert algo in {'approximate', 'exact'}, f"Given algorithm '{algo}' is not supported. " \
                                                 f"Possible values are: 'approximate', 'exact'"


        concepts_sorted = self.sort_concepts(list(self))
        map_concept_i = {c: c_i for c_i, c in enumerate(self)}
        map_isort_i = [map_concept_i[concepts_sorted[c_i_sort]] for c_i_sort in range(len(self))]
        concepts_to_visit = map_isort_i

        if not LIB_INSTALLED['numpy'] or type(context) is not MVContext:
            supc_exts_i = [frozenset(context.extension_i(c.intent_i)) for c in self]
        else:
            supc_exts_i = [np.array(context.extension_i(c.intent_i)) for c in self]

        for c_i in utils.safe_tqdm(concepts_to_visit[1:], disable=not use_tqdm, desc='Calc conditional generators'):
            intent_i = self[c_i].intent_i

            superconcepts_i = self.parents_dict[c_i]

            condgens = {}
            if algo == 'exact':
                if type(context) is MVContext:
                    for supc_i in utils.safe_tqdm(superconcepts_i, desc='Iterate superconcepts', leave=False, disable=not use_tqdm):
                        supc_ext_i = supc_exts_i[supc_i]
                        supc_int_i = self[supc_i].intent_i
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
                        intent_i, self[supc_i].intent_i)
            condgen_dict[c_i] = condgens

        return condgen_dict

    def get_concept_new_extent_i(self, concept_i: int) -> Set[int]:
        """Return the subset of objects indexes which are contained in ``concept_i`` but not its children concepts"""
        sbc_is = self.children_dict[concept_i]
        sbc_extents_i = {g_i for sbc_i in sbc_is for g_i in self[sbc_i].extent_i}
        new_extent_i = set(self[concept_i].extent_i) - sbc_extents_i
        return new_extent_i

    def get_concept_new_extent(self, concept_i: int) -> Set[str]:
        """Return the subset of objects which are contained in ``concept_i`` but not its children concepts"""
        sbc_is = self.children_dict[concept_i]
        sbc_extents = {g for sbc_i in sbc_is for g in self[sbc_i].extent}
        new_extent = set(self[concept_i].extent) - sbc_extents
        return new_extent

    def get_concept_new_intent_i(self, concept_i: int) -> Set[int]:
        """Return the subset of attributes indexes which are contained in ``concept_i`` but not its parent concepts"""
        spc_is = self.parents_dict[concept_i]
        spc_intent_i = {m_i for spc_i in spc_is for m_i in self[spc_i].intent_i}
        new_intent_i = set(self[concept_i].intent_i) - spc_intent_i
        return new_intent_i

    def get_concept_new_intent(self, concept_i: int) -> Set[str]:
        """Return the subset of objects which are contained in ``concept_i`` but not its parent concepts"""
        spc_is = self.parents_dict[concept_i]
        spc_intent = {m for spc_i in spc_is for m in self[spc_i].intent}
        new_intent = set(self[concept_i].intent) - spc_intent
        return new_intent

    def get_chains(self) -> List[List[int]]:
        """Return a list of chains of concept indexes from the ConceptLattice

        A chain of concept indexes is the list of concept indexes
        s.t. the first concept of the chain is the index of top (biggest) concept
        each next concept is a child of the previous one

        A list of chains covers covers all the concepts in the lattice

        Returns
        -------
        chain: `list` of `list` of `int`
            A list of chains of concept indexes from the ConceptLattice

        """
        return self._get_chains(self.elements, self.parents_dict)

    @classmethod
    def _get_chains(
            cls,
            concepts: List[Union[FormalConcept, PatternConcept]],
            superconcepts_dict: Dict[int, List[int]],
            is_concepts_sorted: bool = False
    ) -> List[List[int]]:
        """Return a list of chains of concept indexes from the given set of ``concepts`` and ``parents_dict``

        A chain of concept indexes is the list of concept indexes
        s.t. the first concept of the chain is the index of top (biggest) concept
        each next concept is a child of the previous one

        A list of chains covers all the concepts in the lattice

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
        # TODO: Move the function to Lattice class or even POSet class if possible
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

    @staticmethod
    def read_json(path: str = None, json_data: str = None, pattern_types: Tuple[PS.AbstractPS] = None):
        """Read ConceptLattice from .json file .json formatted string data

        Parameters
        ----------
        path: `str`
            A path to .json file
        json_data: `str`
            A json encoded data
        pattern_types: `tuple` of pattern structure types
            A set of pattern types to decode the values in concept intents (if reading pattern concept lattice)

        Returns
        -------
        ltc: `ConceptLattice`

        """
        assert path is not None or json_data is not None,\
            "ConceptLattice.read_json error. Either path or json_data input parameters should be given"

        if path is not None:
            with open(path, 'r') as f:
                json_data = f.read()
        file_data = json.loads(json_data)
        lattice_metadata, nodes_data, arcs_data = file_data
        top_concept_i = lattice_metadata['Top'][0]
        bottom_concept_i = lattice_metadata['Bottom'][0]

        is_pattern = 'PTypes' in nodes_data['Nodes'][0]['Int']

        concepts = [
            PatternConcept.from_dict(c_dict, json_ready=True, pattern_types=pattern_types) if is_pattern else
            FormalConcept.from_dict(c_dict)
            for c_dict in nodes_data['Nodes']
        ]
        subconcepts_dict = {}
        for arc in arcs_data['Arcs']:
            subconcepts_dict[arc['S']] = subconcepts_dict.get(arc['S'], set()) | {arc['D']}
        subconcepts_dict[bottom_concept_i] = set()

        ltc = ConceptLattice(
            concepts=concepts, subconcepts_dict=subconcepts_dict,
            top_concept_i=top_concept_i, bottom_concept_i=bottom_concept_i
        )
        return ltc

    def write_json(self, objs_order: List[str], attrs_order: List[str], path: str = None) -> Optional[str]:
        """Convert (and possible save) a ConceptLattice in .json format

        Parameters
        ----------
        objs_order: List[str]
            Names of objects put into list (so that name of object i is objs_order[i])
        attrs_order: List[str]
            Names of attributes put into list (so that name of attribute i is attrs_order[i])
        path: str
            A path to .json file

        Returns
        -------
        json_data: `str`
            ConceptLattice decoded in .json format (if ``path`` is None)
        None:
            (if ``path`` is not None)

        """
        assert len(self) >= 3,\
            'ConceptLattice.write_json error. The lattice should have at least 3 concepts to be saved in json'

        arcs = [{"S": s_i, "D": d_i} for s_i, d_is in self.children_dict.items() for d_i in d_is]

        lattice_metadata = {
            'Top': [self.top], "Bottom": [self.bottom],
            "NodesCount": len(self), "ArcsCount": len(arcs)
        }
        if isinstance(self[0], PatternConcept):
            to_dict_kwargs = dict(json_ready=True)
        else:  # if FormalConcept
            to_dict_kwargs = dict(objs_order=objs_order, attrs_order=attrs_order)
        nodes_data = {"Nodes": [c.to_dict(**to_dict_kwargs) for c in self]}
        arcs_data = {"Arcs": arcs}
        file_data = [lattice_metadata, nodes_data, arcs_data]
        json_data = json.dumps(file_data)

        if path is None:
            return json_data

        with open(path, "w") as f:
            f.write(json_data)

    def to_networkx(self, direction: str or None = 'down'):
        """Generate Networkx graph from the concept lattice

        Parameters
        ----------
        direction: {`up`, `down`}
            `up` if the graph should be directed from the lowest concepts to the greatest. `down` otherwise
        Returns
        -------
        `nx.DiGraph`
        """
        return self._to_networkx(direction, 'concept')
