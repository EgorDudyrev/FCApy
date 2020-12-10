from fcapy.context import FormalContext
from fcapy.lattice.formal_concept import FormalConcept


def close_by_one(context: FormalContext, output_as_concepts=True):
    n_objects = context.n_objects

    extents_i_dict = {}
    intents_i = []

    combinations_to_check = [[]]
    while len(combinations_to_check) > 0:
        comb_i = combinations_to_check.pop(0)

        intent_i = context.intention_i(comb_i)
        extent_i = tuple(context.extension_i(intent_i))

        extent_i_new = sorted(set(extent_i)-set(comb_i))

        is_not_lexicographic = len(comb_i) > 0 and len(extent_i_new) > 0 and min(extent_i_new) < max(comb_i)
        is_duplicate = extent_i in extents_i_dict
        if any([is_not_lexicographic, is_duplicate]):
            continue

        extents_i_dict[extent_i] = len(intents_i)
        intents_i.append(intent_i)

        extent_i = list(extent_i)
        new_combs = [extent_i + [g_i]
                     for g_i in range(max(comb_i)+1 if len(comb_i) > 0 else 0, n_objects)
                     if g_i not in extent_i]
        combinations_to_check = new_combs + combinations_to_check

    extents_i = list({idx: extent_i for extent_i, idx in extents_i_dict.items()}.values())

    if output_as_concepts:
        object_names = context.object_names
        attribute_names = context.attribute_names

        concepts = set()
        for concept_data in zip(extents_i, intents_i):
            extent_i, intent_i = concept_data
            extent = [object_names[g_i] for g_i in extent_i]
            intent = [attribute_names[m_i] for m_i in intent_i]
            concepts.add(FormalConcept(extent_i, extent, intent_i, intent))
        return concepts

    return extents_i, intents_i
