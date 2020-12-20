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


def construct_spanning_tree(concepts):
    from fcapy.lattice import ConceptLattice

    sorted_concepts_map = {c: c_i for c_i, c in enumerate(ConceptLattice.sort_concepts(concepts))}
    concepts_sorted_is = [sorted_concepts_map[c] for c in concepts]

    subconcepts_st_dict = {}
    superconcepts_st_dict = {}

    for c_sort_i, c_i in enumerate(concepts_sorted_is):
        c = concepts[c_i]

        subconcepts_st_dict[c_i] = set()
        if c_sort_i == 0:
            superconcepts_st_dict[c_i] = []
            continue

        un_i = concepts_sorted_is[0]
        sifted = True
        while sifted:
            for ln_i in subconcepts_st_dict[un_i]:
                ln = concepts[ln_i]
                if c < ln:
                    un_i = ln_i
                    break
            else:
                sifted = False

        subconcepts_st_dict[un_i].add(c_i)
        superconcepts_st_dict[c_i] = [un_i]

    subconcepts_st_dict = {k: list(v) for k, v in subconcepts_st_dict.items()}
    return subconcepts_st_dict, superconcepts_st_dict
