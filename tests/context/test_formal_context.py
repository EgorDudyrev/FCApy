import pytest
from fcapy.context import FormalContext


@pytest.fixture
def example_context_data():
    data = [[1, 1, 1],
            [0, 1, 1],
            [0, 0, 1]
            ]
    obj_names = ['g1', 'g2', 'g3']
    attr_names = ['m1', 'm2', 'm3']
    return data, obj_names, attr_names


def test_data_property(example_context_data):
    ctx = FormalContext()

    data = example_context_data[0]
    ctx = FormalContext(data=data)
    data_ = ctx.data
    assert data == data_, 'FormalContext.data has changed the initial data'

    with pytest.raises(AssertionError):
        FormalContext(data=[])

    with pytest.raises(AssertionError):
        FormalContext(data=[[0], [1, 2]])


def test_attribute_names(example_context_data):
    data, obj_names, attr_names = example_context_data
    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    assert ctx.object_names == obj_names, 'FormalContext.object_names has changed the initial object_names'
    assert ctx.attribute_names == attr_names, 'FormalContext.attribute_names has changed the initial attribute_names'

    with pytest.raises(AssertionError):
        ctx.attribute_names = []
    with pytest.raises(AssertionError):
        ctx.object_names = [1, 2]


def test_intent_extent_i(example_context_data):
    data = example_context_data[0]
    ctx = FormalContext(data=data)
    ext_ = ctx.extension_i([0, 1])
    assert set(ext_) == {0}, 'FormalContext.extension_i failed. Should be {0}'

    int_ = ctx.intention_i([0, 1])
    assert set(int_) == {1, 2}, 'FormalContext.intention_i failed. Should be {1,2}'

    assert ctx.intention_i(ctx.extension_i(int_)) == int_,\
        'Basic FCA theorem failed. Check FormalContext.extension_i, intention_i'


def test_intent_extent(example_context_data):
    data, obj_names, attr_names = example_context_data
    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    ext_ = ctx.extension(['m1', 'm2'])
    assert set(ext_) == {'g1'}, 'FormalContext.extension_i failed. Should be {"m1"}'

    int_ = ctx.intention(['g1', 'g2'])
    assert set(int_) == {'m2', 'm3'}, 'FormalContext.intention failed. Should be {"m2","m3"}'

    assert ctx.intention(ctx.extension(int_)) == int_,\
        'Basic FCA theorem failed. Check FormalContext.extension, intention'

    with pytest.raises(KeyError):
        ctx.intention(['d1'])
    with pytest.raises(KeyError):
        ctx.extension((['z93']))
