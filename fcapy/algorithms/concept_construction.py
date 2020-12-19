from fcapy.context import FormalContext
from fcapy.lattice.formal_concept import FormalConcept


def close_by_one(context: FormalContext, output_as_concepts=True, iterate_extents=None):
    if iterate_extents is None:
        iterate_extents = context.n_objects < context.n_attributes
    n_iters = context.n_objects if iterate_extents else context.n_attributes

    itersets_i_dict = {}  # extents dict if iterate over objects, intents dict if iterate over attributes
    sidesets_i = []  # intents if iterate over objects, extents if iterate over attributes
    combinations_to_check = [[]]  # subsets of objects if iterate over objects, subsets of attributes otherwise

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

