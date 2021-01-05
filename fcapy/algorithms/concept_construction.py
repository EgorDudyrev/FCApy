from fcapy.context import FormalContext
from fcapy.lattice.formal_concept import FormalConcept
import random


def close_by_one(context: FormalContext, output_as_concepts=True, iterate_extents=None, initial_combinations=None):
    if iterate_extents is None:
        iterate_extents = context.n_objects < context.n_attributes
    n_iters = context.n_objects if iterate_extents else context.n_attributes

    # <iterset> - iterating set - the set of object if one construct construct concepts while iterating over objects,
    #   the set of attributes otherwise
    # <sideset> - the other set, "sided" with <iterset>.
    #   If <iterset> is the set of objects then <sideset> is the set of attributes and vice versa
    itersets_i_dict = {}
    sidesets_i = []
    combinations_to_check = initial_combinations if initial_combinations is not None else [[]]

    iterset_fnc, sideset_fnc = context.extension_i, context.intention_i
    if not iterate_extents:
        iterset_fnc, sideset_fnc = sideset_fnc, iterset_fnc

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
        new_combs = [iterset_i + [g_i]
                     for g_i in range(comb_i[-1]+1 if len(comb_i) > 0 else 0, n_iters)
                     if g_i not in iterset_i]
        combinations_to_check = new_combs + combinations_to_check

    itersets_i = list({idx: x_i for x_i, idx in itersets_i_dict.items()}.values())

    extents_i, intents_i = itersets_i, sidesets_i
    if not iterate_extents:
        extents_i, intents_i = intents_i, extents_i

    if output_as_concepts:
        object_names = context.object_names
        attribute_names = context.attribute_names

        concepts = []
        for concept_data in zip(extents_i, intents_i):
            extent_i, intent_i = concept_data
            extent = [object_names[g_i] for g_i in extent_i]
            intent = [attribute_names[m_i] for m_i in intent_i]
            concepts.append(FormalConcept(extent_i, extent, intent_i, intent))
        return concepts

    data = {'extents_i': extents_i, 'intents_i': intents_i}
    return data


def sofia_binary(context, L_max=100, iterate_attributes=True, measure='LStab', projection_sorting=None):
    assert not (iterate_attributes and type(context) != FormalContext),\
        "Sofia_binary error. " +\
        "Cannot iterate_attributes if given context is of type FormalContext"

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

    # itersets - iteration sets - set of attributes or objects (depends on iterate_attributes)
    itersets = [[]]
    ds = context.to_pandas()

    for projection_num in range(2, max_projection + 1):
        if iterate_attributes:
            ctx_projected = context.from_pandas(ds.iloc[:, projections_order[:projection_num]])
        else:
            ctx_projected = context.from_pandas(ds.iloc[projections_order[:projection_num]])

        new_concepts = close_by_one(
            ctx_projected, output_as_concepts=True,
            iterate_extents=not iterate_attributes, initial_combinations=itersets
        )
        if len(new_concepts) > L_max:
            subconcepts_dict = lca.complete_comparison(new_concepts)
            ltc_projected = ConceptLattice(new_concepts, subconcepts_dict=subconcepts_dict)
            ltc_projected.calc_concepts_measures(measure)
            metrics = [c.measures[measure] for c_i, c in enumerate(ltc_projected.concepts)]
            metrics_lim = sorted(metrics)[-L_max]
            concepts = [c for c, m in zip(ltc_projected.concepts, metrics) if m >= metrics_lim]
        else:
            concepts = new_concepts
        itersets = [c.intent_i if iterate_attributes else c.extent_i for c in concepts]

    return concepts


def sofia_general(context, L_max=100, measure='LStab'):
    concepts = sofia_binary(context, L_max=L_max, iterate_attributes=False, measure=measure)
    return concepts
