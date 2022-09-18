import pytest
from fcapy.mvcontext import mvcontext, pattern_structure as PS
from fcapy.lattice.concept_lattice import ConceptLattice
import math
from frozendict import frozendict
from fcapy import LIB_INSTALLED
import numpy as np
from sklearn.datasets import load_breast_cancer


def test_init():
    mvctx = mvcontext.MVContext()

    for np_instld in [False, True]:
        LIB_INSTALLED['numpy'] = np_instld

        data_input = [[1, 10], [2, 22], [3, 100], [4, 60]]
        data_hidden = [[(1, 1), (10, 10)], [(2, 2), (22, 22)], [(3, 3), (100, 100)], [(4, 4), (60, 60)]]
        pattern_types = {'0': PS.IntervalPS, '1': PS.IntervalPS}
        mvctx = mvcontext.MVContext(
            data_input,
            pattern_types=pattern_types,
            description='description'
        )
        assert mvctx.n_objects == 4, "MVContext.__init__ failed"
        assert mvctx.n_attributes == 2, 'MVContext.__init__ failed'
        assert mvctx.object_names == ['0', '1', '2', '3'], 'MVContext.__init__ failed'
        assert mvctx.attribute_names == ['0', '1'], 'MVContext.__init__ failed'
        assert mvctx.description == 'description', 'MVContext.__init__ failed'
        assert mvctx.pattern_types == pattern_types, 'MVContext.__init__ failed'
        if not np_instld:
            assert mvctx.data == data_hidden, "MVContext.__init__ failed"
        else:
            assert np.all(mvctx.data == np.array(data_hidden)), "MVContext.__init__ failed"

    ps = [PS.IntervalPS([1, 2, 3, 4], name='0'), PS.IntervalPS([10, 22, 100, 60], name='1')]
    assert mvctx.pattern_structures == ps, 'MVContext.__init__ failed'

    object_names = ['a', 'b', 'c', 'd']
    attribute_names = ['M1', 'M2']
    mvctx = mvcontext.MVContext(
        data_input,
        pattern_types={'M1': PS.IntervalPS, 'M2': PS.IntervalPS},
        object_names=object_names,
        attribute_names=attribute_names
    )
    assert mvctx.object_names == object_names, 'MVContext.__init__ failed'
    assert mvctx.attribute_names == attribute_names, 'MVContext.__init__ failed'

    with pytest.raises(AssertionError):
        mvcontext.MVContext(data_input)


def test_extension_intention():
    object_names = ['a', 'b', 'c', 'd']
    attribute_names = ['M1', 'M2']
    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    pattern_types = {'M1': PS.IntervalPS, 'M2': PS.IntervalPS}

    intent_i_true = {0: (2, 3), 1: (22, 100)}
    intent_true = {'M1': (2, 3), 'M2': (22, 100)}
    extent_i_true = [1, 2]
    extent_true = ['b', 'c']

    for x in [False, True]:
        LIB_INSTALLED['numpy'] = x
        mvctx = mvcontext.MVContext(data, pattern_types, object_names, attribute_names)

        if x:
            extent_i_true = np.array(extent_i_true)
            assert (mvctx.extension_i({0: (2, 3), 1: (22, 100)}) == extent_i_true).all(), 'MVContext.extension_i failed'
            assert (mvctx.extension_i({0: (2, 3), 1: (22, 100)}, frozenset([0, 1, 2, 3])) == extent_i_true).all()
            assert (mvctx.extension_i({0: (2, 3), 1: (22, 100)}, [0, 1, 2, 3]) == extent_i_true).all()
            assert (mvctx.extension_i({0: (2, 3), 1: (22, 100)}, np.array([0, 1, 2, 3])) == extent_i_true).all()
        else:
            extent_i_true = list(extent_i_true)
            assert mvctx.extension_i({0: (2, 3), 1: (22, 100)}) == extent_i_true, 'MVContext.extension_i failed'
            assert mvctx.extension_i({0: (2, 3), 1: (22, 100)}, [0, 1, 2, 3]) == extent_i_true
            assert mvctx.extension_i({0: (2, 3), 1: (22, 100)}, frozenset([0, 1, 2, 3])) == extent_i_true

        assert mvctx.intention_i([1, 2]) == intent_i_true, 'MVContext.intention_i failed'
        assert mvctx.intention(['b', 'c']) == intent_true, 'MVContext.intention failed'
        assert mvctx.extension({'M1': (2, 3), 'M2': (22, 100)}) == extent_true, 'MVContext.extension failed'


