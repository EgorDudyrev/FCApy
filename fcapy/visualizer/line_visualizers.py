"""
This module provides visualizers to draw line diagrams

"""
from fcapy.poset import POSet
from fcapy.visualizer.line_layouts import find_nodes_edges_overlay
from fcapy.visualizer.mover import Mover
from fcapy.utils.utils import get_kwargs_used as kw_used, get_not_none
from fcapy.lattice import ConceptLattice

import networkx as nx

from typing import Tuple, Callable, Dict, Iterable
from dataclasses import dataclass

import logging
import warnings


class NodeEdgeOverlayWarning(UserWarning):
    def __init__(self, overlays: Dict[Tuple[int, int], Tuple[int, ...]]):
        self.overlays = overlays

    def __str__(self):
        msg = '\n'.join([
            "Some lines in the line diagram overlap the nodes.",
            "Please, modify the ``pos`` dictionary parameter manually. "
            "You can obtain the default ``pos`` via Mover.initialize_pos(...) function.",
            "",
            "The problematic edges and nodes (in the form of {edge: overlapped nodes indexes}) are:",
            f"{self.overlays}",
        ])
        return msg


class UnsupportedNodeVaryingParameterError(ValueError):
    def __init__(self, param_value, lib_name, param_name):
        self.param_value = param_value
        self.lib_name = lib_name
        self.param_name = param_name

    def __str__(self):
        msg = '\n'.join([
            f"Node {self.param_name} parameter value is unsupported.",
            "It might be defined in one of the following ways:",
            f"* a single {self.param_name} to paint every node (ex. for node_color parameter: 'red');",
            f"* a tuple of {self.param_name}s specific to every node in the visualization "
            f"(ex. for node_color parameter: ('red', 'blue', 'green'), given that there are 3 nodes in total); and"
            f"* a tuple of {self.param_name}s specific to every node in the ``nodelist`` "
            f"(ex. for node_color parameter: ('red', 'blue'), given that there are 2 nodes in ``nodelist`` parameter)",
            '',
            f"The {self.param_name} values should be entered in a format, supported by the library: {self.lib_name}",
            "",
            f"The entered node {self.param_name} parameter value is: {self.param_value}",
        ])
        return msg


