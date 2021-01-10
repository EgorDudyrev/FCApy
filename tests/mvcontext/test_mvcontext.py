import pytest
from fcapy.mvcontext import mvcontext, pattern_structure as PS
import math


def test_init():
    mvctx = mvcontext.MVContext()

    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    pattern_types = {'0': PS.IntervalPS, '1': PS.IntervalPS}
    mvctx = mvcontext.MVContext(
        data,
        pattern_types=pattern_types,
        description='description'
    )
    assert mvctx.n_objects == 4, "MVContext.__init__ failed"
    assert mvctx.n_attributes == 2, 'MVContext.__init__ failed'
    assert mvctx.object_names == ['0', '1', '2', '3'], 'MVContext.__init__ failed'
    assert mvctx.attribute_names == ['0', '1'], 'MVContext.__init__ failed'
    assert mvctx.description == 'description', 'MVContext.__init__ failed'
    assert mvctx.pattern_types == pattern_types, 'MVContext.__init__ failed'

    ps = [PS.IntervalPS([1, 2, 3, 4], name='0'), PS.IntervalPS([10, 22, 100, 60], name='1')]
    assert mvctx.pattern_structures == ps, 'MVContext.__init__ failed'

    object_names = ['a', 'b', 'c', 'd']
    attribute_names = ['M1', 'M2']
    mvctx = mvcontext.MVContext(
        data,
        pattern_types={'M1': PS.IntervalPS, 'M2': PS.IntervalPS},
        object_names=object_names,
        attribute_names=attribute_names
    )
    assert mvctx.object_names == object_names, 'MVContext.__init__ failed'
    assert mvctx.attribute_names == attribute_names, 'MVContext.__init__ failed'

    with pytest.raises(AssertionError):
        mvcontext.MVContext(data)


def test_extension_intention():
    object_names = ['a', 'b', 'c', 'd']
    attribute_names = ['M1', 'M2']
    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    pattern_types = {'M1': PS.IntervalPS, 'M2': PS.IntervalPS}
    mvctx = mvcontext.MVContext(data, pattern_types, object_names, attribute_names)

    assert mvctx.intention_i([1, 2]) == {0: (2, 3), 1: (22, 100)}, 'MVContext.intention_i failed'
    assert mvctx.extension_i({0: (2, 3), 1: (22, 100)}) == [1, 2], 'MVContext.extension_i failed'
    assert mvctx.intention(['b', 'c']) == {'M1': (2, 3), 'M2': (22, 100)}, 'MVContext.intention failed'
    assert mvctx.extension({'M1': (2, 3), 'M2': (22, 100)}) == ['b', 'c'], 'MVContext.extension failed'


def test_to_json():
    mvctx = mvcontext.MVContext()
    with pytest.raises(NotImplementedError):
        mvctx.to_json()


def test_to_csv():
    mvctx = mvcontext.MVContext()
    with pytest.raises(NotImplementedError):
        mvctx.to_csv()


def test_from_to_pandas():
    import pandas as pd

    mvctx = mvcontext.MVContext()
    with pytest.raises(NotImplementedError):
        mvctx.to_pandas()

    with pytest.raises(NotImplementedError):
        mvctx.from_pandas(pd.DataFrame())


def test_repr():
    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    pattern_types = {'0': PS.IntervalPS, '1': PS.IntervalPS}
    mvctx = mvcontext.MVContext(data, pattern_types)
    assert mvctx.__repr__() == 'MultiValuedContext (4 objects, 2 attributes)'


def test_eq_neq():
    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    data1 = [[1, 10], [2, 22], [3, 100], [4, 61]]
    pattern_types = {'0': PS.IntervalPS, '1': PS.IntervalPS}
    mvctx = mvcontext.MVContext(data, pattern_types)
    mvctx1 = mvcontext.MVContext(data1, pattern_types)

    assert mvctx == mvctx, 'MVContext.__eq__ failed'
    assert mvctx != mvctx1, 'MVContext.__neq__ failed'

    mvctx2 = mvcontext.MVContext(data[:-1], pattern_types)
    with pytest.raises(ValueError):
        mvctx == mvctx2
    with pytest.raises(ValueError):
        mvctx != mvctx2

    mvctx3 = mvcontext.MVContext([r[:-1] for r in data], {'0': PS.IntervalPS})
    with pytest.raises(ValueError):
        mvctx == mvctx3
    with pytest.raises(ValueError):
        mvctx != mvctx3


def test_hash():
    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    pattern_types = {'0': PS.IntervalPS, '1': PS.IntervalPS}
    mvctx = mvcontext.MVContext(data, pattern_types)
    mvctx1 = mvcontext.MVContext(data, pattern_types)
    assert len({mvctx, mvctx1}) == 1, "MVContext.__has__ failed"


def test_getitem():
    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    pattern_types = {'0': PS.IntervalPS, '1': PS.IntervalPS}

    mvctx = mvcontext.MVContext(data, pattern_types)
    assert mvctx[0, 0] == 1, "MVContext.__getitem__ failed."

    mvctx_small = mvcontext.MVContext([row[:2] for row in data[:2]], pattern_types)
    assert mvctx[:2, :2] == mvctx_small, "MVContext.__getitem__ failed"

    mvctx_oneobject = mvcontext.MVContext(data[:1], pattern_types)
    assert mvctx[0] == mvctx_oneobject, "MVContext.__getitem__ failed"
    assert mvctx[[0]] == mvctx_oneobject, "MVContext.__getitem__ failed"

    mvctx_oneattribute = mvcontext.MVContext([row[:1] for row in data], {'0': pattern_types['0']})
    assert mvctx[:, 0] == mvctx_oneattribute, "MVContext.__getitem__ failed"
    assert mvctx[:, [0]] == mvctx_oneattribute, "MVContext.__getitem__ failed"


def test_get_minimal_generators():
    data = [[5.1, 3.5, 1.4, 0.2],
            [4.9, 3. , 1.4, 0.2],
            [4.7, 3.2, 1.3, 0.2],
            [4.6, 3.1, 1.5, 0.2]]
    attribute_names = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
    pattern_types = {f: PS.IntervalPS for f in attribute_names}
    mvctx = mvcontext.MVContext(data=data, pattern_types=pattern_types, attribute_names=attribute_names)

    intent = {0: (4.6, 5.1), 1: (3.0, 3.5), 2: (1.4, 1.5), 3: 0.2}
    mg_true = [{2: (1.4, math.inf)}]
    assert mvctx.get_minimal_generators(intent, use_indexes=True) == mg_true, "MVContext.get_minimal_generators failed"

    # TODO: Find better example for usage of base_generator
    intent = {'sepal length (cm)': (4.6, 5.1), 'sepal width (cm)': (3.1, 3.5),
              'petal length (cm)': (1.4, 1.5), 'petal width (cm)': 0.2}
    mg_base = {'petal length (cm)': (1.4, math.inf)}
    mg_true = [{'sepal width (cm)': (3.1, math.inf), 'petal length (cm)': (1.4, math.inf)}]
    assert mvctx.get_minimal_generators(intent, mg_base) == mg_true, "MVContext.get_minimal_generators failed"
