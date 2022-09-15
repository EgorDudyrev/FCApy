"""
This module contains functions that take a `FormalContext` (or `MVContext`)
and return a set of formal (or pattern) concepts.
Some of them return a `ConceptLattice` instead of just a set of concepts.

"""
from fcapy.context.formal_context import FormalContext
from fcapy.mvcontext.mvcontext import MVContext
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.lattice.pattern_concept import PatternConcept
from fcapy.utils import utils
import random
from copy import deepcopy, copy
import math


def close_by_one(context: MVContext, output_as_concepts=True, iterate_extents=None,
                 initial_combinations=None, iter_concepts_to_check=None):
    """Return a list of concepts generated by CloseByOne (CbO) algorithm

    Parameters
    ----------
    context: `FormalContext` or `MVContext`
        A context to build a set of concepts on
    output_as_concepts: `bool`
        A flag whether to return a list of concepts as a list of `FormalConcept`/`PatternConcept` objects (if set True)
        or as a dictionary with concepts extents and intents
    iterate_extents: `bool`
        A flag whether to run CbO by iterating through subsets of objects (if set True) or of attributes (if set False)
        By default it sets to True if the set of objects is smaller than the set of attributes
    initial_combinations: `list` of `int`
        A list of subsets of objects/attributes indexes (depends on ``iterate_extents``) to start CbO algorithm from
        Default value is empty list []
    iter_concepts_to_check: `list` of `int`
        A list of attributes/objects indexes (depends on ``iterate_extents``) to run CbO algorithm on

    Returns
    -------
    Either ``data`` or ``concepts`` depends on ``output_as_concepts`` attribute
    data: `dict`
        A dictionary which contains a set of concepts extents and concepts intents
    concepts: `list` of `FormalConcept` or `PatternConcept`
        A list of concepts of class `FormalConcept` (if given context is of type `FormalContext`)
        or `PatternConcept` (if given context is of type `MVContext`)

    """
    if iterate_extents is False:
        assert type(context) == FormalContext, "Can set iterate_extents=False only if FormalContext is given"

    if initial_combinations is not None:
        assert iterate_extents is not None,\
            "`iterate_extents parameter should be specified if initial_combinations are given " \
            "(`True if initial_combinations are extents, `False if inital_combinations are intents)"

    if iter_concepts_to_check is not None:
        assert iterate_extents is not None, \
            "`iterate_extents parameter should be specified if iter_concepts_to_check are given " \
            "(`True if iter_concepts_to_check are objects, `False if iter_concepts_to_check are attributes)"

    if iterate_extents is None:
        iterate_extents = context.n_objects < context.n_attributes if type(context) == FormalConcept else True
    n_iters = context.n_objects if iterate_extents else context.n_attributes

    # <iterset> - iterating set - the set of object if one construct construct concepts while iterating over objects,
    #   the set of attributes otherwise
    # <sideset> - the other set, "sided" with <iterset>.
    #   If <iterset> is the set of objects then <sideset> is the set of attributes and vice versa
    iterset_fnc, sideset_fnc = context.extension_i, context.intention_i
    if not iterate_extents:
        iterset_fnc, sideset_fnc = sideset_fnc, iterset_fnc

    iter_concepts_to_check = list(range(n_iters)) if iter_concepts_to_check is None else iter_concepts_to_check

    itersets_i_dict = {}
    sidesets_i = []
    combinations_to_check = [[]] if initial_combinations is None else initial_combinations

    while len(combinations_to_check) > 0:
        comb_i = combinations_to_check.pop(0)
        sideset_i = sideset_fnc(comb_i)
        iterset_i = tuple(iterset_fnc(sideset_i))
        iterset_i_new = sorted(set(iterset_i)-set(comb_i))

        is_not_lexicographic = len(comb_i) > 0 and any([g_i < comb_i[-1] for g_i in iterset_i_new])
        is_duplicate = iterset_i in itersets_i_dict
        if any([is_not_lexicographic, is_duplicate]):
            continue

        itersets_i_dict[iterset_i] = len(sidesets_i)
        sidesets_i.append(sideset_i)

        iterset_i = list(iterset_i)

        new_combs = []
        for g_i in iter_concepts_to_check:
            if g_i not in iterset_i \
                    and (len(comb_i) == 0 or g_i > comb_i[-1]):
                new_combs.append(iterset_i+[g_i])
        combinations_to_check = new_combs + combinations_to_check

    itersets_i = list({idx: x_i for x_i, idx in itersets_i_dict.items()}.values())

    extents_i, intents_i = itersets_i, sidesets_i
    if not iterate_extents:
        extents_i, intents_i = intents_i, extents_i

    if output_as_concepts:
        object_names = context.object_names
        attribute_names = context.attribute_names
        context_hash = context.hash_fixed()

        concepts = []
        for concept_data in zip(extents_i, intents_i):
            extent_i, intent_i = concept_data
            extent = [object_names[g_i] for g_i in extent_i]
            if type(context) == FormalContext:
                intent = [attribute_names[m_i] for m_i in intent_i]
                concept = FormalConcept(extent_i, extent, intent_i, intent, context_hash=context_hash)
            else:
                intent = {context.pattern_structures[ps_i].name: description for ps_i, description in intent_i.items()}
                concept = PatternConcept(
                    extent_i, extent, intent_i, intent,
                    context.pattern_types, context.attribute_names,
                    context_hash=context_hash)
            concepts.append(concept)
        return concepts

    data = {'extents_i': extents_i, 'intents_i': intents_i}
    return data


