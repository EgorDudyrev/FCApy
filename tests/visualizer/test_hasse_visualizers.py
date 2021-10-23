from fcapy.visualizer import hasse_visualizers as viz
from fcapy.context import FormalContext
from fcapy.lattice.concept_lattice import ConceptLattice

import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image

import pytest


def test__init__abstract():
    vsl = viz.AbstractHasseViz()

    with pytest.raises(NotImplementedError):
        vsl.draw_poset(None)

    with pytest.raises(NotImplementedError):
        vsl.draw_quiver(None, None)

    with pytest.raises(NotImplementedError):
        vsl.draw_concept_lattice(None)


def test_get_nodes_position():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)

    vsl = viz.AbstractHasseViz()

    pos = vsl.get_nodes_position(L)

    pos = vsl.get_nodes_position(L, 'fcart')

    with pytest.raises(ValueError):
        pos = vsl.get_nodes_position(L, 'FaKeLaYoUt')


def test_filter_nodes_edges():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)
    G = L.to_networkx()

    nodes_all, edges_all = list(G.nodes), list(G.edges)
    nodes_filter = [0, 1, 3, 4, 5]
    edges_filter = [(0,1), (0,2), (1,4), (2,4)]

    vsl = viz.AbstractHasseViz()
    nodes, edges = vsl._filter_nodes_edges(G)
    assert nodes == nodes_all
    assert edges == edges_all

    nodes, edges = vsl._filter_nodes_edges(G, nodelist=nodes_filter)
    assert nodes == nodes_filter
    assert edges == [e for e in edges_all if e[0] in nodes_filter and e[1] in nodes_filter]

    nodes, edges = vsl._filter_nodes_edges(G, edgelist=edges_filter)
    assert nodes == nodes_all
    assert edges == edges_filter

    nodes, edges = vsl._filter_nodes_edges(G, nodelist=nodes_filter, edgelist=edges_filter)
    assert nodes == nodes_filter
    assert edges == [e for e in edges_filter if e[0] in nodes_filter and e[1] in nodes_filter]


def test_concept_lattice_label_func():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)
    vsl = viz.AbstractHasseViz()

    lbl = vsl.concept_lattice_label_func(0, L)
    assert lbl == '\n\n2: cow, hen'

    lbl = vsl.concept_lattice_label_func(2, L, max_new_extent_count=3)
    assert lbl == '1: run\n\n3: dog, horse, zebra'


def test_draw_concept_lattice_networkx():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)

    fig, ax = plt.subplots(figsize=(7, 5))
    vsl = viz.NetworkxHasseViz()
    vsl.draw_concept_lattice(
        L, ax=ax, flg_node_indices=False,
    )
    fig.tight_layout()

    with io.BytesIO() as buff:
        fig.savefig(buff, format='png', dpi=300)
        buff.seek(0)
        im = plt.imread(buff)

    im_true = image.imread('data/animal_movement_lattice.png')
    assert ((im-im_true) < 1e-6).all()
