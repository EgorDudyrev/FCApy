from fcapy.visualizer import visualizer
from fcapy.context import converters
from fcapy.lattice.concept_lattice import ConceptLattice


def test__init__():
    path = 'data/animal_movement.json'
    ctx = converters.read_json(path)
    ltc = ConceptLattice.from_context(ctx)

    vsl = visualizer.Visualizer(ltc)
    pos = {2: (0, 0), 1: (0, -1), 5: (1, -1), 7: (2, -1),
           3: (0, -2), 4: (1, -2), 6: (2, -2), 0: (0, -3)}
    assert vsl._pos == pos, 'Visualizer.__init__ failed. Nodes position calculated wrongly'


def test_draw_networkx():
    path = 'data/animal_movement.json'
    ctx = converters.read_json(path)
    ltc = ConceptLattice.from_context(ctx)

    vsl = visualizer.Visualizer(ltc)
    vsl.draw_networkx()