def test_read_write_json():
    object_names = ['a', 'b', 'c', 'd']
    attribute_names = ['M1', 'M2']
    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    pattern_types = {'M1': PS.IntervalPS, 'M2': PS.IntervalPS}

    mvK = mvcontext.MVContext(data, pattern_types, object_names, attribute_names)
    mvK_json = mvK.read_json(json_data=mvK.write_json())
    assert mvK == mvK_json, 'MVContext.read/write_json failed'

    path = 'test.json'
    mvK.write_json(path)
    mvK_new = mvK.read_json(path)
    assert mvK == mvK_new,\
        'MVContext.read/write_json failed. The lattice changed after 2 conversions and saving to file.'
    import os
    os.remove(path)


def test_read_csv():
    mvctx = mvcontext.MVContext()
    with pytest.raises(NotImplementedError):
        mvctx.read_csv()


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
    assert mvctx.__repr__() == 'ManyValuedContext (4 objects, 2 attributes)'


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


def test_len():
    data = load_breast_cancer(as_frame=True)
    X = data['data'].values[:20]
    Y = data['target'].values[:20]
    feature_names = [str(f) for f in data['feature_names']]

    pattern_types = {f: PS.IntervalPS for f in feature_names}
    mvctx = mvcontext.MVContext(data=X, target=Y, pattern_types=pattern_types, attribute_names=feature_names)
    assert len(mvctx) == len(X)


def test_getitem():
    data = [[1, 10], [2, 22], [3, 100], [4, 60]]
    pattern_types = {'0': PS.IntervalPS, '1': PS.IntervalPS}

    mvctx = mvcontext.MVContext(data, pattern_types)
    assert tuple(mvctx[0, 0]) == (1, 1), "MVContext.__getitem__ failed."

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

    for x in [False, True]:
        LIB_INSTALLED['numpy'] = x

        pattern_types = {f: PS.IntervalPS for f in attribute_names}
        mvctx = mvcontext.MVContext(data=data, pattern_types=pattern_types, attribute_names=attribute_names)

        intent = {0: (4.6, 5.1), 1: (3.0, 3.5), 2: (1.4, 1.5), 3: 0.2}
        mg_true = {frozendict({2: (1.4, math.inf)})}
        assert set(mvctx.get_minimal_generators(intent, use_indexes=True)) == mg_true,\
            "MVContext.get_minimal_generators failed"

        intent = {'sepal length (cm)': (4.6, 5.1), 'sepal width (cm)': (3.0, 3.5),
                  'petal length (cm)': (1.4, 1.5), 'petal width (cm)': 0.2}
        mg_true = {frozendict({'petal length (cm)': (1.4, math.inf)})}
        assert set(mvctx.get_minimal_generators(intent, base_objects=['0', '1', '2', '3'])) == mg_true,\
            "MVContext.get_minimal_generators failed"

    # TODO: Find better example for usage of base_generator
    intent = {'sepal length (cm)': (4.6, 5.1), 'sepal width (cm)': (3.1, 3.5),
              'petal length (cm)': (1.4, 1.5), 'petal width (cm)': 0.2}
    mg_base = {'petal length (cm)': (1.4, math.inf)}
    mg_true = {frozendict({'sepal width (cm)': (3.1, math.inf), 'petal length (cm)': (1.4, math.inf)})}
    assert set(mvctx.get_minimal_generators(intent, mg_base)) == mg_true, "MVContext.get_minimal_generators failed"

    ltc = ConceptLattice.from_context(mvctx)
    for c in ltc:
        mvctx.get_minimal_generators(c.intent)


def test_generators_by_intent_difference():
    data = load_breast_cancer(as_frame=True)
    X = data['data'].values
    Y = data['target'].values
    feature_names = [str(f) for f in data['feature_names']]

    pattern_types = {f: PS.IntervalPS for f in feature_names}
    mvctx = mvcontext.MVContext(data=X, target=Y, pattern_types=pattern_types, attribute_names=feature_names)[:20]
    ltc = ConceptLattice.from_context(mvctx, algo='Sofia', L_max=100, use_tqdm=True)
    c_i = 3
    subc_i = sorted(ltc.children_dict[c_i])[0]
    mg1 = mvctx.generators_by_intent_difference(ltc[subc_i].intent_i, ltc[c_i].intent_i)
    mg2 = mvctx.get_minimal_generators(ltc[subc_i].intent_i, base_objects=list(ltc[c_i].extent_i),
                                       use_indexes=True)

    assert set(mg1) == set(mg2), "MVContext.generators_by_intent_difference failed"
