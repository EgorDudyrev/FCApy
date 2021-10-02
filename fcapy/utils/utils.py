"""
This module provides a set of functions which can be useful in any subpackage of `fcapy` package

"""
from itertools import chain, combinations
from collections.abc import Iterable
import inspect

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['tqdm']:
    from tqdm.notebook import tqdm


def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def sparse_unique_columns(M):
    """Return unique columns of sparse scipy matrix ``M``

    Sincerely copy-pasted from https://stackoverflow.com/questions/50419778/unique-column-of-a-sparse-matrix-in-python
    """
    import numpy as np
    import scipy as sp

    M = M.tocsc()
    m, n = M.shape
    if not M.has_sorted_indices:
        M.sort_indices()
    if not M.has_canonical_format:
        M.sum_duplicates()
    sizes = np.diff(M.indptr)
    idx = np.argsort(sizes)
    Ms = M@sp.sparse.csc_matrix((np.ones((n,)), idx, np.arange(n+1)), (n, n))
    ssizes = np.diff(Ms.indptr)
    ssizes[1:] -= ssizes[:-1]
    grpidx, = np.where(ssizes)
    grpidx = np.concatenate([grpidx, [n]])
    if ssizes[0] == 0:
        counts = [np.array([0, grpidx[0]])]
    else:
        counts = [np.zeros((1,), int)]
    ssizes = ssizes[grpidx[:-1]].cumsum()
    for i, ss in enumerate(ssizes):
        gil, gir = grpidx[i:i+2]
        pl, pr = Ms.indptr[[gil, gir]]
        dv = Ms.data[pl:pr].view(f'V{ss*Ms.data.dtype.itemsize}')
        iv = Ms.indices[pl:pr].view(f'V{ss*Ms.indices.dtype.itemsize}')
        idxi = np.lexsort((dv, iv))
        dv = dv[idxi]
        iv = iv[idxi]
        chng, = np.where(np.concatenate(
            [[True], (dv[1:] != dv[:-1]) | (iv[1:] != iv[:-1]), [True]]))
        counts.append(np.diff(chng))
        idx[gil:gir] = idx[gil:gir][idxi]
    counts = np.concatenate(counts)
    nu = counts.size - 1
    uniques = M@sp.sparse.csc_matrix((np.ones((nu,)), idx[counts[:-1].cumsum()],
                                   np.arange(nu + 1)), (n, nu))
    return uniques, idx, counts[1:]


def safe_tqdm(*args, **kwargs):
    """A decorator to used instead of basic tqdm. Does not raise any error if tqdm package is not installed"""
    if LIB_INSTALLED['tqdm']:
        return tqdm(*args, **kwargs)
    else:
        return args[0]


def slice_list(lst: list, slicer):
    """Slice python list `lst` by any `slicer`"""
    if isinstance(slicer, slice):
        lst = lst[slicer]
    elif isinstance(slicer, Iterable):
        lst = [lst[x] for x in slicer]
    else:
        lst = [lst[slicer]]
    return lst


def get_kwargs_used(kwargs, func):
    """Return `kwargs` which are parameters of `func`"""
    possible_kwargs = inspect.signature(func).parameters
    kwargs_used = {k: v for k, v in kwargs.items() if k in possible_kwargs}
    return kwargs_used


def get_not_none(v, v_if_none):
    return v if v is not None else v_if_none
