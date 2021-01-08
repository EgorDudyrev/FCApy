from copy import deepcopy

# TODO: Remove all print statements

def complete_comparison(concepts, is_concepts_sorted=False, n_jobs=1):
    def get_subconcepts(a_i, a, concepts):
        subconcepts = set()
        for b_i, b in enumerate(concepts):
            if is_concepts_sorted:
                if b_i < a_i:
                    continue

            if b < a:
                subconcepts.add(b_i)
        return subconcepts

    if n_jobs == 1:
        all_subconcepts = [get_subconcepts(a_i, a, concepts) for a_i, a in enumerate(concepts)]
    else:
        from joblib import Parallel, delayed

        all_subconcepts = Parallel(n_jobs=n_jobs, require='sharedmem')(
            delayed(get_subconcepts)(a_i, a, concepts)
            for a_i, a in enumerate(concepts)
        )

    all_subconcepts_dict = {i: subconcepts for i, subconcepts in enumerate(all_subconcepts)}

    subconcepts_dict = {i: None for i in range(len(concepts))}
    for a_i, b_is in all_subconcepts_dict.items():
        subconcepts_dict[a_i] = b_is

        b_is = b_is.copy() if not is_concepts_sorted else sorted(b_is)
        for b_i in b_is:
            subconcepts_dict[a_i] -= all_subconcepts_dict[b_i]

    return subconcepts_dict


def construct_spanning_tree(concepts, is_concepts_sorted=False):
    from fcapy.lattice import ConceptLattice

    if not is_concepts_sorted:
        concepts_sorted = ConceptLattice.sort_concepts(concepts)
        map_concept_i = {c: c_i for c_i, c in enumerate(concepts)}

    subconcepts_st_dict = {}
    superconcepts_st_dict = {}

    for c_sort_i in range(len(concepts)):
        if is_concepts_sorted:
            c = concepts[c_sort_i]
            c_i = c_sort_i
        else:
            c = concepts_sorted[c_sort_i]
            c_i = map_concept_i[c]

        subconcepts_st_dict[c_i] = set()
        if c_sort_i == 0:
            superconcepts_st_dict[c_i] = []
            continue

        if is_concepts_sorted:
            superconcept = concepts[0]
            superconcept_i = 0
        else:
            superconcept = concepts_sorted[0]
            superconcept_i = map_concept_i[superconcept]

        sifted = True
        while sifted:
            for subconcept_i in subconcepts_st_dict[superconcept_i]:
                subconcept = concepts[subconcept_i]
                if c < subconcept:
                    superconcept_i = subconcept_i
                    break
            else:
                sifted = False

        subconcepts_st_dict[superconcept_i].add(c_i)
        superconcepts_st_dict[c_i] = {superconcept_i}

    return subconcepts_st_dict, superconcepts_st_dict


