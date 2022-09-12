import pytest
import numpy as np
from fcapy.context import bintable_new as btables
from .data_to_test import animal_movement_data
from fcapy import LIB_INSTALLED


def test_abstract_class():
    with pytest.raises(TypeError):
        btables.AbstractBinTable()


def test_init(animal_movement_data):
    btables.BinTableLists()

    data = animal_movement_data['data']

    bt = btables.BinTableLists(data)

    # test properties
    assert bt.to_lists() == data, 'BinTable.data failed. Data values were changed while initialization'
    assert bt.height == len(data), 'BinTable.height failed'
    assert bt.width == len(data[0]), 'BinTable.width failed'
    assert bt.shape == (len(data), len(data[0])), 'BinTable.shape failed'

    with pytest.raises(btables.NotBooleanValueError):
        btables.BinTableLists([[1, False], [True, True]])

    with pytest.raises(btables.UnknownDataTypeError):
        btables.BinTableLists({9, 1, 2, 3})

    with pytest.raises(btables.UnmatchedLengthError):
        btables.BinTableLists([[True, True], [False, ]])


def test_to_lists():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    bt = btables.BinTableLists(data)
    assert bt.to_lists() == data


def test_to_tuples():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    bt = btables.BinTableLists(data)
    assert bt.to_tuples() == tuple([tuple(row) for row in data])


def test_hash():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    bt1 = btables.BinTableLists(data)
    bt2 = btables.BinTableLists(data[:-1])
    bt3 = btables.BinTableLists(data)
    set_big = {bt1, bt2, bt3}
    set_small = {bt1, bt2}
    assert set_big == set_small, 'BinTable.__hash__ failed'


def test_all():
    data = [[False, False], [False, True], [True, True]]
    data_np = np.array(data)

    bt = btables.BinTableLists(data)
    assert bt.all() == data_np.all()
    for ax in [0, 1]:
        assert bt.all(ax) == list(data_np.all(ax))

    with pytest.raises(btables.UnknownAxisError):
        bt.all(42)


def test_any():
    data = [[False, False], [False, True], [True, True]]
    data_np = np.array(data)

    bt = btables.BinTableLists(data)
    assert bt.any() == data_np.any()
    for ax in [0, 1]:
        assert bt.any(ax) == list(data_np.any(ax))

    with pytest.raises(btables.UnknownAxisError):
        bt.any(42)


def test_sum():
    data = [[False, False], [False, True], [True, True]]
    data_np = np.array(data)

    bt = btables.BinTableLists(data)
    assert bt.sum() == data_np.sum()
    for ax in [0, 1]:
        assert bt.sum(ax) == list(data_np.sum(ax))

    with pytest.raises(btables.UnknownAxisError):
        bt.sum(42)
