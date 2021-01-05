def complete_comparison(concepts, is_concepts_sorted=False, n_jobs=1):
    def get_subconcepts(a_i, a, concepts):
        subconcepts = []
        for b_i, b in enumerate(concepts):
            if is_concepts_sorted:
                if b_i < a_i:
                    continue

            if b < a:
                subconcepts.append(b_i)
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

    subconcepts_dict = {i: [] for i in range(len(concepts))}
    for a_i, b_is in all_subconcepts_dict.items():
        b_is = b_is if not is_concepts_sorted else sorted(b_is)
        for b_i in b_is:
            for c_i in b_is:
                if b_i == c_i:
                    continue
                if b_i in all_subconcepts_dict[c_i]:
                    break
            else:
                subconcepts_dict[a_i].append(b_i)

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
        superconcepts_st_dict[c_i] = [superconcept_i]

    subconcepts_st_dict = {k: list(v) for k, v in subconcepts_st_dict.items()}
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
    subconcepts_dict = {k: sorted(v) for k, v in subconcepts_dict.items()}
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
        from contextlib import nullcontext
        parallel_manager = nullcontext(lambda x: x)
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
    subconcepts_dict = {k: sorted(v) for k, v in subconcepts_dict.items()}
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
