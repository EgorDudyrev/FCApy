"""
This module provides visualizers to draw Hasse diagrams
"""
from fcapy.poset import POSet
from fcapy.visualizer.hasse_layouts import LAYOUTS
from fcapy.utils.utils import get_kwargs_used, get_not_none
from fcapy.lattice import ConceptLattice

from typing import Tuple, Callable, Dict
from numbers import Number


class AbstractHasseViz:
    def __init__(
            self,
            pos: Dict[int, Tuple[Number, Number]] = None,
            nodelist: Tuple[int] = None,
            node_color: str = 'lightgray', node_alpha: Number = 1, node_size: Number = 300,
            node_label_func: Callable[[int, POSet], str] = None, node_label_font_size: int = 12,
            node_border_color: str = 'white', node_border_width: Number = 1,
            edge_color: str = 'lightgray', edge_radius: Number = 0,
            cmap: str = 'Blues', cmap_min: Number = None, cmap_max: Number = None,
            flg_draw_node_indices: bool = False, flg_show_axes: bool = False,
    ):
        """Initialize the class and set up default parameters values"""
        self.pos = pos
        self.nodelist = nodelist
        self.node_color = node_color
        self.node_alpha = node_alpha
        self.node_size = node_size
        self.node_label_func = node_label_func
        self.node_label_font_size = node_label_font_size
        self.node_border_color = node_border_color
        self.node_border_width = node_border_width
        self.edge_color = edge_color
        self.edge_radius = edge_radius
        self.cmap = cmap
        self.cmap_min = cmap_min
        self.cmap_max = cmap_max
        self.flg_draw_node_indices = flg_draw_node_indices
        self.flg_show_axes = flg_show_axes

    #############
    # Functions #
    #############
    def draw_poset(self, poset, **kwargs):
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

    def _filter_nodes_edges(self, G, nodelist=None):
        if nodelist is not None:
            nodelist = self.nodelist
            missing_nodeset = set(G.nodes) - set(nodelist)
        else:
            nodelist, missing_nodeset = list(G.nodes), set()

        edgelist = [
            e for e in G.edges
            if e[0] not in missing_nodeset and e[1] not in missing_nodeset
        ]
        return nodelist, edgelist

    @staticmethod
    def concept_lattice_label_func(
            c_i: int, lattice: ConceptLattice,
            flg_draw_new_intent_count_prefix: bool, max_new_intent_count: int,
            flg_draw_new_extent_count_prefix: bool, max_new_extent_count: int
    ) -> str:
        new_intent = list(lattice.get_concept_new_intent(c_i))
        if len(new_intent) > 0:
            new_intent_str = f"{len(new_intent)}: " if flg_draw_new_intent_count_prefix else ""
            new_intent_str += ', '.join(new_intent[:max_new_intent_count])
            if len(new_intent_str) > 0 \
                    and max_new_intent_count is not None and len(new_intent) > max_new_intent_count:
                new_intent_str += '...'
        else:
            new_intent_str = ''

        new_extent = list(lattice.get_concept_new_extent(c_i))
        if len(new_extent) > 0:
            new_extent_str = f"{len(new_extent)}: " if flg_draw_new_extent_count_prefix else ""
            new_extent_str += ', '.join(new_extent[:max_new_extent_count])
            if len(new_extent_str) > 0 \
                    and max_new_extent_count is not None and len(new_extent) > max_new_extent_count:
                new_extent_str += '...'
        else:
            new_extent_str = ''

        label = '\n\n'.join([new_intent_str, new_extent_str])
        return label

    ###################
    # Node properties #
    ###################
    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def nodelist(self):
        return self._nodelist

    @nodelist.setter
    def nodelist(self, value):
        self._nodelist = value

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
    def flg_draw_node_indices(self):
        return self._flg_draw_node_indices
    
    @flg_draw_node_indices.setter
    def flg_draw_node_indices(self, value: bool):
        self._flg_draw_node_indices = value

    @property
    def flg_show_axes(self):
        return self._show_axes

    @flg_show_axes.setter
    def flg_show_axes(self, value: bool):
        self._show_axes = value


