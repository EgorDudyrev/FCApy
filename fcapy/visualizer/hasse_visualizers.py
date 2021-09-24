"""
This module provides visualizers to draw Hasse diagrams
"""
from typing import Tuple


class AbstractHasseViz:
    def __init__(
            self,
            node_color='lightgray', edge_color='lightgray', node_border_color='white',
            cmap='Blues', cmap_min=None, cmap_max=None,
            node_alpha=1, node_size=300, node_border_width=1,
            node_label_font_size=12

    ):
        # Node properties
        self.node_color = node_color
        self.node_alpha = node_alpha
        self.node_size = node_size
        self.node_label_font_size = node_label_font_size

        self.node_border_color = node_border_color
        self.node_border_width = node_border_width

        # Edge properties
        self.edge_color = edge_color

        # Colormap properties
        self.cmap = cmap
        self.cmap_min = cmap_min
        self.cmap_max = cmap_max

    #############
    # Functions #
    #############
    def draw(self):
        raise NotImplementedError

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
