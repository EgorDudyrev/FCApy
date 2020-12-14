class Visualizer:
    def __init__(self, lattice):
        self._lattice = lattice
        self._pos = self.get_nodes_position()

    def get_nodes_position(self):
        ltc = self._lattice
        levels = [0] * len(ltc.concepts)
        nodes_to_visit = [ltc.top_concept_i]
        while len(nodes_to_visit) > 0:
            node_id = nodes_to_visit.pop(0)
            spc_ids = ltc.superconcepts_dict[node_id]
            levels[node_id] = max([levels[spc_id] for spc_id in spc_ids]) + 1 if len(spc_ids) > 0 else 0
            nodes_to_visit += ltc.subconcepts_dict[node_id]

        levels_dict = {i: [] for i in range(len(levels))}
        for c_i, c in enumerate(ltc.concepts):
            levels_dict[levels[c_i]].append(c_i)

        pos = {}
        for l_i, c_is in levels_dict.items():
            for idx, c_i in enumerate(c_is):
                pos[c_i] = (idx, -l_i)
        return pos

    def draw_networkx(self):
        import networkx as nx
        graph = nx.from_dict_of_lists(self._lattice.subconcepts_dict)
        nx.draw_networkx(graph, self._pos)