@dataclass
class AbstractLineViz:
    """An abstract class for line visualizer that keeps all the possible visualization parameters"""
    LIB_NAME = "<AbstractLib>"

    #####################
    # Fields            #
    #####################
    # Mover object
    mover: Mover = None

    # Node fields
    nodelist: Tuple[int, ...] = None
    node_color: str = 'lightgray'
    node_shape: str = 'o'

    node_alpha: float = 1
    node_size: float = 300
    node_label_func: Callable[[int, POSet], str] = None
    node_label_font_size: int = 12
    node_border_color: str = 'white'
    node_border_width: float = 1

    # Edge fields
    edgelist: Tuple[Tuple[int, int], ...] = None
    edge_color: str = 'lightgray'
    edge_radius: float = 0
    edge_width: float = 1
    edge_cmap: str = None

    # Colormap fields
    cmap: str = 'Blues'
    cmap_min: float = None
    cmap_max: float = None

    # Binary toggles
    flg_node_indices: bool = False
    flg_axes: bool = False
    flg_drop_bottom_concept: bool = False

    #####################
    # Functions         #
    #####################

    # Drawing functions
    def draw_poset(self, poset: POSet, **kwargs):
        """The main function to draw Partially Ordered Sets"""
        raise NotImplementedError

    def draw_quiver(self, poset: POSet, edges: Tuple[int, int, str], **kwargs):
        """Quiver = directed graph with multiple edges between pairs of nodes.

        .. warning::
            It is only a test feature
        """
        raise NotImplementedError

    def draw_concept_lattice(self, lattice: ConceptLattice, **kwargs):
        """Draw `lattice` via `draw_poset` function with node labels generated by `concept_lattice_label_func` """
        if 'node_label_func' not in kwargs:
            kwargs['node_label_func'] = lambda c_i, L: self.concept_lattice_label_func(
                c_i, L, **kw_used(kwargs, self.concept_lattice_label_func)
            )
        # Temporary solution to drop the bottom concept of a `lattice`
        # if it does not contain any objects and, therefore, any new intent
        flg_name = 'flg_drop_empty_bottom'
        if flg_name in kwargs:
            warnings.warn(
                f"The flag {flg_name} will be removed in future versions"
                "since it is just a temporary solution. "
                "Please, use `flg_drop_bottom_concept` parameter",
                FutureWarning
            )

            if kwargs[flg_name]:
                bc_i = lattice.bottom
                if len(lattice[bc_i].extent) == 0:
                    kwargs['flg_drop_bottom_concept'] = True

        kwargs['bottom_concept_i_to_drop'] = lattice.bottom \
            if kwargs.get('flg_drop_bottom_concept', self.flg_drop_bottom_concept) else None

        self.draw_poset(lattice, **kwargs)

    # Other useful functions
    def _filter_nodes_edges(
            self,
            G: nx.Graph,
            nodelist: Tuple[int, ...] = None,
            edgelist: Tuple[Tuple[int, int], ...] = None,
            bottom_concept_i_to_drop: int = None
    ):
        """Return the list of nodes to draw and edges associated to the nodes.

        Draw all the nodes and edges by default
        """
        # set up default values if none specified
        nodelist = get_not_none(nodelist, self.nodelist)
        edgelist = get_not_none(edgelist, self.edgelist)

        # draw all nodes if none is still specified
        if nodelist is None:
            nodelist = list(G.nodes)

        # drop bottom concept for concept lattice (implying it is empty). (See self.draw_concept_lattice(...) func)
        if bottom_concept_i_to_drop:
            nodelist.remove(bottom_concept_i_to_drop)

        # draw only the edges for the drawn nodes. If other is not specified
        if edgelist is None:
            edgelist = list(G.edges)
        edgelist = [e for e in edgelist if all([v in nodelist for v in e[:2]])]

        return nodelist, edgelist

    @staticmethod
    def concept_lattice_label_func(
            c_i: int, lattice: ConceptLattice,
            flg_new_intent_count_prefix: bool = True, max_new_intent_count: int = 2,
            flg_new_extent_count_prefix: bool = True, max_new_extent_count: int = 2
    ) -> str:
        """A default function to label each concept in the concept lattice visualization

        The label looks somewhat like: ::

            10: m1, m2, m3, m5, ...

            3: g1, g2, g6

        where m_i are attributes of concept intent, and g_i are objects of concept extent
        """
        def short_set_repr(set_: set, flg_count_prefix: bool, max_count: int) -> str:
            if len(set_) > 0:
                s = f"{len(set_)}: " if flg_count_prefix else ""
                s += ', '.join(sorted(set_)[:max_count])
            else:
                s = ''
            return s

        new_intent_str = short_set_repr(lattice.get_concept_new_intent(c_i),
                                        flg_new_intent_count_prefix, max_new_intent_count)
        new_extent_str = short_set_repr(lattice.get_concept_new_extent(c_i),
                                        flg_new_extent_count_prefix, max_new_extent_count)

        label = '\n\n'.join([new_intent_str, new_extent_str])
        return label

    def _retrieve_nodelist_edgelist(self, poset, kwargs):
        """Return nodelist and edgelist to be drawn (either default ones or specified with kwargs)"""
        G = poset.to_networkx('down')
        nodelist, edgelist = self._filter_nodes_edges(G, **kw_used(kwargs, self._filter_nodes_edges))
        for k in ['nodelist', 'edgelist']:
            if k in kwargs:
                del kwargs[k]

        return G, nodelist, edgelist

    def _retrieve_pos(self, poset, kwargs, nodelist, edgelist):
        """Return the nodes positions to be drawn (either default ones or specified with kwargs)"""
        if 'pos' in kwargs:
            pos = kwargs['pos']
        else:
            if self.mover is None or self.mover.pos is None:
                self.init_mover_per_poset(poset, **kwargs)
            pos = self.mover.pos

        overlays = find_nodes_edges_overlay(pos, nodelist, edgelist)
        if len(overlays) > 0:
            #warnings.warn(str(overlays), NodeEdgeOverlayWarning)
            logging.warning(NodeEdgeOverlayWarning(overlays))

        if 'pos' in kwargs:
            del kwargs['pos']
        return pos

    def _parse_node_varying_parameter(self, param_value, default_value, nodelist, graph_size, param_name):
        """Return the values of parameters that may vary through nodes (e.g. node_color, node_shape, node_size)"""
        param_value = get_not_none(param_value, default_value)

        if isinstance(param_value, str) or not isinstance(param_value, Iterable):
            return [param_value] * len(nodelist)

        param_value = list(param_value)
        if len(param_value) == len(nodelist):
            return param_value
        if len(param_value) == graph_size:
            return [param_value[i] for i in nodelist]

        raise UnsupportedNodeVaryingParameterError(param_value, self.LIB_NAME, param_name)

    def init_mover_per_poset(self, poset: POSet, **kwargs):
        """Construct mover with default positions given Partially Ordered set"""
        self.mover = Mover()
        self.mover.initialize_pos(poset, **kw_used(kwargs, self.mover.initialize_pos))


