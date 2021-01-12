from fcapy.utils import utils


def test_powerset():
    ps = set(utils.powerset([1, 2, 3]))
    ps_true = {(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)}
    assert ps == ps_true, 'utils.powerset failed. Powerset does not give the expected result'


def test_sparse_unique_columns():
    import scipy as sp

    data = [[0, 1, 0, 0],
            [0, 1, 1, 0],
            [1, 1, 1, 1],
            [0, 1, 1, 0]]

    M = sp.sparse.csc_matrix(data)[[1, 2, 3, 0, 0]]
    M1, idx, counts = utils.sparse_unique_columns(M)

    M_true = sp.sparse.csc_matrix(
        [[0., 1., 1.],
         [1., 1., 1.],
         [0., 1., 1.],
         [0., 0., 1.],
         [0., 0., 1.]])
    idx_true = [0, 3, 2, 1]
    counts_true = [2, 1, 1]
    assert (M1 != M_true).mean() == 0, 'utils.sparse_unique_columns failed'
    assert (idx == idx_true).mean() == 1, 'utils.sparse_unique_columns failed'
    assert (counts == counts_true).mean() == 1, 'utils.sparse_unique_columns failed'
