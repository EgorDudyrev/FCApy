import pytest
from fcapy.context import converters

@pytest.fixture
def digits_context_data():
    data = [[True, False, True, True, True, True, True],
            [False, False, False, False, False, True, True],
            [True, True, True, False, True, True, False],
            [True, True, True, False, False, True, True],
            [False, True, False, True, False, True, True],
            [True, True, True, True, False, False, True],
            [False, True, True, True, True, False, True],
            [True, False, False, False, False, True, True],
            [True, True, True, True, True, True, True],
            [True, True, False, True, False, True, True]]
    obj_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    attr_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    return data, obj_names, attr_names


def test_read_cxt(digits_context_data):
    data, obj_names, attr_names = digits_context_data
    path = 'data/digits.cxt'

    ctx = converters.read_cxt(path)
    assert ctx.n_objects == len(obj_names),\
        f'Converters.read_cxt failed. n_objects should be equal {len(obj_names)}'
    assert ctx.n_attributes == len(attr_names),\
        f'Converters.read_cxt failed. n_attributes should be equal {len(obj_names)}'
    assert ctx.object_names == obj_names, f'Converters.read_cxt failed. Objects names should be {obj_names}'
    assert ctx.attribute_names == attr_names, f'Converters.read_cxt failed. Attributes names should be {attr_names}'
    assert ctx.data == data, f'Converters.read_cxt failed. Data should be {data}'


def test_to_cxt():
    import os
    path_from = 'data/digits.cxt'
    path_to = 'data/digits_test.cxt'
    with open(path_from, 'r') as f:
        file_from = f.read()

    ctx = converters.read_cxt(path_from)
    assert ctx.to_cxt() == file_from,\
        "Converters.to_cxt failed. The function should return output file text if given path=None"

    converters.to_cxt(ctx, path_to)

    with open(path_to, 'r') as f:
        file_to = f.read()
    os.remove(path_to)
    assert file_from == file_to, f"Converters.to_cxt failed. Output file does not match the input file"