def construct_lattice_from_spanning_tree(concepts, sptree_chains, is_concepts_sorted=False):
    from ..lattice import ConceptLattice

    # initialize the dictionaries
    all_superconcepts, incomparables, superconcepts_dict, subconcepts_dict = [
        {c_i: set() for c_i in range(len(concepts))}
        for i in range(4)]

    # Sort concepts by size of extent: from the more general to more specific
    if not is_concepts_sorted:
        concepts_sorted = ConceptLattice.sort_concepts(concepts) if not is_concepts_sorted else concepts
        map_concept_i_sort = {c: c_i_sort for c_i_sort, c in enumerate(concepts_sorted)}
        map_i_isort = [map_concept_i_sort[concepts[c_i]] for c_i in range(len(concepts))]
    else:
        concepts_sorted, map_concept_i_sort, map_i_isort = [None] * 3

    # function to iterate through chains. Looking for superconcepts of the current concept
    def iterate_chain(
            chain_comp, c_i_cur, idx_comp_start, concepts,
            superconcepts_cur, all_superconcepts_cur, incomparables_cur,
            is_concepts_sorted=is_concepts_sorted, map_i_isort=map_i_isort
    ):
        for idx_comp, c_i_comp in enumerate(chain_comp[idx_comp_start:]):
            idx_comp += idx_comp_start
            if c_i_comp in all_superconcepts_cur:
                continue

            has_smaller_i = map_i_isort[c_i_comp] < map_i_isort[c_i_cur] \
                if not is_concepts_sorted else c_i_comp < c_i_cur

            # if at last concepts in the chain it is superconcept
            last_in_chain = idx_comp == len(chain_comp) - 1

            # if stepped on the concept in chain which is not subconcept
            if c_i_comp in incomparables_cur:
                is_superconcept = False
            else:
                c_comp = concepts[c_i_comp]
                is_superconcept = c_comp > c_cur if has_smaller_i else False
                if has_smaller_i and not is_superconcept:
                    incomparables_cur.add(c_i_comp)

            if is_superconcept and last_in_chain:
                superconcepts_cur |= {c_i_comp}
                idx_comp_start = idx_comp
                all_superconcepts_cur.add(c_i_comp)
                break

            if not is_superconcept:
                superconcept_i_comp = chain_comp[idx_comp - 1]

                superconcepts_cur |= {superconcept_i_comp}
                idx_comp_start = idx_comp
                break

            all_superconcepts_cur.add(c_i_comp)
        return superconcepts_cur, all_superconcepts_cur, incomparables_cur, idx_comp_start

        # iterate through every chain. If new concept in the chain is found: select its superconcepts and subconcepts
    for ch_i_cur in range(len(sptree_chains)):
        # start comparison of current concept and concepts from chain `ch_i from idxs_comp[ch_i]
        idxs_comp = [0] * len(sptree_chains)
        # iterate through every concept in the chain. Except the very first one (it is the lattice top concept)
        for idx_cur, c_i_cur in enumerate(sptree_chains[ch_i_cur][1:]):
            idx_cur += 1  # position of current concept in the chain should start with 1
            c_cur = concepts[c_i_cur]
            if len(superconcepts_dict[c_i_cur]) > 0:
                # if superconcepts of current concept are already found
                continue

            superconcept_i_cur = sptree_chains[ch_i_cur][idx_cur - 1]
            superconcepts_dict[c_i_cur] = {superconcept_i_cur}
            all_superconcepts[c_i_cur] |= {superconcept_i_cur} | all_superconcepts[superconcept_i_cur]

            for ch_i_comp, chain_comp in enumerate(sptree_chains):
                output = iterate_chain(
                    chain_comp, c_i_cur, idxs_comp[ch_i_comp], concepts,
                    superconcepts_dict[c_i_cur], all_superconcepts[c_i_cur], incomparables[c_i_cur]
                )

                superconcepts_cur, all_superconcepts_cur, incomparables_cur, idx_comp_start = output
                superconcepts_dict[c_i_cur] |= superconcepts_cur
                all_superconcepts[c_i_cur] |= all_superconcepts_cur
                incomparables[c_i_cur] |= incomparables_cur
                idxs_comp[ch_i_comp] = idx_comp_start

    for c_i, c in enumerate(concepts):
        def sort_key(sc_i):
            return -map_i_isort[sc_i] if not is_concepts_sorted else -sc_i
        superconcepts = sorted(superconcepts_dict[c_i], key=lambda sc_i: sort_key(sc_i))
        for idx in range(len(superconcepts)):
            if idx >= len(superconcepts):
                break

            sc_i = superconcepts[idx]
            superconcepts = [i for i in superconcepts if i not in all_superconcepts[sc_i]]
        superconcepts_dict[c_i] = superconcepts
        for superconcept_i in superconcepts_dict[c_i]:
            subconcepts_dict[superconcept_i].add(c_i)
    return subconcepts_dict


