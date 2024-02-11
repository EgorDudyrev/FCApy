"""
This module contains functions that take a `FormalContext` (or `MVContext`)
and return a set of formal (or pattern) concepts.
Some of them return a `ConceptLattice` instead of just a set of concepts.

"""
from collections import deque
from typing import List, Tuple, Iterator, Iterable, Union

from bitarray import frozenbitarray as fbarray
from bitarray.util import zeros as bazeros
from caspailleur.order import inverse_order, sort_intents_inclusion

from fcapy.context.formal_context import FormalContext
from fcapy.context.bintable import BinTableBitarray
from fcapy.mvcontext.mvcontext import MVContext
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.lattice.pattern_concept import PatternConcept
from fcapy.utils import utils


def close_by_one(context: Union[FormalContext, MVContext], n_projections_to_binarize: int = 1000)\
        -> Iterator[Union[FormalConcept, PatternConcept]]:
    """Return a list of concepts generated by CloseByOne (CbO) algorithm

    Parameters
    ----------
    context: `FormalContext` or `MVContext`
        A context to build a set of concepts on
    n_projections_to_binarize: int
        The maximal number of projections of MVContext, s.t. it can be binarized.
        Binarizing the context may fasten up the computations. However, it can also result in more memory consumption.

    Returns
    -------
    concepts: `Iterator` of `FormalConcept` or `PatternConcept`
        An iterator of concepts of class `FormalConcept` (if given context is of type `FormalContext`)
        or `PatternConcept` (if given context is of type `MVContext`)

    """
    if isinstance(context, FormalContext):
        if context.n_objects < context.n_bin_attrs:
            return close_by_one_objectwise_fbarray(context)
        # not wide, i.e. contains more objects than attributes
        return (
            FormalConcept.from_objects(c.intent_i, context, is_extent=True)
            for c in close_by_one_objectwise_fbarray(context.T)
        )

    # not formal, i.e. many valued context
    try:
        n_projections = context.n_bin_attrs
    except NotImplementedError:
        n_projections = None

    if n_projections is None or n_projections > n_projections_to_binarize:
        return close_by_one_objectwise(context)

    # n_projections <= n_projections_to_binarize:
    if context.n_objects <= n_projections:
        extents_iter = (c.extent_i for c in close_by_one_objectwise_fbarray(context.binarize()))
    else:  # context.n_objects > n_projections
        extents_iter = (c.intent_i for c in close_by_one_objectwise_fbarray(context.binarize().T))

    return (PatternConcept.from_objects(extent, context) for extent in extents_iter)


def close_by_one_objectwise(context: Union[FormalContext, MVContext]) -> Iterator[Union[FormalConcept, PatternConcept]]:
    """Return a list of concepts generated by CloseByOne (CbO) algorithm

    Parameters
    ----------
    context: `FormalContext` or `MVContext`
        A context to build a set of concepts on

    Returns
    -------
    concepts: `iterator` of `FormalConcept` or `PatternConcept`
        A list of concepts of class `FormalConcept` (if given context is of type `FormalContext`)
        or `PatternConcept` (if given context is of type `MVContext`)

    """
    n_objs = context.n_objects
    concept_cls = FormalConcept if isinstance(context, FormalContext) else PatternConcept

    extents_i_found = set()
    combinations_to_check = deque([tuple()])

    while combinations_to_check:
        comb_i = combinations_to_check.pop()
        intent_i = context.intention_i(comb_i)
        comb_i_set = set(comb_i)
        if comb_i:
            objects_lexicographic = [g_i for g_i in range(comb_i[-1]) if g_i not in comb_i_set]
            extent_lexicographic = context.extension_i(intent_i, base_objects_i=objects_lexicographic)
            if extent_lexicographic:
                continue

        base_objects_i = range(comb_i[-1]+1, n_objs) if comb_i else range(n_objs)
        base_objects_i = [i for i in base_objects_i if i not in comb_i_set]
        extent_i = comb_i + tuple(context.extension_i(intent_i, base_objects_i=base_objects_i))

        if extent_i in extents_i_found:
            continue

        yield concept_cls.from_objects(extent_i, context, is_extent=True)

        possible_new_objects = range(n_objs - 1, (comb_i[-1] if comb_i else 0) - 1, -1)
        extent_i_set = set(extent_i)
        new_combs = [extent_i + (g_i,) for g_i in possible_new_objects if g_i not in extent_i_set]
        combinations_to_check.extend(new_combs)


