"""
This module provides a class `Visualizer` to visualize a `ConceptLattice`
"""
from fcapy.poset import POSet
from fcapy.lattice import ConceptLattice
from fcapy.visualizer.line_layouts import LAYOUTS
from fcapy.utils.utils import get_kwargs_used

import networkx as nx
from collections.abc import Iterable

import warnings


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
            node_color='lightgray', edge_color='lightgray', node_edgecolor='white',
            cmap='Blues', node_alpha=1, node_size=300, node_linewidth=1,
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
        label_font_size: `int`
            The size of a font size when labeling the nodes
        """
        warnings.warn(
            "The use of class POSetVisualizer and its successors is deprecated and will be removed in future versions."
            "Please, move to use LineVizNx class for visualization",
            FutureWarning
        )

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

    @staticmethod
    def get_nodes_position(poset, layout='fcart', **kwargs):
        """Return a dict of nodes positions in a line diagram"""
        if layout not in LAYOUTS:
            raise ValueError(
                f'Layout "{layout}" is not supported. '
                f'Possible layouts are: {", ".join(LAYOUTS.keys())}'
            )
        layout_func = LAYOUTS[layout]
        kwargs_used = get_kwargs_used(kwargs, layout_func)
        return layout_func(poset, **kwargs_used)

    def draw_networkx(
        self,
        draw_node_indices=False, edge_radius=None,
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
        label_func: `int` -> `str`
            A function to create a label for a given element defined by an index
        ax: `Matplotlib Axes`
            A matplotlib axis to draw a poset on
        nodelist: `list`[`int`]
            Indexes of poset elements to draw.
        Returns
        -------
        """
        G = self._poset.to_networkx('down')
        if nodelist is None:
            nodelist = list(range(len(self._poset)))
        missing_nodeset = set(range(len(self._poset))) - set(nodelist)
        edgelist = [
            e for e in G.edges
            if e[0] not in missing_nodeset and e[1] not in missing_nodeset
        ]

        cs = f'arc3,rad={edge_radius}' if edge_radius is not None else 'arc3,rad=0'  # None
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

    def draw_plotly(
            self,
            label_func=None,
            nodelist: list = None,
            **kwargs):
        """Get a line diagram of `POSet` constructed by `plotly` package
        Parameters
        ----------
        label_func: 'int' -> 'str'
            A function to create a label for a given element defined by an index
        nodelist: `list`[`int`]
            Indexes of poset elements to draw.
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
        fig: `plotly.graph_objects.FigureWidget`
            A line diagram of POSet in the form of Plotly FigureWidget
        """
        from plotly import graph_objects as go

        digraph = self._poset.to_networkx('down')
        pos = self._pos
        nx.set_node_attributes(digraph, pos, 'pos')

        # Convert edges of the graph to the plotly format
        edge_x = [y for edge in digraph.edges() for y in [pos[edge[0]][0], pos[edge[1]][0], None]]
        edge_y = [y for edge in digraph.edges() for y in [pos[edge[0]][1], pos[edge[1]][1], None]]

        import math

        edge_color = [self.edge_color] * len(digraph.edges) if type(self.edge_color) == str \
            else self.edge_color * math.ceil((len(digraph.edges) / len(self.edge_color)))

        edge_traces = [dict(type='scatter',
                            x=[edge_x[k * 3], edge_x[k * 3 + 1]],
                            y=[edge_y[k * 3], edge_y[k * 3 + 1]],
                            mode='lines',
                            line=dict(width=1, color=edge_color[k])) for k in range(len(digraph.edges))]

        # Convert nodes of the graph to the plotly format
        node_x = [pos[node][0] for node in digraph.nodes()]
        node_y = [pos[node][1] for node in digraph.nodes()]

        node_color = [self.node_color[n] for n in digraph.nodes()] if type(self.node_color) != str \
            else [self.node_color for n in digraph.nodes()]

        node_size = self.node_size / 30

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            textposition='middle right',
            marker=dict(
                showscale=True,
                cmin=self.cmap_min,
                cmax=self.cmap_max,
                colorscale=self.cmap,
                reversescale=True,
                color=node_color,
                size=node_size,
                colorbar=dict(
                    thickness=15,
                    title=kwargs.get('colorbar_title', ''),
                    xanchor='left',
                    titleside='right'
                ),
                line_width=self.node_linewidth)
        )

        # Add color and text to nodes
        node_trace.marker.color = node_color
        node_trace.marker.opacity = [self.node_alpha[n] for n in digraph.nodes()] \
            if isinstance(self.node_alpha, Iterable) else self.node_alpha

        node_labels = [label_func(i) for i in range(len(self._poset))] if label_func is not None else []
        node_hovertext = [f"id: {i}\n\n{lbl}" for i, lbl in enumerate(node_labels)]
        node_labels, node_hovertext = [[x.replace('\n', '<br>') for x in lst] for lst in [node_labels, node_hovertext]]
        node_trace.text = node_labels
        node_trace.hovertext = node_hovertext

        data = [node_trace]
        for edge_trace in edge_traces:
            data.append(edge_trace)

        fig = go.FigureWidget(
            data=data,
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

        from copy import copy

        node_color_copy = copy(node_color)

        def update_point(trace, points, selector):
            c = node_color_copy
            s = [node_size * 1.0] * len(digraph)
            for i in points.point_inds:
                if c[i] == node_color[i]:
                    c[i] = 'green'
                    s[i] = node_size * 2.5

                    for j in digraph.neighbors(i):
                        c[j] = 'green'
                        s[j] = node_size * 1.5
                else:
                    c[i] = node_color[i]
                    s[i] = node_size

                    for j in digraph.neighbors(i):
                        c[j] = node_color[i]
                        s[j] = node_size

                with fig.batch_update():
                    fig.data[0].marker.color = c
                    fig.data[0].marker.size = s

        fig.data[0].on_click(update_point)

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
            node_color='lightgray', edge_color='lightgrey', node_edgecolor='white',
            cmap='Blues', node_alpha=1, node_linewidth=1,
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
        label_font_size: `int`
            The size of a font size when labeling the nodes
        node_size: `int`
            The size of a node in the visualization
        """
        super(ConceptLatticeVisualizer, self).__init__(
            poset=lattice, node_color=node_color, edge_color=edge_color, cmap=cmap, node_alpha=node_alpha,
            node_linewidth=node_linewidth, node_edgecolor=node_edgecolor, cmap_min=cmap_min, cmap_max=cmap_max,
            label_font_size=label_font_size, node_size=node_size,
        )
        self._lattice = lattice

    def _concept_label_func(
            self, c_i,
            draw_new_intent_len, max_new_intent_count,
            draw_new_extent_len, max_new_extent_count,
    ):
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

    def draw_networkx(
            self, draw_node_indices=False, edge_radius=None, max_new_extent_count=3, max_new_intent_count=3,
            draw_bottom_concept=True, draw_new_extent_len=True, draw_new_intent_len=True,
            label_func=None,
            ax=None,
            nodelist=None,
    ):
        """Draw line diagram of the `ConceptLattice` with `networkx` package
        Parameters
        ----------
        draw_node_indices: `bool`
            A flag whether to draw indexes of nodes inside the nodes
        edge_radius: `float`
            A value of how much curve the edges on line diagram should be
        ax: `Matplotlib Axes`
            A matplotlib axis to draw a lattice on
        nodelist: `list`[`int`]
            Indexes of lattice elements to draw
        draw_bottom_concept: `bool`
            A flag whether to draw the bottom concept of a lattice
        label_func: `int` -> `str`
            A function to create a label for a given element defined by an index
        max_new_extent_count: `int`
            A number of new objects in concept extent to draw (used by default ``label_func``)
        draw_new_extent_len: `bool`
            A flag whether to draw a size of a concept extent before the extent itself (used by default ``label_func``)
        max_new_intent_count: `int`
            A number of new attributes in concept intent to draw (used by default ``label_func``)
        draw_new_intent_len: `bool`
            A flag whether to draw a size of a concept intent before the intent itself (used by default ``label_func``)
        Returns
        -------
        """
        nodelist = list(range(len(self._lattice))) if nodelist is None else nodelist
        if not draw_bottom_concept:
            nodelist.remove(self._lattice.bottom)

        if label_func is None:
            label_func = lambda c_i: self._concept_label_func(
                c_i, draw_new_intent_len, max_new_intent_count,
                draw_new_extent_len, max_new_extent_count
            )

        super(ConceptLatticeVisualizer, self).draw_networkx(
            draw_node_indices=draw_node_indices, edge_radius=edge_radius,
            label_func=label_func, ax=ax, nodelist=nodelist
        )

    def draw_plotly(
            self, max_new_extent_count=3, max_new_intent_count=3,
            draw_new_extent_len=True, draw_new_intent_len=True,
            label_func=None,
            nodelist=None,
    ):
        """Draw line diagram of the `ConceptLattice` with `plotly` package
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
        nodelist = list(range(len(self._lattice))) if nodelist is None else nodelist

        if label_func is None:
            label_func = lambda c_i: self._concept_label_func(
                c_i, draw_new_intent_len, max_new_intent_count,
                draw_new_extent_len, max_new_extent_count
            )

        fig = super(ConceptLatticeVisualizer, self).draw_plotly(
            label_func=label_func,
            nodelist=nodelist
        )
        return fig
