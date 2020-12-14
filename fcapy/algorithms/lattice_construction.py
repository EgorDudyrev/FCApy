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
