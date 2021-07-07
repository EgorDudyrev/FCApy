from fcapy.visualizer import visualizer
from fcapy.context import converters
from fcapy.lattice.concept_lattice import ConceptLattice
import numpy as np

import pytest


def test__init__():
    with pytest.raises(AssertionError):
        vsl = visualizer.ConceptLatticeVisualizer()
    with pytest.raises(AssertionError):
        vsl = visualizer.POSetVisualizer()


def test_get_nodes_position():
    path = 'data/animal_movement.json'
    K = converters.read_json(path)
    L = ConceptLattice.from_context(K)

    pos = visualizer.POSetVisualizer.get_nodes_position(L)
    
    pos = visualizer.POSetVisualizer.get_nodes_position(L, 'fcart')

    with pytest.raises(ValueError):
        pos = visualizer.POSetVisualizer.get_nodes_position(L, 'FaKeLaYoUt')


def test_draw_networkx():
    path = 'data/animal_movement.json'
    ctx = converters.read_json(path)
    ltc = ConceptLattice.from_context(ctx)

    vsl = visualizer.ConceptLatticeVisualizer(ltc)
    vsl.draw_networkx(draw_node_indices=True)

    vsl = visualizer.POSetVisualizer(ltc)
    vsl.draw_networkx(draw_node_indices=True)


def test_draw_plotly():
    path = 'data/animal_movement.json'
    ctx = converters.read_json(path)
    ltc = ConceptLattice.from_context(ctx)

    vsl = visualizer.ConceptLatticeVisualizer(ltc)
    vsl.draw_plotly()

    vsl = visualizer.POSetVisualizer(ltc)
    vsl.draw_plotly()
