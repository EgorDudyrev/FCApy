from fcapy.context import FormalContext
from fcapy.lattice.formal_concept import FormalConcept
import random


def close_by_one(context: FormalContext, output_as_concepts=True, iterate_extents=None,
                 initial_combinations=None, iter_elements_to_check=None):
    if initial_combinations is not None:
        assert iterate_extents is not None,\
            "`iterate_extents parameter should be specified if initial_combinations are given " \
            "(`True if initial_combinations are extents, `False if inital_combinations are intents)"

    if iter_elements_to_check is not None:
        assert iterate_extents is not None, \
            "`iterate_extents parameter should be specified if iter_elements_to_check are given " \
            "(`True if iter_elements_to_check are objects, `False if iter_elements_to_check are attributes)"

    if iterate_extents is None:
        iterate_extents = context.n_objects < context.n_attributes
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

    lattice = None

    for projection_num in range(1, max_projection + 1):
        if iterate_attributes:
            ctx_projected = context.from_pandas(ds.iloc[:, projections_order[:projection_num]])
        else:
            ctx_projected = context.from_pandas(ds.iloc[projections_order[:projection_num]])

        new_concepts = close_by_one(
            ctx_projected, output_as_concepts=True,
            iterate_extents=not iterate_attributes,
            initial_combinations=itersets.copy(),
            iter_elements_to_check=[projection_num-1]
        )
        if len(new_concepts) > L_max:
            if lattice is None:
                subconcepts_dict = lca.complete_comparison(new_concepts)
                lattice = ConceptLattice(new_concepts, subconcepts_dict=subconcepts_dict)
            else:
                # concepts that were changed during projection iteration
                concepts_delta = set(new_concepts) - set(concepts)
                # find concepts which were just 'expanded' to the new projection
                old_sidesets = {c.extent_i if iterate_attributes else c.intent_i: c_i
                                for c_i, c in enumerate(concepts)}
                concepts_delta_same_sidesets = {
                    c for c in concepts_delta
                    if (c.extent_i if iterate_attributes else c.intent_i) in old_sidesets}
                for c in concepts_delta_same_sidesets:
                    sideset = c.extent_i if iterate_attributes else c.intent_i
                    lattice._concepts[old_sidesets[sideset]] = c

                # find completely new concepts created while projection iteration
                # sort concepts to ensure there will be no moment with multiple top or bottom concepts
                concepts_to_add = lattice.sort_concepts(concepts_delta - concepts_delta_same_sidesets)
                concepts_to_add = [concepts_to_add[0], concepts_to_add[-1]] + concepts_to_add[1:-1]
                for c in concepts_to_add:
                    lattice.add_concept(c)

            lattice.calc_concepts_measures(measure)
            metrics = [c.measures[measure] for c_i, c in enumerate(lattice.concepts)]
            metrics_lim = sorted(metrics)[-L_max]
            concepts = [c for c, m in zip(lattice.concepts, metrics) if m > metrics_lim]
        else:
            concepts = new_concepts
        itersets = [c.intent_i if iterate_attributes else c.extent_i for c in concepts]

    return concepts


def sofia_general(context, L_max=100, measure='LStab'):
    concepts = sofia_binary(context, L_max=L_max, iterate_attributes=False, measure=measure)
    return concepts