class LineVizNx(AbstractLineViz):
    """A class to draw line visualisations via Networkx package

    ----------
    Parameters
    ----------
    mover: Mover
        Mover object, defaults to ``None``
    nodelist: Tuple[int, ...]
        defaults to ``None``
    node_color: str
        defaults to ``'lightgray'``
    node_shape: str
        defaults to ``'o'``
    node_alpha: float
        defaults to ``1``
    node_size: float
        defaults to ``300``
    node_label_func: Callable[[int, POSet], str]
        defaults to ``None``
    node_label_font_size: int
        defaults to ``12``
    node_border_color: str
        defaults to ``'white'``
    node_border_width: float
        defaults to ``1``
    edgelist: Tuple[Tuple[int, int], ...]
        defaults to ``None``
    edge_color: str
        defaults to ``'lightgray'``
    edge_radius: float
        defaults to  ``0``
    edge_width: float
        defaults to ``1``
    edge_cmap: str
        defaults to ``None``
    cmap: str
        defaults to ``'Blues'``
    cmap_min: float
        defaults to ``None``
    cmap_max: float
        defaults to ``None``
    flg_node_indices: bool
        defaults to ``False``
    flg_axes: bool
        defaults to ``False``
    flg_drop_bottom_concept: bool
        defaults to  ``False``

    """
    LIB_NAME = 'networkx'

    def draw_poset(self, poset: POSet, ax=None, **kwargs):
        """Draw a Partially Ordered Set as a line diagram with Networkx package

        .. important::
            Please specify `ax` parameter in order for the function to work properly e.g.

            .. code-block:: python

                import matplotlib.pyplot as plt
                viz = LineVizNx()
                poset = POSet(...)

                fig, ax = plt.subplots()
                viz.draw_poset(poset, ax=ax, ...)

        """
        assert ax is not None,\
            "Please specify `ax` parameter in order for the function to work properly." \
            "You may obtain the `ax` value via ```import matplotlib.pyplot as plt; fig, ax = plt.subplots()```"

        G, nodelist, edgelist = self._retrieve_nodelist_edgelist(poset, kwargs)
        pos = self._retrieve_pos(poset, kwargs, nodelist, edgelist)

        self._setup_legend(ax, **kw_used(kwargs, self._setup_legend))
        self._draw_edges(G, pos, ax, edgelist, **kw_used(kwargs, self._draw_edges))
        self._draw_nodes(G, pos, ax, nodelist, **kw_used(kwargs, self._draw_nodes))

        node_label_func = kwargs.get('node_label_func', self.node_label_func)
        if node_label_func is not None:
            self._draw_node_labels(poset, G, pos, ax, nodelist, **kw_used(kwargs, self._draw_node_labels))

        flg_node_indices = kwargs.get('flg_node_indices', self.flg_node_indices)
        if flg_node_indices:
            self._draw_node_indices(G, pos, ax, nodelist)

        flg_axes = kwargs.get('flg_axes', self.flg_axes)
        for spine in ['right', 'top', 'left', 'bottom']:
            ax.spines[spine].set_visible(flg_axes)

        return G, pos, nodelist, edgelist

    def draw_concept_lattice(self, lattice: ConceptLattice, **kwargs):
        """Draw `lattice` with `draw_poset` function with node labels generated by `concept_lattice_label_func`

        .. important::
            Please specify the `ax` parameter from kwargs in order for the function to work properly e.g.

            .. code-block:: python

                import matplotlib.pyplot as plt
                viz = LineVizNx()
                L = ConceptLattice(...)

                fig, ax = plt.subplots()
                viz.draw_concept_lattice(L, ax=ax, ...)

        """
        super(LineVizNx, self).draw_concept_lattice(lattice, **kwargs)

    def draw_quiver(self, poset: POSet, edges: Tuple[int, int, str], ax=None, **kwargs):
        """Quiver = directed graph with multiple edges between pairs of nodes.

        .. warning::
            It is only a test feature
        """
        G, pos, nodelist, _ = self.draw_poset(poset, ax, **dict(kwargs, edgelist=[]))

        edge_label_rotate = kwargs.get('edge_label_rotate', False)
        edge_label_pos = kwargs.get('edge_label_pos', 0.9)
        edge_color = kwargs.get('edge_color', self.edge_color)

        is_edge_color_rgba_single = len(edge_color) in {3, 4} and all([isinstance(x, float) for x in edge_color])
        is_edge_color_specific = len(edge_color) == len(edges) and not is_edge_color_rgba_single

        edge_labels_map = {}
        for e in edges:
            child_i, parent_i, label = e
            edge_labels_map[(parent_i, child_i)] = edge_labels_map.get((parent_i, child_i), []) + [label]

        edgelist = list(edge_labels_map)

        # multiedges = list(set([el for i, el in enumerate(edgelist) if el in edgelist[i + 1:]]))

        for edge, labels in edge_labels_map.items():
            if len(labels) % 2 == 0:
                r_func = lambda i: (i // 2 + 1) * ((-1) ** (i % 2))
            else:
                r_func = lambda i: ((i - 1) // 2 + 1) * ((-1) ** (i % 2 + 1))

            for i, label in enumerate(labels):
                if is_edge_color_specific:
                    edge_lbl = (edge[1], edge[0], label)
                    edge_lbl_i = edges.index(edge_lbl)
                    edge_color_ = edge_color[edge_lbl_i]
                else:
                    edge_color_ = edge_color

                r = r_func(i)
                self._draw_edges(G, pos, ax, [edge], edge_radius=r*0.1, edge_color=[edge_color_])

        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels={edge: '\n'.join(labels) for edge, labels in edge_labels_map.items()},
            rotate=edge_label_rotate,
            ax=ax, label_pos=edge_label_pos
        )
        return G, pos, nodelist, edgelist

    def _draw_nodes(
            self, G, pos, ax, nodelist,
            node_color=None, cmap=None, node_alpha=None,
            node_border_width=None, node_border_color=None,
            cmap_min=None, cmap_max=None, node_size=None,
            node_shape=None,
            color_legend=None,
            shape_legend=None,
    ):
        """Draw nodes via networkx package"""
        lcls = locals()

        kwargs_static = dict(
            ax=ax,
            cmap=lcls.get('cmap', self.cmap),
            alpha=lcls.get('node_alpha', self.node_alpha),
            linewidths=lcls.get('node_border_width', self.node_border_width),
            edgecolors=lcls.get('node_border_color', self.node_border_color),
            vmin=lcls.get('cmap_min', self.cmap_min),
            vmax=lcls.get('cmap_max', self.cmap_max),
        )

        node_color, node_shape, node_size = [
            self._parse_node_varying_parameter(lcls[pname], self.__dict__[pname], nodelist, len(G), pname)
            for pname in ['node_color', 'node_shape', 'node_size']
        ]

        for color, shape in set(zip(node_color, node_shape)):
            nlist = [node_i for (node_i, clr, shp) in zip(nodelist, node_color, node_shape)
                     if clr == color and shp == shape]
            sizes = [node_size[i] for i in nlist]

            nx.draw_networkx_nodes(
                G, pos,
                nodelist=nlist, node_color=color, node_shape=shape, node_size=sizes,
                **kwargs_static
            )

    def _setup_legend(self, ax, node_color_legend=None, node_shape_legend=None):
        """Add matplotlib legend to axis"""
        G = nx.Graph([(0, 0)])
        nodelist = [0]
        pos = {0: (0, 0)}

        fclr = ax.get_facecolor()
        if node_color_legend:
            lgnd_kwargs = dict(nodelist=nodelist, node_size=100)
            for k, v in node_color_legend.items():
                nx.draw_networkx_nodes(G, pos, node_color=k, label=v, **lgnd_kwargs)

            lgnd_kwargs_overlap = lgnd_kwargs.copy()
            lgnd_kwargs_overlap['linewidths'] = lgnd_kwargs_overlap.get('linewidths', 1) + 1
            nx.draw_networkx_nodes(G, pos, node_color=[fclr], edgecolors=[fclr], **lgnd_kwargs_overlap)

        if node_shape_legend:
            lgnd_kwargs = dict(nodelist=nodelist, node_color=[fclr], linewidths=2,  node_size=100)
            lgnd_kwargs_overlap = lgnd_kwargs.copy()
            lgnd_kwargs_overlap['linewidths'] = lgnd_kwargs_overlap.get('linewidths', 1) + 1

            for k, v in node_shape_legend.items():
                nx.draw_networkx_nodes(G, pos, node_shape=k, label=v, edgecolors='black', **lgnd_kwargs)
                nx.draw_networkx_nodes(G, pos, node_shape=k, edgecolors=[fclr], **lgnd_kwargs_overlap)

    def _draw_node_labels(
            self, poset, G, pos, ax, nodelist,
            node_label_func=None, node_label_font_size=None
    ):
        """Draw node labels via networkx package"""
        node_label_func = get_not_none(node_label_func, self.node_label_func)
        node_label_font_size = int(get_not_none(node_label_font_size, self.node_label_font_size))

        labels = {el_i: node_label_func(el_i, poset) for el_i in nodelist}
        nx.draw_networkx_labels(
            G, pos,
            labels=labels,
            horizontalalignment='center',  # 'left',
            font_size=node_label_font_size,
            ax=ax
        )

    def _draw_node_indices(self, G, pos, ax, nodelist):
        """Draw node indices via networkx package"""
        labels = {el_i: f"{el_i}" for el_i in nodelist}
        nx.draw_networkx_labels(G, pos, ax=ax, labels=labels)

    def _draw_edges(
            self, G, pos, ax, edgelist,
            edge_radius=None, edge_color=None,
            edge_width=None, node_size=None,
            edge_cmap=None,
    ):
        """Draw edges via networkx package"""
        edge_radius = get_not_none(edge_radius, self.edge_radius)
        edge_color = get_not_none(edge_color, self.edge_color)
        edge_width = get_not_none(edge_width, self.edge_width)
        node_size = get_not_none(node_size, self.node_size)
        edge_cmap = get_not_none(edge_cmap, self.edge_cmap)

        cs = f'arc3,rad={edge_radius}' if edge_radius is not None else None
        nx.draw_networkx_edges(
            G, pos,
            edgelist=edgelist,
            edge_color=edge_color, width=edge_width, edge_cmap=edge_cmap,
            node_size=node_size,
            arrowstyle='-', connectionstyle=cs,
            ax=ax,
        )
