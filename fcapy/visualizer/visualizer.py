"""
This module provides a class `Visualizer` to visualize a `ConceptLattice`

"""
from fcapy.poset import POSet
from fcapy.lattice import ConceptLattice
import networkx as nx
from collections.abc import Iterable


class POSetVisualizer:
    """
    A class to visualize `POSet` as graph

    Methods
    -------
    draw_networkx(...):
        Draw a `ConceptLattice` line diagram with networkx package
    get_plotly_figure(...):
        Return a Plotly figure with the `ConceptLattice` line diagram
    """

    def __init__(
            self, poset: POSet = None,
            node_color='lightblue', edge_color='lightgrey',
            cmap='Blues', node_alpha=1, node_size=300, node_linewidth=1, node_edgecolor='darkblue',
            cmap_min=None, cmap_max=None, label_font_size=12,
    ):
        """Initialize the Visualizer

        Parameters
        ----------
        poset: `POSet`
            A Partially Ordered Set to visualize
        node_color: `str` or `list` of `str`
            A default color to use for ConceptLattice visualization (can be changed afterwards)
        cmap: `str`
            Colormap to use for ConceptLattice visualization
        node_alpha: `float`
            Transparency of nodes
        node_linewidth: `float`
            Width of borderline (edge) around the nodes in a line diagram
        node_edgecolor: `float`
            Color of borderline (edge) around the nodes in a line diagram
        cmap_min: `float`
            The minimum value of a colormap
        cmap_max: `float`
            The maximum value of a colormap

        """
        assert poset is not None, "Cannot visualize an empty poset"

        self._poset = poset
        self._pos = self.get_nodes_position(poset) if poset is not None else None
        self.node_color = node_color
        self.edge_color = edge_color
        self.cmap = cmap
        self.cmap_min = cmap_min
        self.cmap_max = cmap_max
        self.node_alpha = node_alpha
        self.node_linewidth = node_linewidth
        self.node_edgecolor = node_edgecolor
        self.node_size = node_size
        self.label_font_size = label_font_size

    def get_nodes_position(self, poset, layout='multipartite'):
        """Return a dict of nodes positions in a line diagram"""
        if layout == 'multipartite':
            pos = self.multipartite_layout(poset)
        else:
            raise NotImplementedError(f'Layout "{layout}" is not supported. Possible values are: "multipartite"')
        return pos

    def multipartite_layout(self, poset):
        c_levels, levels_dict = self._calc_levels(poset)
        G = poset.to_networkx('down')
        nx.set_node_attributes(G, dict(enumerate(c_levels)), 'level')
        pos = nx.multipartite_layout(G, subset_key='level', align='horizontal')
        pos = {c_i: [p[0], -p[1]] for c_i, p in pos.items()}
        return pos

    def _calc_levels(self, poset):
        """Return levels (y position) of nodes and dict with {`level`: `nodes`} mapping in a line diagram"""
        poset = self._poset if poset is None else poset
        c_levels = [0] * len(poset)
        nodes_to_visit = poset.top_elements
        nodes_visited = set()
        while len(nodes_to_visit) > 0:
            node_id = nodes_to_visit.pop(0)
            nodes_visited.add(node_id)
            dsups_ids = poset.direct_super_elements(node_id)
            c_levels[node_id] = max([c_levels[dsup_id] for dsup_id in dsups_ids]) + 1 if len(dsups_ids) > 0 else 0
            nodes_to_visit += [n_i for n_i in poset.direct_sub_elements(node_id) if n_i not in nodes_visited]

        levels_dict = {i: [] for i in range(max(c_levels) + 1)}
        for c_i in range(len(poset)):
            levels_dict[c_levels[c_i]].append(c_i)
        return c_levels, levels_dict

    def draw_networkx(
        self,
        draw_node_indices=False, edge_radius=None,
        max_new_extent_count=3, max_new_intent_count=3,
        label_func=None, ax=None,
        nodelist:list = None
    ):
        """Draw line diagram of the `POSet` with `networkx` package

        Parameters
        ----------
        draw_node_indices: `bool`
            A flag whether to draw indexes of nodes inside the nodes
        edge_radius: `float`
            A value of how much curve the edges on line diagram should be
        max_new_extent_count: `int`
            A number of new objects in concept extent to draw
        max_new_intent_count: `int`
            A number of new attributes in concept intent to draw

        Returns
        -------

        """
        poset = self._poset

        G = poset.to_networkx('down')
        if nodelist is None:
            nodelist = list(range(len(self._poset)))
        missing_nodeset = set(range(len(poset))) - set(nodelist)
        edgelist = [
            e for e in G.edges
            if e[0] not in missing_nodeset and e[1] not in missing_nodeset
        ]

        cs = f'arc3,rad={edge_radius}' if edge_radius is not None else None
        nx.draw_networkx_edges(
            G, self._pos,
            edgelist=edgelist,
            edge_color=self.edge_color,
            arrowstyle='-', connectionstyle=cs,
            ax=ax
        )
        
        nx.draw_networkx_nodes(
            G, self._pos,
            nodelist=nodelist,
            node_color=self.node_color, cmap=self.cmap, alpha=self.node_alpha,
            linewidths=self.node_linewidth, edgecolors=self.node_edgecolor,
            vmin=self.cmap_min, vmax=self.cmap_max,
            ax=ax,
            node_size=self.node_size
        )

        if label_func is not None:
            labels = {el_i: label_func(el_i) for el_i in range(len(self._poset))}

            nx.draw_networkx_labels(
                G, self._pos, labels={el_i: l for el_i, l in labels.items() if el_i in range(len(self._poset))},
                horizontalalignment='center', #'left',
                font_size=self.label_font_size,
                ax=ax
            )

        if draw_node_indices:
            nx.draw_networkx_labels(
                G, self._pos,
                ax=ax,
                labels={el_i: f"{el_i}" for el_i in nodelist}
            )


    def draw_plotly(self, poset=None, **kwargs):
        """Get a line diagram of `POSet` constructed by `plotly` package

        Parameters
        ----------
        kwargs:
            colorbar_title: `str`
                A title of colorbar axis
            max_new_extent_count: `int`
                A number of new objects in concept extent to draw
            max_new_intent_count: `int`
                A number of new objects in concept extent to draw
            xlim: `tuple of `float`
                A tuple of xaxis ranges (x_left, x_right) (default value is (-1, 1))
            figsize: `tuple` of `float`
                A tuple of size of a figure (width, height) (default value is (1000, 500))

        Returns
        -------
        fig: `plotly.graph_objects.Figure`
            A line diagram of POSet in the form of Plotly Figure

        """
        from plotly import graph_objects as go

        digraph = self._poset.to_networkx('down')
        pos = self._pos
        nx.set_node_attributes(digraph, pos, 'pos')

        # Convert edges of the graph to the plotly format
        edge_x = [y for edge in digraph.edges() for y in [pos[edge[0]][0], pos[edge[1]][0], None]]
        edge_y = [y for edge in digraph.edges() for y in [pos[edge[0]][1], pos[edge[1]][1], None]]

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Convert nodes of the graph to the plotly format
        node_x = [pos[node][0] for node in digraph.nodes()]
        node_y = [pos[node][1] for node in digraph.nodes()]

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            textposition='middle right',
            marker=dict(
                showscale=True,
                # colorscale options
                # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale=self.cmap,
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title=kwargs.get('colorbar_title', ''),
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2)
        )

        # Add color and text to nodes
        node_trace.marker.color = [self.node_color[n] for n in digraph.nodes()] \
            if type(self.node_color) != str else self.node_color
        node_trace.marker.opacity = [self.node_alpha[n] for n in digraph.nodes()] \
            if isinstance(self.node_alpha, Iterable) else self.node_alpha

        node_labels = []
        node_hovertext = []
        node_trace.text = node_labels
        node_trace.hovertext = node_hovertext

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=kwargs.get('title', 'POSet'),
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(range=kwargs.get('xlim', (-1, 1)), showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                width=kwargs.get('figsize', [1000, 500])[0],
                height=kwargs.get('figsize', [1000, 500])[1]
            )
        )
        return fig


