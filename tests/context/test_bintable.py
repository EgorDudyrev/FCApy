import pytest
import numpy as np
from fcapy.context import bintable as btables
from fcapy.context import bintable_errors as berrors
from .data_to_test import animal_movement_data


def test_abstract_class():
    with pytest.raises(TypeError):
        btables.AbstractBinTable()


def test_init(animal_movement_data):
    for BTClass in btables.BINTABLE_CLASSES.values():
        BTClass()

    data = animal_movement_data['data']

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)

        # test properties
        assert bt.to_list() == data, 'BinTable.data failed. Data values were changed while initialization'
        assert bt.height == len(data), 'BinTable.height failed'
        assert bt.width == len(data[0]), 'BinTable.width failed'
        assert bt.shape == (len(data), len(data[0])), 'BinTable.shape failed'

        with pytest.raises(berrors.NotBooleanValueError):
            BTClass([[1, False], [True, True]])
        with pytest.raises(berrors.UnknownDataTypeError):
            BTClass({9, 1, 2, 3})
        with pytest.raises(berrors.UnmatchedLengthError):
            BTClass([[True, True], [False, ]])


def test_to_lists():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)
        assert bt.to_list() == data


def test_to_tuples():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)
        assert bt.to_tuple() == tuple([tuple(row) for row in data])


def test_hash():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt1 = BTClass(data)
        bt2 = BTClass(data[:-1])
        bt3 = BTClass(data)
        set_big = {bt1, bt2, bt3}
        set_small = {bt1, bt2}
        assert set_big == set_small, 'BinTable.__hash__ failed'


def test_all():
    data = [[False, False], [False, True], [True, True]]
    data_np = np.array(data)

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)

        assert bt.all() == data_np.all()
        for ax in [0, 1]:
            assert list(bt.all(ax)) == list(data_np.all(ax))

        with pytest.raises(berrors.UnknownAxisError):
            bt.all(42)


def test_all_i():
    data = [[False, False], [False, True], [True, True]]
    data_np = np.array(data)

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)

        for ax in [0, 1]:
            assert list(bt.all_i(ax)) == list(data_np.all(ax).nonzero()[0])

        with pytest.raises(berrors.UnknownAxisError):
            bt.all(42)


def test_any():
    data = [[False, False], [False, True], [True, True]]
    data_np = np.array(data)

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)
        assert bt.any() == data_np.any()
        for ax in [0, 1]:
            assert list(bt.any(ax)) == list(data_np.any(ax))

        with pytest.raises(berrors.UnknownAxisError):
            bt.any(42)


def test_any_i():
    data = [[False, False], [False, True], [True, True]]
    data_np = np.array(data)

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)
        for ax in [0, 1]:
            assert list(bt.any_i(ax)) == list(data_np.any(ax).nonzero()[0])

        with pytest.raises(berrors.UnknownAxisError):
            bt.any(42)


def test_sum():
    data = [[False, False], [False, True], [True, True]]
    data_np = np.array(data)

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)
        assert bt.sum() == data_np.sum()
        for ax in [0, 1]:
            assert list(bt.sum(ax)) == list(data_np.sum(ax))

        with pytest.raises(berrors.UnknownAxisError):
            bt.sum(42)


def test_interchangeability():
    data = [[False, False], [False, True], [True, True]]

    for BTClass_A in btables.BINTABLE_CLASSES.values():
        for BTClass_B in btables.BINTABLE_CLASSES.values():
            bt_a = BTClass_A(data)
            bt_b = BTClass_B(bt_a.data)
            assert bt_a.to_list() == bt_b.to_list()


def test_getitem():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    for BTClass in btables.BINTABLE_CLASSES.values():
        bt = BTClass(data)

        assert bt[0, 0] is False, f"{BTClass}.__getitem__ failed."

        bt_small = BTClass([row[:2] for row in data[:2]])
        assert bt[:2, :2] == bt_small, f"{BTClass}.__getitem__ failed"

        bt_onerow = BTClass(data[:1])
        assert bt[:1] == bt_onerow, f"{BTClass}.__getitem__ failed"
        assert bt[[0]] == bt_onerow, f"{BTClass}.__getitem__ failed"

        bt_onecolumn = BTClass([row[:1] for row in data])
        assert bt[:, :1] == bt_onecolumn, f"{BTClass}.__getitem__ failed"
        assert bt[:, [0]] == bt_onecolumn, f"{BTClass}.__getitem__ failed"

        output = bt[0]
        assert tuple(output) == tuple(data[0]), f"{BTClass}.__getitem__ failed"
        output = bt[:, 0]
        assert tuple(output) == tuple([row[0] for row in data]), f"{BTClass}.__getitem__ failed"


def test_and():
    data1 = [[False, True, True], [False, False, True], [False, False, True]]
    data2 = [[True, False, True], [False, False, False], [True, False, True]]
    data_and = [[False, False, True], [False, False, False], [False, False, True]]

    for class_name, BTClass in btables.BINTABLE_CLASSES.items():
        bt1 = BTClass(data1)
        bt2 = BTClass(data2)
        bt_and = BTClass(data_and)

        assert bt1 & bt2 == bt_and, f"{class_name}.__and__ failed"


def test_or():
    data1 = [[False, True, True], [False, False, True], [False, False, True]]
    data2 = [[True, False, True], [False, False, False], [True, False, True]]
    data_or = [[True, True, True], [False, False, True], [True, False, True]]

    for class_name, BTClass in btables.BINTABLE_CLASSES.items():
        bt1 = BTClass(data1)
        bt2 = BTClass(data2)
        bt_or = BTClass(data_or)

        assert bt1 | bt2 == bt_or, f"{class_name}.__or__ failed"


def test_invert():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    for class_name, BTClass in btables.BINTABLE_CLASSES.items():
        bt = BTClass(data)
        assert ~~bt == bt,  f"{class_name}.__invert__ failed"


def test_transpose():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    for class_name, BTClass in btables.BINTABLE_CLASSES.items():
        bt = BTClass(data)
        assert bt.T.T == bt, f"{class_name}.T failed"


def test_init_bintable():
    data = [[False, True, True], [False, False, True], [False, False, True]]

    for class_name, BTClass in btables.BINTABLE_CLASSES.items():
        assert BTClass(data) == btables.init_bintable(data, class_name)

    assert type(btables.init_bintable(data)) == btables.BINTABLE_CLASSES['BinTableBitarray']
