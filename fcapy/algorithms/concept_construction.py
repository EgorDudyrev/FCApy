from fcapy.context import FormalContext
from fcapy.mvcontext.mvcontext import MVContext
from fcapy.lattice.formal_concept import FormalConcept
from fcapy.lattice.pattern_concept import PatternConcept
from ..utils import utils
import random
from copy import deepcopy
import math


def close_by_one(context: MVContext, output_as_concepts=True, iterate_extents=None,
                 initial_combinations=None, iter_elements_to_check=None):
    if iterate_extents is False:
        assert type(context) == FormalContext, "Can set iterate_extents=False only if FormalContext is given"

    if initial_combinations is not None:
        assert iterate_extents is not None,\
            "`iterate_extents parameter should be specified if initial_combinations are given " \
            "(`True if initial_combinations are extents, `False if inital_combinations are intents)"

    if iter_elements_to_check is not None:
        assert iterate_extents is not None, \
            "`iterate_extents parameter should be specified if iter_elements_to_check are given " \
            "(`True if iter_elements_to_check are objects, `False if iter_elements_to_check are attributes)"

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

    iter_elements_to_check = list(range(n_iters)) if iter_elements_to_check is None else iter_elements_to_check

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
        for g_i in iter_elements_to_check:
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
        context_hash = hash(context)

        concepts = []
        for concept_data in zip(extents_i, intents_i):
            extent_i, intent_i = concept_data
            extent = [object_names[g_i] for g_i in extent_i]
            if type(context) == FormalContext:
                intent = [attribute_names[m_i] for m_i in intent_i]
                concept = FormalConcept(extent_i, extent, intent_i, intent, context_hash=context_hash)
            else:
                intent = {context.pattern_structures[ps_i].name: description for ps_i, description in intent_i.items()}
                concept = PatternConcept(extent_i, extent, intent_i, intent, context.pattern_types,
                                         context_hash=context_hash)
            concepts.append(concept)
        return concepts

    data = {'extents_i': extents_i, 'intents_i': intents_i}
    return data


def sofia_binary(context: MVContext, L_max=100, iterate_attributes=True, measure='LStab',
                 projection_sorting=None, proj_to_start=None, use_tqdm=False):
    assert not (iterate_attributes and type(context) != FormalContext),\
        "Sofia_binary error. " +\
        "Cannot iterate_attributes if given context is of type FormalContext"

    if iterate_attributes:
        assert type(context) == FormalContext, "Can only iterate_attributes if FormalContext is given"

    from fcapy.algorithms import lattice_construction as lca
    from fcapy.lattice import ConceptLattice

    max_projection = context.n_attributes if iterate_attributes else context.n_objects
    projections_order = list(range(max_projection))

    if projection_sorting in {'ascending', 'descending'}:
        def key_fnc(i):
            v = len(context.extension_i([i]) if iterate_attributes else context.intention_i([i]))
            if projection_sorting == 'descending':
                v = -v
            return v
        projections_order = sorted(projections_order, key=key_fnc)
    elif projection_sorting == 'random':
        projections_order = random.sample(range(max_projection), k=max_projection)
    elif projection_sorting is not None:
        raise ValueError(f'Sofia_binary error. Unknown projection_sorting is given: {projection_sorting}. ' +
                         'Possible ones are "ascending", "descending", "random"')

    proj_to_start = int(math.log2(L_max)) if proj_to_start is None else proj_to_start
    if iterate_attributes:
        ctx_projected = context[:, projections_order[:proj_to_start]]
    else:
        ctx_projected = context[projections_order[:proj_to_start]]
    concepts = close_by_one(ctx_projected, output_as_concepts=True, iterate_extents=not iterate_attributes)
    subconcepts_dict = lca.complete_comparison(concepts)
    lattice = ConceptLattice(concepts, subconcepts_dict=subconcepts_dict)

    # itersets - iteration sets - set of attributes or objects (depends on iterate_attributes)
    itersets = [c.intent_i if iterate_attributes else c.extent_i for c in lattice._concepts]

    for projection_num in utils.safe_tqdm(range(proj_to_start+1, max_projection + 1),
                                          desc='SOFIA: Iterate projections', disable=not use_tqdm):
        if iterate_attributes:
            ctx_projected = context[:, projections_order[:projection_num]]
        else:
            ctx_projected = context[projections_order[:projection_num]]

        new_concepts = close_by_one(
            ctx_projected, output_as_concepts=True,
            iterate_extents=not iterate_attributes,
            initial_combinations=deepcopy(itersets),
            iter_elements_to_check=[projection_num-1]
        )

        # make the concepts comparable
        ctx_projected_hash = hash(ctx_projected)
        for c in lattice._concepts:
            c._context_hash = ctx_projected_hash

        # concepts that were changed during projection iteration
        concepts_delta = set(new_concepts) - set(lattice._concepts)
        # find concepts which were just 'expanded' to the new projection:
        # their "iterset" is changed but "sideset" is the same (see the notation described in close_by_one)
        old_sidesets = {c.extent_i if iterate_attributes else c.intent_i: c_i
                        for c_i, c in enumerate(lattice._concepts)}
        concepts_delta_same_sidesets = {
            c for c in concepts_delta
            if (c.extent_i if iterate_attributes else c.intent_i) in old_sidesets}
        for c in concepts_delta_same_sidesets:
            sideset = c.extent_i if iterate_attributes else c.intent_i
            c_i = old_sidesets[sideset]
            lattice._concepts[c_i] = c

        top_concept_i, bottom_concept_i = ConceptLattice.get_top_bottom_concepts_i(lattice._concepts)

        # find completely new concepts created while projection iteration
        # sort concepts to ensure there will be no moment with multiple top or bottom concepts
        concepts_to_add = lattice.sort_concepts(concepts_delta - concepts_delta_same_sidesets)
        if len(concepts_to_add) >= 2 and concepts_to_add[-1] < lattice._concepts[bottom_concept_i]:
            concepts_to_add = [concepts_to_add[-1]] + concepts_to_add[:-1]
        for c_i, c in enumerate(concepts_to_add):
            lattice.add_concept(c)

        if len(lattice.concepts) > L_max:
            lattice.calc_concepts_measures(measure)
            metrics = [c.measures[measure] for c_i, c in enumerate(lattice.concepts)]
            metrics_lim = sorted(metrics)[-L_max-1]
            concepts_to_remove = [i for i in range(len(lattice.concepts)) if metrics[i] <= metrics_lim][::-1]
            concepts_to_remove = [i for i in concepts_to_remove
                                  if i not in [lattice.top_concept_i, lattice.bottom_concept_i]]
            for c_i in concepts_to_remove:
                lattice.remove_concept(c_i)

        itersets = [c.intent_i if iterate_attributes else c.extent_i for c in lattice._concepts]
    return lattice


