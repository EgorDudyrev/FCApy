"""
This subpackage provides a number of options to visualize objects of `fcapy` package

Classes
-------
hasse_visualizers.LineVizNx:
    A class to visualize the `POSet` (incl. `ConceptLattice`) via NetworkX package.
mover.Mover:
    A class to move nodes in a visualization in a user friendly fashion.

Modules
-------
hasse_layouts:
    This module provides a set of functions to derive a layout (node positions) for a given POSet
hasse_visualizers:
    This module provides visualizer classes to draw Hasse diagrams
measures:
    This module provides functions to measure the "goodness" of visualizations: e.g. amount of lines intersections
mover:
    This module provides a class Mover to make node moving in Hasse Diagrams easier

Deprecated
----------
visualizer.POSetVisualizer:
    A class to visualize `POSet`s
visualizer.ConceptLatticeVisualizer:
    A class to visualize `ConceptLattice`s
visualizer:
    This module provides classes `POSetVisualizer` and `ConceptLatticeVisualizer`
    to visualize a `POSet` or a `ConceptLattice` respectively

"""
from .line_visualizers import LineVizNx
from .mover import Mover

from .visualizer import POSetVisualizer, ConceptLatticeVisualizer
