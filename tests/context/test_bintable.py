import pytest
from fcapy.context.bintable import BinTable
from .data_to_test import animal_movement_data


def test_init(animal_movement_data):
    BinTable()

    data = animal_movement_data['data']
    bt = BinTable(data)

    # test properties
    assert bt.data == data, 'BinTable.data failed. Data was changed while initialization'
    assert bt.height == len(data), 'BinTable.height failed'
    assert bt.width == len(data[0]), 'BinTable.width failed'
    assert bt.shape == (len(data), len(data[0])), 'BinTable.shape failed'


def test_getitem():
    data = [[False, True, True], [False, False, True], [False, False, True]]
    bt = BinTable(data)
    assert bt[0, 0] is False, "BinTable.__getitem__ failed."

    bt_small = BinTable([row[:2] for row in data[:2]])
    assert bt[:2, :2] == bt_small, "BinTable.__getitem__ failed"

    bt_onerow = BinTable(data[:1])
    assert bt[:1] == bt_onerow, "BinTable.__getitem__ failed"
    assert bt[[0]] == bt_onerow, "BinTable.__getitem__ failed"

    bt_onecolumn = BinTable([row[:1] for row in data])
    assert bt[:, :1] == bt_onecolumn, "BinTable.__getitem__ failed"
    assert bt[:, [0]] == bt_onecolumn, "BinTable.__getitem__ failed"

    assert bt[0] == data[0], "BinTable.__getitem__ failed"
    assert bt[:, 0] == [row[0] for row in data], "BinTable.__getitem__ failed"


def test_to_list():
    data = [[False, True, True], [False, False, True], [False, False, True]]
    bt = BinTable(data)
    assert bt.to_list() == data, 'BinTable.to_list() failed'


def test_eq():
    data = [[False, True, True], [False, False, True], [False, False, True]]
    bt1 = BinTable(data)
    bt2 = BinTable(data[:-1])
    bt3 = BinTable(data)
    assert bt1 != bt2, 'BinTable.__eq__ failed'
    assert bt1 == bt3, 'BinTable.__eq__ failed'


def test_hash():
    data = [[False, True, True], [False, False, True], [False, False, True]]
    bt1 = BinTable(data)
    bt2 = BinTable(data[:-1])
    bt3 = BinTable(data)
    set_big = {bt1, bt2, bt3}
    set_small = {bt1, bt2}
    assert set_big == set_small, 'BinTable.__hash__ failed'


def test_all_any():
    data = [[False, False], [False, True], [True, True]]
    bt = BinTable(data)
    assert not bt.all()
    assert bt.any()
    assert bt[[2]].all()
    assert not bt[[0]].any()

    assert bt.all(0) == [False, False]
    assert bt.any(0) == [True, True]

    assert bt[1:].all(1) == [False, True]
    assert bt[:2].any(1) == [False, True]

    with pytest.raises(ValueError):
        bt.all(2)

    with pytest.raises(ValueError):
        bt.any(2)

    # weird thing for numpy compatibility
    assert bt[:0].all()
    assert bt[:0].all(0) == [True, True]
    assert bt[:0].all(1) == []
    assert bt[:, :0].all()
    assert bt[:, :0].all(0) == []
    assert bt[:, :0].all(1) == [True, True, True]

    assert not bt[:0].any()
    assert bt[:0].any(0) == [False, False]
    assert bt[:0].any(1) == []
    assert not bt[:, :0].any()
    assert bt[:, :0].any(0) == []
    assert bt[:, :0].any(1) == [False, False, False]
