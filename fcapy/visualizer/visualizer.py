import networkx as nx


class Visualizer:
    def __init__(
            self, lattice=None,
            node_color='blue', cmap='Blues', node_alpha=1, node_linewidth=1, node_edgecolor='blue'):
        self._lattice = lattice
        self._pos = self.get_nodes_position() if lattice is not None else None
        self.node_color = node_color
        self.cmap = cmap
        self.node_alpha = node_alpha
        self.node_linewidth = node_linewidth
        self.node_edgecolor = node_edgecolor

    def get_nodes_position(self, lattice=None):
        lattice = self._lattice if lattice is None else lattice
        c_levels, levels_dict = self._calc_levels()
        n_levels = len(levels_dict)
        digraph = nx.DiGraph(lattice.subconcepts_dict)
        for c_i, l_i in enumerate(c_levels):
            digraph.nodes[c_i]['level'] = l_i
        pos = nx.multipartite_layout(digraph, subset_key='level', align='horizontal')
        pos = {c_i: [p[0], -p[1]] for c_i, p in pos.items()}
        return pos

    def _calc_levels(self, lattice=None):
        lattice = self._lattice if lattice is None else lattice
        c_levels = [0] * len(lattice.concepts)
        nodes_to_visit = [lattice.top_concept_i]
        while len(nodes_to_visit) > 0:
            node_id = nodes_to_visit.pop(0)
            spc_ids = lattice.superconcepts_dict[node_id]
            c_levels[node_id] = max([c_levels[spc_id] for spc_id in spc_ids]) + 1 if len(spc_ids) > 0 else 0
            nodes_to_visit += lattice.subconcepts_dict[node_id]

        levels_dict = {i: [] for i in range(max(c_levels) + 1)}
        for c_i, c in enumerate(lattice.concepts):
            levels_dict[c_levels[c_i]].append(c_i)
        return c_levels, levels_dict

    def draw_networkx(self):
        graph = nx.from_dict_of_lists(self._lattice.subconcepts_dict)
        nx.draw_networkx_nodes(
            graph, self._pos,
            node_color=self.node_color, cmap=self.cmap, alpha=self.node_alpha,
            linewidths=self.node_linewidth, edgecolors=self.node_edgecolor
        )
        nx.draw_networkx_edges(graph, self._pos)
