def test_load_data():
    import pandas as pd
    from fcapy.context import FormalContext
    url = 'https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/data/animal_movement.csv'
    K = FormalContext.from_pandas(pd.read_csv(url, index_col=0))

    # Print the first five objects data
    print(K[:5])

    assert K.extension(['fly', 'swim']) == ['duck', 'goose']
    assert K.intention(['dove', 'goose']) == ['fly']


def test_lattice_construction():
    import pandas as pd
    from fcapy.context import FormalContext
    url = 'https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/data/animal_movement.csv'
    K = FormalContext.from_pandas(pd.read_csv(url, index_col=0))

    # Create the concept lattice
    from fcapy.lattice import ConceptLattice
    L = ConceptLattice.from_context(K)

    assert len(L) == 8
    assert L.top == 0
    assert L.bottom == 7


def test_lattice_visualisation():
    import pandas as pd
    from fcapy.context import FormalContext
    url = 'https://raw.githubusercontent.com/EgorDudyrev/FCApy/main/data/animal_movement.csv'
    K = FormalContext.from_pandas(pd.read_csv(url, index_col=0))

    # Create the concept lattice
    from fcapy.lattice import ConceptLattice
    L = ConceptLattice.from_context(K)

    import matplotlib.pyplot as plt
    from fcapy.visualizer import LineVizNx
    fig, ax = plt.subplots(figsize=(10, 5))
    vsl = LineVizNx()
    vsl.draw_concept_lattice(L, ax=ax, flg_node_indices=True)
    #ax.set_title('"Animal movement" concept lattice', fontsize=18)
    #plt.tight_layout()
    #plt.show()