def sofia_objectwise(
        K: FormalContext or MVContext,
        L_max: int = 100, measure_name: str = 'LStab',
        use_tqdm: bool = False,
        proj_start: int = None
) -> 'ConceptLattice':
    from fcapy.lattice import ConceptLattice

    #############
    # The Setup #
    #############
    is_K_multivalued = isinstance(K, MVContext)

    # Define concept constructors based on the class of context K
    if is_K_multivalued:
        def concept_factory(ext_i, ext_, int_i, int_, hash_):
            return PatternConcept(ext_i, ext_, int_i, int_, K.pattern_types, K.attribute_names, context_hash=hash_)
    else:
        def concept_factory(ext_i, ext_, int_i, int_, hash_):
            return FormalConcept(ext_i, ext_, int_i, int_, context_hash=hash_)

    def close_by_one_proj(K_, extents, i):
        f = close_by_one(
            K_,
            initial_combinations=extents, iter_concepts_to_check=[i-1],
            output_as_concepts=True, iterate_extents=True,
        )
        return f

    # Define where to start and where to end while iterating projections
    proj_start = int(math.log2(L_max)) if proj_start is None else proj_start
    max_proj = len(K)

    proj_iterator = range(proj_start + 1, max_proj + 1)
    if use_tqdm:
        proj_iterator = utils.safe_tqdm(proj_iterator, desc='SOFIA: Iterate objects')

    #################
    # The Algorithm #
    #################

    # Step 1: Construct a lattice on a small enough subset of the context
    K_proj = K[:proj_start]
    L_proj = ConceptLattice.from_context(K_proj, algo='CbO')

    for proj_i in proj_iterator:
        # Step i.0: Update context projection
        K_proj = K[:proj_i]

        # Step i.1: Update old concepts to the new context
        K_proj_hash = K_proj.hash_fixed()
        for c in L_proj:
            ext_i_new = K_proj.extension_i(c.intent_i)
            ext_new = [K_proj.object_names[g_i] for g_i in ext_i_new]
            c_new = concept_factory(ext_i_new, ext_new, c.intent_i, c.intent, K_proj_hash)
            L_proj._update_element(c, c_new)

        # Step i.2: Construct concepts on a new part of the context
        extents_proj = [c.extent_i for c in L_proj]
        new_concepts = close_by_one_proj(K_proj, extents_proj, proj_i)

        # Step i.3: Add new concepts to the lattice

        # concepts that were changed during projection iteration
        concepts_to_add = list(set(new_concepts) - set(L_proj))
        # sort concepts to ensure there will be no moment with multiple top or bottom concepts
        concepts_to_add = L_proj.sort_concepts(concepts_to_add)
        if len(concepts_to_add) >= 2 and concepts_to_add[-1] < L_proj[L_proj.bottom]:
            concepts_to_add = [concepts_to_add[-1]] + concepts_to_add[:-1]

        for c in concepts_to_add:  # As, for now, ConceptLattice does not support addition of many elements at once
            L_proj.add(c)

        # Step i.4: Drop bad concepts from the lattice (if needed)
        if len(L_proj) > L_max:
            L_proj.calc_concepts_measures(measure_name, K_proj)
            measure_values = L_proj.measures[measure_name]
            thold = sorted(measure_values)[::-1][L_max]

            top_i, bottom_i = L_proj.top, L_proj.bottom
            concepts_to_remove = [i for i, v in enumerate(measure_values)
                                  if v <= thold and i != top_i and i != bottom_i]

            for c_i in concepts_to_remove[::-1]:
                del L_proj[c_i]

    return L_proj