def close_by_one_objectwise_fbarray(context: Union[FormalContext, MVContext])\
        -> Iterator[Union[FormalConcept, PatternConcept]]:
    """Return a list of concepts generated by CloseByOne (CbO) algorithm

    Parameters
    ----------
    context: `FormalContext` or `MVContext`
        A context to build a set of concepts on

    Returns
    -------
    concepts: `iterator` of `FormalConcept` or `PatternConcept`
        A list of concepts of class `FormalConcept` (if given context is of type `FormalContext`)
        or `PatternConcept` (if given context is of type `MVContext`)

    """
    n_objs, n_attrs = context.n_objects, context.n_bin_attrs
    concept_cls = FormalConcept if isinstance(context, FormalContext) else PatternConcept

    all_attrs = ~bazeros(n_attrs)

    context_bin = context.binarize() if isinstance(context, MVContext) else context
    objs_descriptions = BinTableBitarray(context_bin.data.data).data

    def intention_ba(objs_idxs: Iterable[int]) -> fbarray:
        intent = all_attrs.copy()
        for g_i in objs_idxs:
            intent &= objs_descriptions[g_i]
        return fbarray(intent)

    def extension_iter(intent_ba: fbarray, base_objects: Iterable[int] = range(n_objs)) -> Iterator[int]:
        for g_i in base_objects:
            if intent_ba & objs_descriptions[g_i] == intent_ba:
                yield g_i

    intents_found: set[fbarray] = set()
    combinations_to_check = deque([tuple()])
    n_cncpt = 0

    while combinations_to_check:
        comb_i = combinations_to_check.pop()
        intent_ba = intention_ba(comb_i)
        if intent_ba in intents_found:
            continue

        comb_i_set = set(comb_i)
        if comb_i:
            objects_lexicographic = (g_i for g_i in range(comb_i[-1]) if g_i not in comb_i_set)
            objects_lexicographic = extension_iter(intent_ba, objects_lexicographic)
            if any(True for _ in objects_lexicographic):
                continue

        base_objects_i = range((comb_i[-1]+1) if comb_i else 0, n_objs)
        base_objects_i = (i for i in base_objects_i if i not in comb_i_set)
        extent_i = comb_i + tuple(extension_iter(intent_ba, base_objects_i))

        yield concept_cls.from_objects(extent_i, context)

        n_cncpt += 1

        intents_found.add(intent_ba)
        possible_new_objects = range(n_objs - 1, (comb_i[-1] if comb_i else 0) - 1, -1)
        extent_i_set = set(extent_i)
        new_combs = [extent_i + (g_i,) for g_i in possible_new_objects if g_i not in extent_i_set]
        combinations_to_check.extend(new_combs)


def sofia(
        K: Union[FormalContext, MVContext], L_max: int = 100, min_supp: float = 0,
        use_tqdm: bool = False, use_log_stability_bound=True
) -> List[Union[FormalConcept, PatternConcept]]:
    min_supp = min_supp * len(K) if min_supp < 1 else min_supp

    if use_log_stability_bound:
        def stability_lbounds(extents: List[fbarray]) -> List[float]:
            #assert all(a.count() <= b.count() for a, b in zip(extents, extents[1:]))
            bounds = []
            for i, extent in enumerate(extents):
                bound = extent.count()
                for potent_child in extents[i-1::-1]:
                    if potent_child & extent == potent_child:
                        bound -= potent_child.count()
                        break
                bounds.append(bound)
            return bounds
    else:
        def stability_lbounds(extents: List[fbarray]) -> List[float]:
            children_ordering = inverse_order(sort_intents_inclusion(extents))
            children_intersections = (
                ((extent & (~extents[child])).count() for child in children.itersearch(True))
                if children.any() else [extent.count()]
                for children, extent in zip(children_ordering, extents)
            )
            bounds = [1-sum(2**(-v) for v in intersections) for intersections in children_intersections]
            return bounds

    extents_proj: List[fbarray] = [fbarray(~bazeros(K.n_objects))]

    n_projs = K.n_bin_attrs
    proj_iterator = utils.safe_tqdm(enumerate(K.to_bin_attr_extents()), total=n_projs,
                                    desc='Iter. Sofia projections', disable=not use_tqdm)
    for proj_i, (_, attr_extent_ba) in proj_iterator:
        if attr_extent_ba.all():
            continue

        if attr_extent_ba.count() < min_supp:
            continue

        new_extents = {extent & attr_extent_ba for extent in extents_proj}
        extents_proj = sorted(set(extents_proj) | new_extents, key=lambda extent: extent.count())
        extents_proj = extents_proj[:1] + [extent for extent in extents_proj[1:] if extent.count() >= min_supp]

        if len(extents_proj) > L_max:
            measure_values = stability_lbounds(extents_proj)
            thold = sorted(measure_values)[::-1][L_max]
            extents_proj = [extent for extent_i, (extent, measure) in enumerate(zip(extents_proj, measure_values))
                            if measure > thold or extent_i in {0, len(extents_proj)-1}]

    concept_cls = FormalConcept if isinstance(K, FormalContext) else PatternConcept
    final_concepts = [concept_cls.from_objects(extent.itersearch(True), K, is_extent=True) for extent in extents_proj]
    return final_concepts