def sofia_general(context: MVContext, L_max=100, measure='LStab', proj_to_start=None, use_tqdm=False):
    lattice = sofia_binary(
        context,
        L_max=L_max, iterate_attributes=False, measure=measure, proj_to_start=proj_to_start,
        use_tqdm=use_tqdm
    )
    return lattice


def parse_decision_tree_to_extents(tree, X, n_jobs=1):
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
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

    rf_params = rf_params if rf_params is not None else {}

    X = context.data.copy()
    # TODO: Add support of categorical features
    # if type(context) is MVContext:
    #     for f_idx in context._cat_attrs_idxs:
    #         if len(set(X[:, f_idx])) <= 10:
    #             for v in np.unique(X[:, f_idx]):
    #                 X = np.hstack((X, (X[:, f_idx] == v).reshape(-1, 1)))
    #         else:
    #             le = LabelEncoder()
    #             X = np.hstack((X, le.fit_transform(X[:, f_idx]).reshape(-1, 1)))
    # X = X[:, [idx for idx in range(X.shape[1]) if idx not in context._cat_attrs_idxs]]

    Y = context.target

    if rf_class is None:
        rf_class = RandomForestClassifier if len(set(Y)) == 2 else RandomForestRegressor

    rf = rf_class(**rf_params)
    rf.fit(X, Y)
    extents_i = parse_decision_tree_to_extents(rf, X)
    extents_i.append(context.extension_i(context.intention_i([])))

    concepts = []

    object_names = context.object_names
    context_hash = hash(context)
    for extent_i in extents_i:
        extent = [object_names[g_i] for g_i in extent_i]
        intent_i = context.intention_i(extent_i)
        if type(context) == FormalContext:
            intent = [context.attribute_names[m_i] for m_i in intent_i]
            concept = FormalConcept(extent_i, extent, intent_i, intent, context_hash=context_hash)
        else:
            intent = {context.pattern_structures[ps_i].name: description for ps_i, description in intent_i.items()}
            concept = PatternConcept(extent_i, extent, intent_i, intent, context.pattern_types,
                                     context_hash=context_hash)
        concepts.append(concept)

    return concepts
