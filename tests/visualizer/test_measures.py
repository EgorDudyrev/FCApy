from fcapy.context import FormalContext
from fcapy.lattice import ConceptLattice
from fcapy.visualizer import line_layouts
from fcapy.visualizer import measures


def test_count_line_intersections():
    path = 'data/animal_movement.csv'
    K = FormalContext.read_csv(path)
    K_df = K.to_pandas()
    for m in K.attribute_names:
        K_df[f'not_{m}'] = ~K_df[m]
    K = FormalContext.from_pandas(K_df)
    L = ConceptLattice.from_context(K)

    pos_multipartite = line_layouts.multipartite_layout(L)
    n_intersections_multipartite = measures.count_line_intersections(pos_multipartite, L)
    assert n_intersections_multipartite == 19, "Wrong number of line intersections in multipartite layout"

    pos_fcart = line_layouts.fcart_layout(L)
    n_intersections_fcart = measures.count_line_intersections(pos_fcart, L)
    assert n_intersections_fcart == 14, "Wrong number of line intersections in fcart layout"