def parse_decision_tree_to_extents(tree, X, n_jobs=1) -> List[Tuple[int, ...]]:
    """Return a set of extents of nodes from sklearn `DecisionTree` (or `RandomForest`)

    Parameters
    ----------
    tree: `DecisionTreeRegressor` or `DecisionTreeClassifier` or `RandomForestRegressor` or `RandomForestClassifier`
        sklearn DecisionTree or RandomForest to retrieve a set of extents from
    X: `numpy.ndarray`
        An input data for ``tree`` model. The same format it is used for ``tree.predict(X)`` function
    n_jobs: `int`
        A number of parallel jobs to run. WARNING: A number of jobs works slower than a single one.
    Returns
    -------
    exts: `list` of `int`
        A list of objects indexes from ``X`` described by nodes of decision tree(s) from ``tree``

    """
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

    if isinstance(tree, (RandomForestClassifier, RandomForestRegressor)):
        paths = tree.decision_path(X)[0].tocsc()
    else:
        paths = tree.decision_path(X).tocsc()

    def get_indices(i, paths):
        return paths.indices[paths.indptr[i]:paths.indptr[i + 1]]
    paths = utils.sparse_unique_columns(paths)[0]

    if n_jobs == 1:
        exts = [get_indices(i, paths) for i in range(paths.shape[1])]
    else:
        from joblib import Parallel, delayed
        exts = Parallel(n_jobs)([delayed(get_indices)(i, paths) for i in range(paths.shape[1])])
    exts = [tuple(ext) for ext in exts]
    return exts


def random_forest_concepts(context: Union[FormalContext, MVContext], rf_params=None, rf_class=None):
    """Fit a RandomForest model and return a set of pattern concepts used by this model

    Parameters
    ----------
    context: `MVContext`
        A context to fit a RandomForest on.
        Training features data for the Forest are kept in context.data
        Target values are kept in ``context.target``
    rf_params: `dict`
        A dict of parameters to initialize RandomForest model with
    rf_class: type `RandomForestRegressor` or `RandomForestClassifier`
        A type of RandomForest model to fit.
        By default this value is set to RandomForestClassifier if ``context.target`` value has only 2 distinct values
    Returns
    -------
    concepts: `list` of `PatternConcept`
        A list of PatternConcepts retrieved from context by RandomForest

    """
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    concept_cls = FormalConcept if isinstance(context, FormalContext) else PatternConcept

    rf_params = rf_params if rf_params is not None else {}

    X = context.to_numeric()[0]
    Y = context.target

    if rf_class is None:
        rf_class = RandomForestClassifier if len(set(Y)) == 2 else RandomForestRegressor

    rf = rf_class(**rf_params)
    rf.fit(X, Y)
    extents_i = parse_decision_tree_to_extents(rf, X)
    extents_i.append(context.extension_i(context.intention_i([])))

    return [concept_cls.from_objects(extent_i, context, is_extent=True) for extent_i in extents_i]