def sofia_binary(
        K: FormalContext, L_max: int = 100,
        iterate_attributes: bool = True, measure: str = 'LStab',
        proj_sorting: str = None, proj_start: int = None, use_tqdm: bool = False):
    """Return a lattice of the most interesting concepts generated by SOFIA algorithm. Optimized for `FormalContext`

    WARNING: The author of the algorithm (A. Buzmakov) said this function is not an accurate implementation
    of the original Sofia algorithm. Thus the function may work not as efficient as expected.

    Parameters
    ----------
    K: `FormalContext`
        A context to build a list of concepts on
    L_max: `int`
        Maximum size of returned lattice. That is the maximum number of most interesting concepts
    iterate_attributes: `bool`
        A flag whether to iterate a set of attributes as a chain of projections (if set to True) or a set of objects o/w
    measure: `string`
        The name of a concept interesting measure_name to maximize
    proj_sorting: `str` of {'ascending', 'descending', 'random', None}
        A way to sort a chain of projections by their support.
        E.g. if ``iterate_attributes`` is set to True, 'Ascending' sorting start running projections
        from an attribute shared by the least amount of objects to an attributes shared by the most amount of objects
    proj_start: `int`
        A number of projection (a set of attributes/objects) to construct a basic `ConceptLattice` on
    use_tqdm: `bool`
        A flag whether to visualize the progress of the algorithm with `tqdm` bar or not

    Returns
    -------
    lattice: `ConceptLattice`
        A ConceptLattice which contains a set of Formal (or Pattern) concepts
        with high values of given interesting measure

    """
    def setup_projection_order(K_):
        max_proj_ = len(K_)
        if proj_sorting == 'ascending':
            def key_func(proj_i):
                return len(K_.intention_i([proj_i]))
        elif proj_sorting == 'descending':
            def key_func(proj_i):
                return -len(K_.intention_i([proj_i]))
        elif proj_sorting == 'random':
            rand_idxs = random.sample(range(max_proj_), k=max_proj_)

            def key_func(proj_i):
                return rand_idxs[proj_i]
        elif proj_sorting is None:
            key_func = None
        else:
            raise ValueError(f'Sofia_binary error. Unknown proj_sorting is given: {proj_sorting}. ' +
                             'Possible ones are "ascending", "descending", "random"')

        order = range(max_proj_)
        if key_func:
            order = sorted(order, key=key_func)
        return order

    def setup_measure(measure_):
        if not isinstance(measure_, str):
            raise TypeError('Sofia_binary error. For now, you can only specify the name of already defined measure')
        return measure_

    if iterate_attributes is None:
        iterate_attributes = len(K.attribute_names) < len(K.object_names)

    K_hash = K.hash_fixed()
    if iterate_attributes:
        K = K.T

    proj_order = setup_projection_order(K)
    measure_name = setup_measure(measure)

    L = sofia_objectwise(K[proj_order], L_max, measure_name=measure_name, use_tqdm=use_tqdm, proj_start=proj_start)

    if iterate_attributes:
        L = L.T

    for i in range(len(L)):
        c = L[i]
        c_new = deepcopy(L[i])
        c_new._context_hash = K_hash
        L._update_element(c, c_new)

    return L


def sofia_general(K: MVContext, L_max=100, measure='LStab', proj_to_start=None, use_tqdm=False):
    """Return a lattice of the most interesting concepts generated by SOFIA algorithm. Can work with any `MVContext`

    WARNING: The author of the algorithm (A. Buzmakov) said this is not an accurate implementation
    of the original Sofia algorithm. Thus, the function may work not as efficient as expected.
    Moreover, it represents the simplest way to construct a lattice over MVContext. Therefore, it is very inefficient.

    Parameters
    ----------
    K: `FormalContext` or `MVContext`
        A context to build a list of concepts on
    L_max: `int`
        Maximum size of returned lattice. That is the maximum number of most interesting concepts
    measure: `string`
        The name of a concept interesting measure to maximize
    proj_to_start: `int`
        A number of projection (a set of attributes/objects) to construct a basic `ConceptLattice` on
    use_tqdm: `bool`
        A flag whether to visualize the progress of the algorithm with `tqdm` bar or not

    Returns
    -------
    lattice: `ConceptLattice`
        A ConceptLattice which contains a set of Formal (or Pattern) concepts
        with high values of given interesting measure

    """
    return sofia_objectwise(K, L_max, measure, use_tqdm, proj_to_start)


def parse_decision_tree_to_extents(tree, X, n_jobs=1):
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
    return exts


def random_forest_concepts(context: MVContext, rf_params=None, rf_class=None):
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

    rf_params = rf_params if rf_params is not None else {}

    X = context.to_numeric()[0]
    Y = context.target

    if rf_class is None:
        rf_class = RandomForestClassifier if len(set(Y)) == 2 else RandomForestRegressor

    rf = rf_class(**rf_params)
    rf.fit(X, Y)
    extents_i = parse_decision_tree_to_extents(rf, X)
    extents_i.append(context.extension_i(context.intention_i([])))

    concepts = []

    object_names = context.object_names
    context_hash = context.hash_fixed()
    for extent_i in extents_i:
        extent = [object_names[g_i] for g_i in extent_i]
        intent_i = context.intention_i(extent_i)
        if type(context) == FormalContext:
            intent = [context.attribute_names[m_i] for m_i in intent_i]
            concept = FormalConcept(extent_i, extent, intent_i, intent, context_hash=context_hash)
        else:
            intent = {context.pattern_structures[ps_i].name: description for ps_i, description in intent_i.items()}
            concept = PatternConcept(extent_i, extent, intent_i, intent,
                                     context.pattern_types, context.attribute_names, context_hash=context_hash)
        concepts.append(concept)

    return concepts


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
