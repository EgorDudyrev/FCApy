import pytest
from fcapy.context import FormalContext, read_cxt, read_json


@pytest.fixture
def example_context_data():
    data = [[True, True, True],
            [False, True, True],
            [False, False, True]
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


def test_object_attribute_names(example_context_data):
    data, obj_names, attr_names = example_context_data

    ctx = FormalContext(data=data)
    assert ctx.object_names == ['0', '1', '2'],\
        'FormalContext.object_names failed. Default object names should be ["0", "1", "2"]'
    assert ctx.attribute_names == ['0', '1', '2'], \
        'FormalContext.attribute_names failed. Default attribute names should be ["0", "1", "2"]'

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


def test_n_objects(example_context_data):
    data = example_context_data[0]
    ctx = FormalContext()
    assert ctx.n_objects is None, 'FormalContext.n_objects failed. Should be None since no data in the context'

    ctx = FormalContext(data=data)
    assert ctx.n_objects == 3, 'FormalContext.n_objects failed. Should be 3 since data has 3 lines'

    with pytest.raises(AttributeError):
        ctx.n_objects = 4


def test_n_attributes(example_context_data):
    data = example_context_data[0]
    ctx = FormalContext()
    assert ctx.n_attributes is None, 'FormalContext.n_attributes failed. Should be None since no data in the context'

    ctx = FormalContext(data=data)
    assert ctx.n_attributes == 3,\
        'FormalContext.n_attributes failed. Should be 3 since each line in data is of length 3'

    with pytest.raises(AttributeError):
        ctx.n_attributes = 4


def test_to_cxt():
    path = 'data/digits.cxt'
    with open(path, 'r') as f:
        file_orig = f.read()

    ctx = read_cxt(path)
    file_new = ctx.to_cxt()
    assert file_new == file_orig, 'FormalContext.to_ext failed. Result context file does not math the initial one'


def test_to_json():
    path = 'data/animal_movement.json'
    with open(path, 'r') as f:
        file_orig = f.read()

    ctx = read_json(path)
    file_new = ctx.to_json()
    assert file_new == file_orig, 'FormalContext.to_ext failed. Result context file does not math the initial one'