class ConceptLatticeVisualizer(POSetVisualizer):
    """
    A class for visualizing the `ConceptLattice`

    Methods
    -------
    draw_networkx(...):
        Draw a `ConceptLattice` line diagram with networkx package
    get_plotly_figure(...):
        Return a Plotly figure with the `ConceptLattice` line diagram
    """
    def __init__(
            self, lattice: ConceptLattice = None,
            node_color='lightblue', edge_color='lightgrey', cmap='Blues', node_alpha=1, node_linewidth=1, node_edgecolor='darkblue',
            cmap_min=None, cmap_max=None, label_font_size=12, node_size=300,
    ):
        """Initialize the Visualizer

        Parameters
        ----------
        lattice: `ConceptLattice`
            A ConceptLattice to visualize
        node_color: `str` or `list` of `str`
            A default color to use for ConceptLattice visualization (can be changed afterwards)
        cmap: `str`
            Colormap to use for ConceptLattice visualization
        node_alpha: `float`
            Transparency of nodes
        node_linewidth: `float`
            Width of borderline (edge) around the nodes in a line diagram
        node_edgecolor: `str`
            Color of borderline (edge) around the nodes in a line diagram
        cmap_min: `float`
            The minimum value of a colormap
        cmap_max: `float`
            The maximum value of a colormap

        """
        super(ConceptLatticeVisualizer, self).__init__(
            poset=lattice, node_color=node_color, edge_color=edge_color, cmap=cmap, node_alpha=node_alpha,
            node_linewidth=node_linewidth, node_edgecolor=node_edgecolor, cmap_min=cmap_min, cmap_max=cmap_max,
            label_font_size=label_font_size, node_size=node_size,
        )
        self._lattice = lattice

    def draw_networkx(
            self, draw_node_indices=False, edge_radius=None, max_new_extent_count=3, max_new_intent_count=3,
            draw_bottom_concept=True, draw_new_extent_len=True, draw_new_intent_len=True,
            label_func=None,
            ax=None,
    ):
        """Draw line diagram of the `ConceptLattice` with `networkx` package

        Parameters
        ----------
        draw_node_indices: `bool`
            A flag whether to draw indexes of nodes inside the nodes
        edge_radius: `float`
            A value of how much curve the edges on line diagram should be
        max_new_extent_count: `int`
            A number of new objects in concept extent to draw
        max_new_intent_count: `int`
            A number of new attributes in concept intent to draw

        Returns
        -------

        """
        graph = self._lattice.to_networkx()

        nodelist = list(range(len(self._lattice)))
        if not draw_bottom_concept:
            nodelist.remove(self._lattice.bottom_concept_i)
        edgelist = list(graph.edges)
        if not draw_bottom_concept:
            edgelist = [e for e in edgelist if self._lattice.bottom_concept_i not in e]

        cs = f'arc3,rad={edge_radius}' if edge_radius is not None else None

        nx.draw_networkx_edges(graph, self._pos, edgelist=edgelist,
                               edge_color=self.edge_color, arrowstyle='-', connectionstyle=cs,
                               ax=ax)

        nx.draw_networkx_nodes(
            graph, self._pos,
            node_color=self.node_color, cmap=self.cmap, alpha=self.node_alpha,
            linewidths=self.node_linewidth, edgecolors=self.node_edgecolor,
            vmin=self.cmap_min, vmax=self.cmap_max,
            nodelist=nodelist,
            node_size=self.node_size,
            ax=ax,
        )

        if label_func is None:
            def label_func(c_i):
                new_intent = list(self._lattice.get_concept_new_intent(c_i))
                if len(new_intent) > 0:
                    new_intent_str = f"{len(new_intent)}: " if draw_new_intent_len else ""
                    new_intent_str += ', '.join(new_intent[:max_new_intent_count])
                    if len(new_intent_str) > 0 \
                            and max_new_intent_count is not None and len(new_intent) > max_new_intent_count:
                        new_intent_str += '...'
                else:
                    new_intent_str = ''

                new_extent = list(self._lattice.get_concept_new_extent(c_i))
                if len(new_extent) > 0:
                    new_extent_str = f"{len(new_extent)}: " if draw_new_extent_len else ""
                    new_extent_str += ', '.join(new_extent[:max_new_extent_count])
                    if len(new_extent_str) > 0 \
                            and max_new_extent_count is not None and len(new_extent) > max_new_extent_count:
                        new_extent_str += '...'
                else:
                    new_extent_str = ''

                label = '\n\n'.join([new_intent_str, new_extent_str])
                return label

        labels = {c_i: label_func(c_i) for c_i in range(len(self._lattice))}
        
        nx.draw_networkx_labels(
            graph, self._pos, labels={c_i: l for c_i, l in labels.items() if c_i in nodelist},
            horizontalalignment='center', #'left',
            font_size=self.label_font_size,
            ax=ax,
        )

        if draw_node_indices:
            nx.draw_networkx_labels(
                graph, self._pos,
                labels={c_i: f"{c_i}" for c_i in nodelist},
                #font_size=self.label_font_size
                ax=ax,
            )

    def draw_plotly(self, poset=None, **kwargs):
        """Get a line diagram of `ConceptLattice` constructed by `plotly` package

        Parameters
        ----------
        kwargs:
            colorbar_title: `str`
                A title of colorbar axis
            max_new_extent_count: `int`
                A number of new objects in concept extent to draw
            max_new_intent_count: `int`
                A number of new objects in concept extent to draw
            xlim: `tuple of `float`
                A tuple of xaxis ranges (x_left, x_right) (default value is (-1, 1))
            figsize: `tuple` of `float`
                A tuple of size of a figure (width, height) (default value is (1000, 500))

        Returns
        -------
        fig: `plotly.graph_objects.Figure`
            A line diagram of ConceptLattice in the form of Plotly Figure

        """
        from plotly import graph_objects as go

        digraph = nx.DiGraph(self._lattice.subconcepts_dict)
        pos = self._pos
        nx.set_node_attributes(digraph, pos, 'pos')

        # Convert edges of the graph to the plotly format
        edge_x = [y for edge in digraph.edges() for y in [pos[edge[0]][0], pos[edge[1]][0], None]]
        edge_y = [y for edge in digraph.edges() for y in [pos[edge[0]][1], pos[edge[1]][1], None]]

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Convert nodes of the graph to the plotly format
        node_x = [pos[node][0] for node in digraph.nodes()]
        node_y = [pos[node][1] for node in digraph.nodes()]

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            textposition='middle right',
            marker=dict(
                showscale=True,
                # colorscale options
                # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale=self.cmap,
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title=kwargs.get('colorbar_title', ''),
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2)
        )

        # Add color and text to nodes
        node_trace.marker.color = [self.node_color[n] for n in digraph.nodes()] \
            if type(self.node_color) != str else self.node_color
        node_trace.marker.opacity = [self.node_alpha[n] for n in digraph.nodes()] \
            if isinstance(self.node_alpha, Iterable) else self.node_alpha

        node_labels = []
        node_hovertext = []
        for n in digraph.nodes():
            new_extent = list(self._lattice.get_concept_new_extent(n))
            new_intent = list(self._lattice.get_concept_new_intent(n))
            if len(new_extent) > 0:
                new_extent_str = f"{len(new_extent)}: " + ', '.join(new_extent[:kwargs.get('max_new_extent_count', 3)])
                new_extent_str += '...' if kwargs.get('max_new_extent_count') is not None and len(
                    new_extent) > kwargs.get('max_new_extent_count', 3) else ''
            else:
                new_extent_str = ''
            if len(new_intent) > 0:
                new_intent_str = f"{len(new_intent)}: " + ', '.join(new_intent[:kwargs.get('max_new_intent_count', 3)])
                new_intent_str += '...' if kwargs.get('max_new_intent_count') is not None and len(
                    new_intent) > kwargs.get('max_new_intent_count', 3) else ''
            else:
                new_intent_str = ''

            node_labels.append('<br><br>'.join([new_intent_str, new_extent_str]))
            node_hovertext.append(f'id: {n}<br><br>' + node_labels[-1])
        node_trace.text = node_labels
        node_trace.hovertext = node_hovertext

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=kwargs.get('title', 'Concept Lattice'),
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(range=kwargs.get('xlim', (-1, 1)), showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                width=kwargs.get('figsize', [1000, 500])[0],
                height=kwargs.get('figsize', [1000, 500])[1]
            )
        )
        return fig