def construct_lattice_from_spanning_tree_parallel(concepts, sptree_chains, is_concepts_sorted=False, n_jobs=1):
    from ..lattice import ConceptLattice

    # initialize the dictionaries
    all_superconcepts, incomparables, superconcepts_dict, subconcepts_dict = [
        {c_i: set() for c_i in range(len(concepts))}
        for i in range(4)]

    # Sort concepts by size of extent: from the more general to more specific
    if not is_concepts_sorted:
        concepts_sorted = ConceptLattice.sort_concepts(concepts) if not is_concepts_sorted else concepts
        map_concept_i_sort = {c: c_i_sort for c_i_sort, c in enumerate(concepts_sorted)}
        map_i_isort = [map_concept_i_sort[concepts[c_i]] for c_i in range(len(concepts))]
    else:
        concepts_sorted, map_concept_i_sort, map_i_isort = [None] * 3

    # function to iterate through chains. Looking for superconcepts of the current concept
    def iterate_chain(
            chain_comp, c_i_cur, idx_comp_start, concepts,
            superconcepts_cur, all_superconcepts_cur, incomparables_cur,
            is_concepts_sorted=is_concepts_sorted, map_i_isort=map_i_isort
    ):
        for idx_comp, c_i_comp in enumerate(chain_comp[idx_comp_start:]):
            idx_comp += idx_comp_start
            if c_i_comp in all_superconcepts_cur:
                continue

            has_smaller_i = map_i_isort[c_i_comp] < map_i_isort[c_i_cur] \
                if not is_concepts_sorted else c_i_comp < c_i_cur

            # if at last concepts in the chain it is superconcept
            last_in_chain = idx_comp == len(chain_comp) - 1

            # if stepped on the concept in chain which is not subconcept
            if c_i_comp in incomparables_cur:
                is_superconcept = False
            else:
                c_comp = concepts[c_i_comp]
                is_superconcept = c_comp > c_cur if has_smaller_i else False
                if has_smaller_i and not is_superconcept:
                    incomparables_cur.add(c_i_comp)

            if is_superconcept and last_in_chain:
                superconcepts_cur |= {c_i_comp}
                idx_comp_start = idx_comp
                all_superconcepts_cur.add(c_i_comp)
                break

            if not is_superconcept:
                superconcept_i_comp = chain_comp[idx_comp - 1]

                superconcepts_cur |= {superconcept_i_comp}
                idx_comp_start = idx_comp
                break

            all_superconcepts_cur.add(c_i_comp)
        return superconcepts_cur, all_superconcepts_cur, incomparables_cur, idx_comp_start

        # iterate through every chain. If new concept in the chain is found: select its superconcepts and subconcepts
    if n_jobs == 1:
        class NullContextManager(object):
            def __init__(self, dummy_resource=None):
                self.dummy_resource = dummy_resource
            def __enter__(self):
                return self.dummy_resource
            def __exit__(self, *args):
                pass

        parallel_manager = NullContextManager(lambda x: x)
    else:
        from joblib import Parallel, delayed
        parallel_manager = Parallel(n_jobs=n_jobs, backend="threading", require='sharedmem')
        iterate_chain = delayed(iterate_chain)

    with parallel_manager as pm:
        for ch_i_cur in range(len(sptree_chains)):
            # start comparison of current concept and concepts from chain `ch_i from idxs_comp[ch_i]
            idxs_comp = [0] * len(sptree_chains)
            # iterate through every concept in the chain. Except the very first one (it is the lattice top concept)
            for idx_cur, c_i_cur in enumerate(sptree_chains[ch_i_cur][1:]):
                idx_cur += 1  # position of current concept in the chain should start with 1
                c_cur = concepts[c_i_cur]
                if len(superconcepts_dict[c_i_cur]) > 0:
                    # if superconcepts of current concept are already found
                    continue

                superconcept_i_cur = sptree_chains[ch_i_cur][idx_cur - 1]
                superconcepts_dict[c_i_cur] = {superconcept_i_cur}
                all_superconcepts[c_i_cur] |= {superconcept_i_cur} | all_superconcepts[superconcept_i_cur]

                assert n_jobs == -1 or n_jobs >= 1, \
                    f"construct_lattice_from_spanning_tree error. only n_jobs>=1 or -1 are supported ({n_jobs} given)"
                max_n_jobs = pm._effective_n_jobs() if n_jobs > 1 else 1

                for chain_set_i in range(len(sptree_chains) // max_n_jobs):
                    min_chain_i = max_n_jobs * chain_set_i
                    chain_subset = tuple(sptree_chains[min_chain_i: min_chain_i + max_n_jobs])
                    outputs = pm(
                        iterate_chain(
                            chain_comp, c_i_cur, idxs_comp[ch_i_comp + min_chain_i], concepts,
                            superconcepts_dict[c_i_cur], all_superconcepts[c_i_cur], incomparables[c_i_cur]
                        ) for ch_i_comp, chain_comp in enumerate(chain_subset)
                    )
                    for ch_i_comp, output in enumerate(outputs):
                        superconcepts_cur, all_superconcepts_cur, incomparables_cur, idx_comp_start = output
                        superconcepts_dict[c_i_cur] |= superconcepts_cur
                        all_superconcepts[c_i_cur] |= all_superconcepts_cur
                        incomparables[c_i_cur] |= incomparables_cur
                        idxs_comp[ch_i_comp] = idx_comp_start

    for c_i, c in enumerate(concepts):
        def sort_key(sc_i):
            return -map_i_isort[sc_i] if not is_concepts_sorted else -sc_i
        superconcepts = sorted(superconcepts_dict[c_i], key=lambda sc_i: sort_key(sc_i))
        for idx in range(len(superconcepts)):
            if idx >= len(superconcepts):
                break

            sc_i = superconcepts[idx]
            superconcepts = [i for i in superconcepts if i not in all_superconcepts[sc_i]]
        superconcepts_dict[c_i] = superconcepts
        for superconcept_i in superconcepts_dict[c_i]:
            subconcepts_dict[superconcept_i].add(c_i)
    return subconcepts_dict


def construct_lattice_by_spanning_tree(concepts, is_concepts_sorted=False, n_jobs=1):
    from ..lattice import ConceptLattice
    subconcepts_st_dict, superconcepts_st_dict = \
        construct_spanning_tree(concepts, is_concepts_sorted=is_concepts_sorted)
    chains = ConceptLattice._get_chains(concepts, superconcepts_st_dict, is_concepts_sorted=is_concepts_sorted)
    if n_jobs == 1:
        subconcepts_dict = construct_lattice_from_spanning_tree(concepts, chains, is_concepts_sorted=is_concepts_sorted)
    else:
        subconcepts_dict = construct_lattice_from_spanning_tree_parallel(
            concepts, chains, is_concepts_sorted=is_concepts_sorted, n_jobs=n_jobs)
    return subconcepts_dict


def add_concept(new_concept, concepts, subconcepts_dict, superconcepts_dict,
                top_concept_i=None, bottom_concept_i=None,
                inplace=True, verbose=False):
    assert new_concept not in concepts, "add_concept error. New concept is already in the concepts list"
    assert len(concepts) >= 2, 'add_concept error. Concepts list should contain both top and bottom concepts'

    if not inplace:
        concepts = deepcopy(concepts)
        subconcepts_dict = deepcopy(subconcepts_dict)
        superconcepts_dict = deepcopy(superconcepts_dict)

    new_concept_i = len(concepts)

    # top/bottom indices are considered weird
    # if new concept is bigger than top concept or smaller than the bottom concept
    # in this situation it is better to double check these indices
    def are_top_bottom_indices_weird():
        return new_concept > concepts[top_concept_i] or new_concept < concepts[bottom_concept_i]
    if top_concept_i is None or bottom_concept_i is None or are_top_bottom_indices_weird():
        from ..lattice import ConceptLattice
        if verbose:
            print(f'Fix top bottom concepts from {top_concept_i}, {bottom_concept_i}')
        top_concept_i, bottom_concept_i = ConceptLattice.get_top_bottom_concepts_i(concepts)
        if verbose:
            print(f'To {top_concept_i}, {bottom_concept_i}')
            if top_concept_i is None or concepts[top_concept_i] > new_concept:
                print(
                    f'WARNING. Top concept is ill defined. '
                    f'Concepts extents are: {[c.extent_i for c in concepts]}\n'
                    f'Concepts intents are: {[c.intent_i for c in concepts]}\n'
                    f'New concept: {new_concept.extent_i}; {new_concept.intent_i}'
                )
            if bottom_concept_i is None or concepts[bottom_concept_i] < new_concept:
                print(
                    f'WARNING. Bottom concept is ill defined.\n'
                    f'Concepts extents are: {[c.extent_i for c in concepts]}\n'
                    f'Concepts intents are: {[c.intent_i for c in concepts]}\n'
                    f'New concept: {new_concept.extent_i}; {new_concept.intent_i}'
                )

    assert top_concept_i is not None and bottom_concept_i is not None,\
        "add_concept error. Concepts list should always have one single top concept and one single bottom concept"

    if verbose:
        print(f'Top concept idx: {top_concept_i}, bottom concept idx: {bottom_concept_i}')

    if new_concept > concepts[top_concept_i]:
        if verbose:
            print('INFO. New concept is bigger than the top one')
        direct_superconcepts = set()
        direct_subconcepts = {top_concept_i}
        top_concept_i = new_concept_i
    elif new_concept < concepts[bottom_concept_i]:
        if verbose:
            print('INFO. New concept is smaller than the bottom one')
        direct_superconcepts = {bottom_concept_i}
        direct_subconcepts = set()
        bottom_concept_i = new_concept_i
    else:
        # find direct superconcepts
        if verbose:
            print('n concepts:', len(concepts))
            print('Top concept:', top_concept_i)
        concepts_to_visit = [top_concept_i]
        visited_concepts = set()
        direct_superconcepts = set()
        while len(concepts_to_visit) > 0:
            c_i = concepts_to_visit.pop(0)
            visited_concepts.add(c_i)

            subconcepts = {subc_i for subc_i in subconcepts_dict[c_i]
                           if new_concept < concepts[subc_i]}
            if len(subconcepts) > 0:
                concepts_to_visit += list(subconcepts - visited_concepts)
            else:
                direct_superconcepts.add(c_i)
        if verbose:
            print('Direct superconcepts:', direct_superconcepts)

        # find direct subconcepts
        if verbose:
            print("Start looking for subconcepts")
        concepts_to_visit = [bottom_concept_i]
        if verbose:
            print(f'Concepts_to_visit: {concepts_to_visit}')
        visited_concepts = set()
        direct_subconcepts = set()
        while len(concepts_to_visit) > 0:
            c_i = concepts_to_visit.pop(0)
            visited_concepts.add(c_i)
            if verbose:
                print(f'Looking at concepts {c_i}')
            superconcepts = {supc_i for supc_i in superconcepts_dict[c_i]
                             if new_concept > concepts[supc_i]}
            if verbose:
                print(f'Superconcepts are: {superconcepts}')
            if len(superconcepts) > 0:
                concepts_to_visit += list(superconcepts - visited_concepts)
            else:
                direct_subconcepts.add(c_i)
            if verbose:
                print(f'Concepts to visit: {concepts_to_visit}')
        if verbose:
            print('Direct subconcepts:', direct_subconcepts)
            print('Bottom concept:', bottom_concept_i)

    # for every pair of superconcept-subconcept put new concept in a line
    for supc_i in direct_superconcepts:
        subconcepts_dict[supc_i] -= direct_subconcepts
        subconcepts_dict[supc_i] |= {new_concept_i}
    for subc_i in direct_subconcepts:
        superconcepts_dict[subc_i] -= direct_superconcepts
        superconcepts_dict[subc_i] |= {new_concept_i}

    concepts.append(new_concept)
    superconcepts_dict[new_concept_i] = direct_superconcepts
    subconcepts_dict[new_concept_i] = direct_subconcepts

    if verbose:
        print(f'NEW Top concept idx: {top_concept_i}, bottom concept idx: {bottom_concept_i}')
        print('INFO. New concept is successfully added\n')

    return concepts, subconcepts_dict, superconcepts_dict, top_concept_i, bottom_concept_i


def remove_concept(concept_i, concepts, subconcepts_dict, superconcepts_dict,
                   top_concept_i=None, bottom_concept_i=None,
                   inplace=True, verbose=True):
    from ..lattice import ConceptLattice

    assert concept_i < len(concepts), f"remove_concept error. There is no concept {concept_i} in a concepts list"
    assert len(concepts) >= 3,\
        "remove_concept error. " \
        "Concept list should be at least of size 3 (so there will still be top and bottom concepts)"

    if not inplace:
        concepts = deepcopy(concepts)
        subconcepts_dict = deepcopy(subconcepts_dict)
        superconcepts_dict = deepcopy(superconcepts_dict)

    if top_concept_i is None or bottom_concept_i is None \
            or concepts[concept_i] > concepts[top_concept_i] or concepts[concept_i] < concepts[bottom_concept_i]:
        from ..lattice import ConceptLattice
        top_concept_i, bottom_concept_i = ConceptLattice.get_top_bottom_concepts_i(concepts)

    superconcepts = superconcepts_dict[concept_i]
    subconcepts = subconcepts_dict[concept_i]

    if concept_i == top_concept_i:
        top_concept_i = list(subconcepts)[0] if len(subconcepts) == 1 else None
        assert top_concept_i is not None, "Cannot remove the top concept of the lattice"
    elif concept_i == bottom_concept_i:
        bottom_concept_i = list(superconcepts)[0] if len(superconcepts) == 1 else None
        assert bottom_concept_i is not None, "Cannot remove the bottom concept of the lattice"
    else:
        pass
    # find all subconcepts of current superconcepts to drop transitive relations
    all_superconcepts = ConceptLattice.get_all_superconcepts_dict(concepts, superconcepts_dict)
    all_subconcepts = ConceptLattice.get_all_subconcepts_dict(concepts, subconcepts_dict)

    if verbose:
        print(f'START removing concept {concept_i}')
        print(f'INFO. Superconcepts are: {superconcepts}')
        print(f'INFO. Subconcepts are: {subconcepts}')
    for supc_i in superconcepts:
        subconcepts_dict[supc_i] -= {concept_i}
        subconcepts_dict[supc_i] |= subconcepts
        subconcepts_ = sorted(subconcepts_dict[supc_i], key=lambda c_i: -concepts[c_i].support)
        for c_i in subconcepts_:
            if c_i not in subconcepts_dict[supc_i]:
                continue
            subconcepts_dict[supc_i] -= all_subconcepts[c_i]
    for subc_i in subconcepts:
        superconcepts_dict[subc_i] -= {concept_i}  # |all_superconcepts[concept_i]
        superconcepts_dict[subc_i] |= superconcepts - {subc_i}  # -all_superconcepts[subc_i]#-{subc_i}
        superconcepts_ = sorted(superconcepts_dict[subc_i], key=lambda c_i: concepts[c_i].support)
        for c_i in superconcepts_:
            if c_i not in superconcepts_dict[subc_i]:
                continue
            superconcepts_dict[subc_i] -= all_superconcepts[c_i]

    del concepts[concept_i]
    del superconcepts_dict[concept_i]
    del subconcepts_dict[concept_i]

    # update concept indices
    def decrement(c_i, threshold):
        return c_i - 1 if c_i >= threshold else c_i
    for c_i in range(len(concepts) + 1):
        if c_i == concept_i:
            continue
        new_c_i = decrement(c_i, concept_i)
        superconcepts_dict[new_c_i] = {decrement(supc_i, concept_i) for supc_i in superconcepts_dict[c_i]}
        subconcepts_dict[new_c_i] = {decrement(subc_i, concept_i) for subc_i in subconcepts_dict[c_i]}
        if new_c_i != c_i:
            del superconcepts_dict[c_i]
            del subconcepts_dict[c_i]

    top_concept_i = decrement(top_concept_i, concept_i) if top_concept_i is not None else None
    bottom_concept_i = decrement(bottom_concept_i, concept_i) if bottom_concept_i is not None else None

    return concepts, subconcepts_dict, superconcepts_dict, top_concept_i, bottom_concept_i