class NetworkxHasseViz(AbstractHasseViz):
    import matplotlib.pyplot as plt

    def draw_poset(
            self, poset: POSet, ax=plt.Axes,
            pos: Dict[int, Tuple[Number, Number]] = None, nodelist: Tuple[int] = None,
            node_color: str = None, node_alpha: Number = None, node_size: Number = None,
            node_label_func: Callable[[int, POSet], str] = None, node_label_font_size: int = None,
            node_border_color: str = None, node_border_width: Number = None,
            edge_color: str = None, edge_radius: Number = None,
            cmap: str = None, cmap_min: Number = None, cmap_max: Number = None,
            flg_draw_node_indices: bool = None, flg_show_axes: bool = None,
    ):
        pos = self.get_nodes_position(poset) if pos is None else pos

        G = poset.to_networkx('down')
        nodelist, edgelist = self._filter_nodes_edges(G, nodelist)
        self._draw_edges(
            G, pos, ax, edgelist,
            edge_radius=edge_radius, edge_color=edge_color
        )

        self._draw_nodes(
            G, pos, ax, nodelist,
            node_color=node_color, cmap=cmap, node_alpha=node_alpha,
            node_border_width=node_border_width, node_border_color=node_border_color,
            cmap_min=cmap_min, cmap_max=cmap_max, node_size=node_size
        )

        node_label_func = get_not_none(node_label_func, self.node_label_func)
        if node_label_func is not None:
            self._draw_node_labels(
                poset, G, pos, ax, nodelist,
                node_label_func=node_label_func, node_label_font_size=node_label_font_size
            )

        flg_draw_node_indices = get_not_none(flg_draw_node_indices, self.flg_draw_node_indices)
        if flg_draw_node_indices:
            self._draw_node_indices(
                G, pos, ax, nodelist,
            )

        flg_show_axes = get_not_none(flg_show_axes, self.flg_show_axes)
        if flg_show_axes:
            ax.set_axis_on()
        else:
            ax.set_axis_off()

    def _draw_nodes(
            self, G, pos, ax, nodelist,
            node_color = None, cmap = None, node_alpha = None,
            node_border_width = None, node_border_color = None,
            cmap_min = None, cmap_max = None, node_size = None
    ):
        node_color = get_not_none(node_color, self.node_color)
        cmap =  get_not_none(cmap, self.cmap)
        node_alpha = get_not_none(node_alpha, self.node_alpha)
        node_border_width = get_not_none(node_border_width, self.node_border_width)
        node_border_color = get_not_none(node_border_color, self.node_border_color)
        cmap_min = get_not_none(cmap_min, self.cmap_min)
        cmap_max = get_not_none(cmap_max, self.cmap_max)
        node_size = get_not_none(node_size, self.node_size)

        import networkx as nx

        nx.draw_networkx_nodes(
            G, pos,
            nodelist=nodelist,
            node_color=node_color, cmap=cmap, alpha=node_alpha,
            linewidths=node_border_width, edgecolors=node_border_color,
            vmin=cmap_min, vmax=cmap_max,
            ax=ax,
            node_size=node_size
        )

    def _draw_node_labels(
            self, poset, G, pos, ax, nodelist,
            node_label_func=None, node_label_font_size=None
    ):
        node_label_func = get_not_none(node_label_func, self.node_label_func)
        node_label_font_size = int(get_not_none(node_label_font_size, self.node_label_font_size))

        import networkx as nx

        labels = {el_i: node_label_func(el_i, poset) for el_i in nodelist}
        nx.draw_networkx_labels(
            G, pos,
            labels=labels,
            horizontalalignment='center',  # 'left',
            font_size=node_label_font_size,
            ax=ax
        )

    def _draw_node_indices(
            self, G, pos, ax, nodelist,
    ):
        import networkx as nx

        labels = {el_i: f"{el_i}" for el_i in nodelist}
        nx.draw_networkx_labels(G, pos, ax=ax, labels=labels)

    def _draw_edges(
            self, G, pos, ax, edgelist,
            edge_radius=None, edge_color=None
    ):
        edge_radius = get_not_none(edge_radius, self.edge_radius)
        edge_color = get_not_none(edge_color, self.edge_color)

        import networkx as nx

        cs = f'arc3,rad={edge_radius}' if edge_radius is not None else None
        nx.draw_networkx_edges(
            G, pos,
            edgelist=edgelist,
            edge_color=edge_color,
            arrowstyle='-', connectionstyle=cs,
            ax=ax
        )
