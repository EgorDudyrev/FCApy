"""
This module provides visualizers to draw Hasse diagrams
"""
from fcapy.poset import POSet
from fcapy.visualizer.hasse_layouts import LAYOUTS
from fcapy.utils.utils import get_kwargs_used

from typing import Tuple, Callable


class AbstractHasseViz:
    def __init__(
            self,
            node_color='lightgray', node_alpha=1, node_size=300, node_label_func=None, node_label_font_size=12,
            node_border_color='white', node_border_width=1,
            edge_color='lightgray', edge_radius=0,
            cmap='Blues', cmap_min=None, cmap_max=None,
            draw_node_indices=False, show_axes=False, nodelist=None,
    ):
        # Node properties
        self.node_color = node_color
        self.node_alpha = node_alpha
        self.node_size = node_size
        self.node_label_func = node_label_func
        self.node_label_font_size = node_label_font_size

        self.node_border_color = node_border_color
        self.node_border_width = node_border_width

        # Edge properties
        self.edge_color = edge_color
        self.edge_radius = edge_radius

        # Colormap properties
        self.cmap = cmap
        self.cmap_min = cmap_min
        self.cmap_max = cmap_max

        # Toggles
        self.draw_node_indices = draw_node_indices
        self.nodelist = nodelist
        self.show_axes = show_axes

    #############
    # Functions #
    #############
    def draw_poset(self, poset):
        raise NotImplementedError

    @staticmethod
    def get_nodes_position(poset: POSet, layout='fcart', **kwargs):
        """Return a dict of nodes positions in a line diagram"""
        if layout not in LAYOUTS:
            raise ValueError(
                f'Layout "{layout}" is not supported. '
                f'Possible layouts are: {", ".join(LAYOUTS.keys())}'
            )
        layout_func = LAYOUTS[layout]
        kwargs_used = get_kwargs_used(kwargs, layout_func)
        return layout_func(poset, **kwargs_used)

    ###################
    # Node properties #
    ###################
    @property
    def node_color(self):
        return self._node_color

    @node_color.setter
    def node_color(self, value: str or Tuple[str]):
        self._node_color = value

    @property
    def node_alpha(self):
        return self._node_alpha

    @node_alpha.setter
    def node_alpha(self, value: float):
        self._node_alpha = value

    @property
    def node_size(self):
        return self._node_size

    @node_size.setter
    def node_size(self, value: float):
        self._node_size = value

    @property
    def node_label_func(self):
        return self._node_label_func

    @node_label_func.setter
    def node_label_func(self, value: Callable):
        self._node_label_func = value

    @property
    def node_label_font_size(self):
        return self._node_label_font_size

    @node_label_font_size.setter
    def node_label_font_size(self, value: float):
        self._node_label_font_size = value

    @property
    def node_border_color(self):
        return self._node_border_color

    @node_border_color.setter
    def node_border_color(self, value: str or Tuple[str]):
        self._node_border_color = value

    @property
    def node_border_width(self):
        return self._node_border_width

    @node_border_width.setter
    def node_border_width(self, value: float):
        self._node_border_width = value

    ###################
    # Edge properties #
    ###################
    @property
    def edge_color(self):
        return self._edge_color

    @edge_color.setter
    def edge_color(self, value: str or Tuple[str]):
        self._edge_color = value

    @property
    def edge_radius(self):
        return self._edge_radius

    @edge_radius.setter
    def edge_radius(self, value: float):
        self._edge_radius = value

    #######################
    # Colormap properties #
    #######################
    @property
    def cmap(self):
        return self._cmap

    @cmap.setter
    def cmap(self, value: str):
        self._cmap = value

    @property
    def cmap_min(self):
        return self._cmap_min

    @cmap_min.setter
    def cmap_min(self, value: float):
        self._cmap_min = value

    @property
    def cmap_max(self):
        return self._cmap_max

    @cmap_max.setter
    def cmap_max(self, value: float):
        self._cmap_max = value

    ##################
    # Binary toggles #
    ##################
    @property
    def draw_node_indices(self):
        return self._flag_draw_node_indices
    
    @draw_node_indices.setter
    def draw_node_indices(self, value: bool):
        self._flag_draw_node_indices = value

    @property
    def nodelist(self):
        return self._nodelist

    @nodelist.setter
    def nodelist(self, value: Tuple[int] or None):
        self._nodelist = value

    @property
    def show_axes(self):
        return self._show_axes

    @show_axes.setter
    def show_axes(self, value: bool):
        self._show_axes = value
        
    def _filter_nodes_edges(self, G):
        if self.nodelist is not None:
            nodelist = self.nodelist
            missing_nodeset = set(G.nodes) - set(nodelist)
        else:
            nodelist, missing_nodeset = list(G.nodes), set()

        edgelist = [
            e for e in G.edges
            if e[0] not in missing_nodeset and e[1] not in missing_nodeset
        ]
        return nodelist, edgelist


class NetworkxHasseViz(AbstractHasseViz):
    import matplotlib.pyplot as plt

    def draw_poset(self, poset: POSet, ax=plt.Axes, pos=None):
        pos = self.get_nodes_position(poset) if pos is None else pos

        G = poset.to_networkx('down')
        nodelist, edgelist = self._filter_nodes_edges(G)
        self._draw_edges(G, pos, ax, edgelist)
        self._draw_nodes(G, pos, ax, nodelist)
        if self.node_label_func is not None:
            self._draw_node_labels(G, pos, ax, nodelist)
        if self.draw_node_indices:
            self._draw_node_indices(G, pos, ax, nodelist)

        if self.show_axes:
            ax.set_axis_on()
        else:
            ax.set_axis_off()

    def _draw_nodes(self, G, pos, ax, nodelist):
        import networkx as nx

        nx.draw_networkx_nodes(
            G, pos,
            nodelist=nodelist,
            node_color=self.node_color, cmap=self.cmap, alpha=self.node_alpha,
            linewidths=self.node_border_width, edgecolors=self.node_border_color,
            vmin=self.cmap_min, vmax=self.cmap_max,
            ax=ax,
            node_size=self.node_size
        )

    def _draw_node_labels(self, G, pos, ax, nodelist):
        import networkx as nx

        labels = {el_i: self.node_label_func(el_i) for el_i in nodelist}
        nx.draw_networkx_labels(
            G, pos,
            labels=labels,
            horizontalalignment='center',  # 'left',
            font_size=int(self.node_label_font_size),
            ax=ax
        )

    def _draw_node_indices(self, G, pos, ax, nodelist):
        import networkx as nx

        labels = {el_i: f"{el_i}" for el_i in nodelist}
        nx.draw_networkx_labels(G, pos, ax=ax, labels=labels)

    def _draw_edges(self, G, pos, ax, edgelist):
        import networkx as nx

        cs = f'arc3,rad={self.edge_radius}' if self.edge_radius is not None else None
        nx.draw_networkx_edges(
            G, pos,
            edgelist=edgelist,
            edge_color=self.edge_color,
            arrowstyle='-', connectionstyle=cs,
            ax=ax
        )