def lindig_algorithm(context: FormalContext, iterate_extents=None):
    """Get Concept Lattice from Formal Context using Lindig algorithm
    (https://www.researchgate.net/publication/2812391_Fast_Concept_Analysis)

    Parameters
    ----------
    context: `FormalContext`
        A context to build lattice on
    iterate_extents: `bool`
        A flag whether to run Lindig by iterating through subsets of objects (if set True) or of attributes (if set False)
        By default it sets to True if the set of objects is smaller than the set of attributes and False otherwise

    Returns
    -------
    lattice: `ConceptLattice`
        A ConceptLattice which contains a set of Formal Concepts and relations between them

    """
    if type(context) == MVContext:
        raise NotImplementedError('Sorry. Lindig algorithm is not yet implemented for ManyValued context')

    from fcapy.lattice import ConceptLattice

    if iterate_extents is None:
        iterate_extents = context.n_objects < context.n_attributes

    n_objects = context.n_objects
    n_attributes = context.n_attributes
    intention_i = context.intention_i
    extension_i = context.extension_i
    object_names = context.object_names
    attribute_names = context.attribute_names
    if not iterate_extents:
        n_objects, n_attributes = n_attributes, n_objects
        intention_i, extension_i = extension_i, intention_i
        object_names, attribute_names = attribute_names, object_names
    context_hash = context.hash_fixed()


    def direct_super_concepts(concept):
        extent = set(concept.extent_i)
        reps = set(range(n_objects)) - extent
        neighbors = []
        for g in set(reps):
            extent.add(g)
            M = intention_i(list(extent))
            G = extension_i(M)
            extent.remove(g)
            if len(reps & set(G)) == 1:
                neighbors.append(FormalConcept(G, [object_names[i] for i in G],
                                               M, [attribute_names[i] for i in M],
                                               context_hash = context_hash))
            else:
                reps.remove(g)
        return neighbors

    M = list(range(n_attributes))
    G = extension_i(M)
    c = FormalConcept(G, [object_names[i] for i in G],
                      M, [attribute_names[i] for i in M],
                      context_hash = context_hash)

    concepts = [c]
    queue = {c}
    children_dict = {0: []}
    parents_dict = {}

    index = {c : 0}

    while len(queue) != 0:
        c = queue.pop()
        c_id = index[c]
        dsups = direct_super_concepts(c)
        if len(dsups) == 0:
            parents_dict[c_id] = []
            continue

        for x in dsups:
            if x not in index:
                queue.add(x)
                index[x] = len(concepts)
                concepts.append(x)
            x_id = index[x]

            children_dict.setdefault(x_id, []).append(c_id)
            parents_dict.setdefault(c_id, []).append(x_id)

    if not iterate_extents:
        concepts = [FormalConcept(concepts[i].intent_i, concepts[i].intent,
                                  concepts[i].extent_i, concepts[i].extent,
                                  context_hash=context_hash)
                    for i in range(len(concepts))]
        children_dict, parents_dict = parents_dict, children_dict

    lattice = ConceptLattice(concepts, children_dict=children_dict)
    return lattice


def lcm_skmine(context: Union[FormalContext, MVContext], min_supp: float = 1, n_jobs: int = 1)\
        -> List[Union[FormalConcept, PatternConcept]]:
    from skmine.itemsets import LCM

    context_bin = context if isinstance(context, FormalContext) else context.binarize()
    itemsets = [list(row.itersearch(True)) for row in BinTableBitarray(context_bin.data.data)]

    lcm = LCM(min_supp=min_supp, n_jobs=n_jobs)
    lcm_data = lcm.fit_transform(itemsets, return_tids=True)
    intents_i = list(lcm_data['itemset'])
    extents_i = [list(row) for row in lcm_data['tids']]
    del lcm_data

    if all(len(intent_i) < context_bin.n_attributes for intent_i in intents_i):
        bottom_extent = context_bin.extension_i(list(range(context_bin.n_attributes)))
        extents_i.append(bottom_extent)

    if all(len(extent_i) < context_bin.n_objects for extent_i in extents_i):
        extents_i.append(list(range(context_bin.n_objects)))

    concept_cls = FormalConcept if isinstance(context, FormalContext) else PatternConcept
    return [concept_cls.from_objects(extent_i, context) for extent_i in extents_i]
