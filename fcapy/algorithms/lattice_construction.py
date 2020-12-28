def complete_comparison(concepts):
    all_subconcepts_dict = {i: [] for i in range(len(concepts))}
    for a_i, a in enumerate(concepts):
        for b_i, b in enumerate(concepts):
            if b < a:
                all_subconcepts_dict[a_i].append(b_i)

    subconcepts_dict = {i: [] for i in range(len(concepts))}
    for a_i, b_is in all_subconcepts_dict.items():
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
    all_superconcepts = {}
    incomparables = {}
    superconcepts_dict = {}
    subconcepts_dict = {}
    for c_i, c in enumerate(concepts):
        all_superconcepts[c_i] = set()
        incomparables[c_i] = set()
        superconcepts_dict[c_i] = set()
        subconcepts_dict[c_i] = set()

    # Sort concepts by size of extent: from the more general to more specific
    if not is_concepts_sorted:
        concepts_sorted = ConceptLattice.sort_concepts(concepts) if not is_concepts_sorted else concepts
        map_concept_i_sort = {c: c_i_sort for c_i_sort, c in enumerate(concepts_sorted)}
        map_concept_i = {c: c_i for c_i, c in enumerate(concepts)}
        map_i_isort = [map_concept_i_sort[concepts[c_i]] for c_i in range(len(concepts))]

    # get the list of chains in the spanning tree. Each chain starts with a top concept index
    chains = sptree_chains

    # iterate through every chain. If new concept in the chain is found: select its superconcepts and subconcepts
    for ch_i_cur in range(len(chains)):
        # start comparison of current concept and concepts from chain `ch_i from idxs_comp[ch_i]
        idxs_comp = [0]*len(chains)
        # iterate through every concept in the chain. Except the very first one (it is the lattice top concept)
        for idx_cur, c_i_cur in enumerate(chains[ch_i_cur][1:]):
            idx_cur += 1  # position of current concept in the chain should start with 1
            c_cur = concepts[c_i_cur]
            if len(superconcepts_dict[c_i_cur]) > 0:
                # if superconcepts of current concept are already found
                continue

            superconcept_i_cur = chains[ch_i_cur][idx_cur-1]
            superconcepts_dict[c_i_cur] = {superconcept_i_cur}
            all_superconcepts[c_i_cur] |= {superconcept_i_cur} | all_superconcepts[superconcept_i_cur]

            # iterate through other chains. Looking for superconcepts of the current concept
            for ch_i_comp in range(len(chains)):
                if ch_i_comp == ch_i_cur:
                    continue

                chain_comp = chains[ch_i_comp]
                idx_comp_start = idxs_comp[ch_i_comp]
                for idx_comp, c_i_comp in enumerate(chain_comp[idx_comp_start:]):
                    idx_comp += idx_comp_start
                    if c_i_comp in all_superconcepts[c_i_cur]:  # superconcepts_dict[c_i_cur]:
                        continue

                    has_smaller_i = map_i_isort[c_i_comp] < map_i_isort[c_i_cur] \
                        if not is_concepts_sorted else c_i_comp < c_i_cur

                    # if at last concepts in the chain it is superconcept
                    last_in_chain = idx_comp == len(chain_comp) - 1

                    # if stepped on the concept in chain which is not subconcept
                    if c_i_comp in incomparables[c_i_cur]:
                        is_superconcept = False
                    else:
                        c_comp = concepts[c_i_comp]
                        is_superconcept = c_comp > c_cur if has_smaller_i else False
                        if has_smaller_i and not is_superconcept:
                            incomparables[c_i_cur].add(c_i_comp)

                    if is_superconcept and last_in_chain:
                        superconcepts_dict[c_i_cur] |= {c_i_comp}
                        idxs_comp[ch_i_comp] = idx_comp
                        all_superconcepts[c_i_cur].add(c_i_comp)
                        break

                    if not is_superconcept:
                        superconcept_i_comp = chain_comp[idx_comp - 1]

                        superconcepts_dict[c_i_cur] |= {superconcept_i_comp}
                        idxs_comp[ch_i_comp] = idx_comp
                        break

                    all_superconcepts[c_i_cur].add(c_i_comp)

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


def construct_lattice_by_spanning_tree(concepts, is_concepts_sorted=False):
    from ..lattice import ConceptLattice
    subconcepts_st_dict, superconcepts_st_dict = \
        construct_spanning_tree(concepts, is_concepts_sorted=is_concepts_sorted)
    chains = ConceptLattice._get_chains(concepts, superconcepts_st_dict, is_concepts_sorted=is_concepts_sorted)
    subconcepts_dict = construct_lattice_from_spanning_tree(concepts, chains, is_concepts_sorted=is_concepts_sorted)
    return subconcepts_dict
