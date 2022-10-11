import pytest
import os
from operator import itemgetter
import filecmp

from fcapy.context import FormalContext, read_cxt, read_json, read_csv, from_pandas
from fcapy.lattice.concept_lattice import ConceptLattice
from .data_to_test import animal_movement_data


def test_data_property(animal_movement_data):
    K = FormalContext()
    assert K.data.to_list() == [], 'FormalContext.data failed'

    data = animal_movement_data['data']
    K = FormalContext(data)
    assert K.data.to_list() == data, 'FormalContext.data has changed the initial data'

    with pytest.raises(ValueError):
        FormalContext(data=[[0], [1, 2]])


def test_object_attribute_names(animal_movement_data):
    data, obj_names, attr_names = itemgetter('data', 'obj_names', 'attr_names')(animal_movement_data)

    ctx = FormalContext(data=data)
    obj_names_default = tuple([str(idx) for idx in range(len(obj_names))])
    assert ctx.object_names == obj_names_default,\
        f'FormalContext.object_names failed. Default object names should be {obj_names_default}'
    attr_names_default = tuple([str(idx) for idx in range(len(attr_names))])
    assert ctx.attribute_names == attr_names_default, \
        f'FormalContext.attribute_names failed. Default attribute names should be {attr_names_default}'

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    assert ctx.object_names == obj_names, 'FormalContext.object_names has changed the initial object_names'
    assert ctx.attribute_names == attr_names, 'FormalContext.attribute_names has changed the initial attribute_names'

    with pytest.raises(AssertionError):
        ctx.attribute_names = []
    with pytest.raises(AssertionError):
        ctx.object_names = [1, 2]


def test_intent_extent_i(animal_movement_data):
    data = animal_movement_data['data']
    ctx = FormalContext(data=data)
    ext_ = ctx.extension_i([0, 1])
    assert set(ext_) == {4, 5, 6}, 'FormalContext.extension_i failed. Should be {4, 5, 6}'

    int_ = ctx.intention_i([4, 5, 6])
    assert set(int_) == {0, 1}, 'FormalContext.intention_i failed. Should be {0, 1}'

    assert ctx.intention_i(ctx.extension_i(int_)) == int_,\
        'Basic FCA theorem failed. Check FormalContext.extension_i, intention_i'

    assert ctx.extension_i([]) == list(range(ctx.n_objects))
    assert ctx.intention_i([]) == list(range(ctx.n_attributes))


def test_intent_extent_i_monotone(animal_movement_data):
    data = animal_movement_data['data']
    ctx = FormalContext(data=data)

    assert ctx.extension_monotone_i([0]) == ctx.extension_i([0])

    assert set(ctx.extension_monotone_i([0, 1])) == {g_i for m_i in [0, 1] for g_i in ctx.extension_monotone_i([m_i])}

    int_ = ctx.intention_monotone_i([2, 3])
    assert set(int_) == {3}, 'FormalContext.intention_i failed. Should be {3}}'

    int_ = [0, 1, 3]
    assert ctx.intention_monotone_i(ctx.extension_monotone_i(int_)) == int_, \
        'Basic FCA theorem failed. Check FormalContext.extension_i, intention_i'

    assert ctx.extension_monotone_i([]) == []
    assert ctx.intention_monotone_i([]) == []
    assert ctx.extension_monotone_i(list(range(ctx.n_attributes))) == list(range(ctx.n_objects))
    assert ctx.intention_monotone_i(list(range(ctx.n_objects))) == list(range(ctx.n_attributes))


def test_intent_extent(animal_movement_data):
    data, obj_names, attr_names = itemgetter('data', 'obj_names', 'attr_names')(animal_movement_data)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    ext_ = ctx.extension(['fly', 'hunt'])
    assert set(ext_) == {'owl', 'hawk', 'eagle'}, 'FormalContext.extension failed. Should be {"owl", "hawk", "eagle"}'

    int_ = ctx.intention(['owl', 'hawk', 'eagle'])
    assert set(int_) == {'fly', 'hunt'}, 'FormalContext.intention failed. Should be {"fly","hunt"}'

    assert ctx.intention(ctx.extension(int_)) == int_,\
        'Basic FCA theorem failed. Check FormalContext.extension, intention'

    with pytest.raises(KeyError):
        ctx.intention(['d1'])
    with pytest.raises(KeyError):
        ctx.extension((['z93']))

    K = FormalContext(data=[[True, True, False],
                            [False, True, False]])
    assert K.intention('0') == ['0', '1']
    assert K.intention('1') == ['1']
    assert K.extension('0') == ['0']
    assert K.extension('1') == ['0', '1']
    assert K.extension('2') == []

    ext_ = ['dove', 'duck', 'goose', 'owl', 'hawk', 'eagle', 'fox', 'wolf', 'cat', 'tiger', 'lion']
    assert ctx.extension(['fly', 'hunt'], is_monotone=True) == ext_
    assert ctx.intention(['duck', 'goose'], is_monotone=True) == ['swim']


def test_n_objects(animal_movement_data):
    data, obj_names = itemgetter('data', 'obj_names')(animal_movement_data)

    ctx = FormalContext()
    assert ctx.n_objects == 0, 'FormalContext.n_objects failed. Should be 0 since no data in the context'

    ctx = FormalContext(data=data)
    assert ctx.n_objects == len(obj_names), f'FormalContext.n_objects failed. '\
                                            + f'Should be {len(obj_names)} since data has {len(obj_names)} lines'

    with pytest.raises(AttributeError):
        ctx.n_objects = 42


def test_n_attributes(animal_movement_data):
    data, attr_names = itemgetter('data', 'attr_names')(animal_movement_data)
    ctx = FormalContext()
    assert ctx.n_attributes == 0, 'FormalContext.n_attributes failed. Should be 0 since no data in the context'

    ctx = FormalContext(data=data)
    assert ctx.n_attributes == len(attr_names),\
        f'FormalContext.n_attributes failed. '\
        + f'Should be {len(attr_names)} since each line in data is of length {(len(attr_names))}'

    with pytest.raises(AttributeError):
        ctx.n_attributes = 42


def test_description():
    ctx = FormalContext()
    ctx.description = 'Test description'
    assert ctx.description == 'Test description',\
        'FormalContext.description failed. The description differs from the given "Test description"'

    with pytest.raises(AssertionError):
        ctx.description = 42


def test_read_write_funcs(animal_movement_data):
    path = animal_movement_data['path']
    for file_extension in ['.cxt', '.json', '.csv']:
        fnc_read = {
            '.cxt': FormalContext.read_cxt,
            '.json': FormalContext.read_json,
            '.csv': FormalContext.read_csv
        }[file_extension]

        path_ext = path+file_extension

        with open(path_ext, 'r') as f:
            file_orig = f.read()

        ctx = fnc_read(path_ext)

        fnc_write = {
            '.cxt': ctx.write_cxt,
            '.json': ctx.write_json,
            '.csv': ctx.write_csv
        }[file_extension]

        fnc_name = fnc_write.__name__

        file_new = fnc_write()
        assert file_new == file_orig,\
            f'FormalContext.{fnc_name} failed. Result context file does not math the initial one'

        tmp_path = 'tmp_data'+file_extension
        fnc_write(tmp_path)
        assert filecmp.cmp(path_ext, tmp_path),\
            f'FormalContext.{fnc_name} failed. Saved file differs from the original one'
        os.remove(tmp_path)


def test_to_from_pandas(animal_movement_data):
    data, obj_names, attr_names = \
        itemgetter('data', 'obj_names', 'attr_names')(animal_movement_data)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    assert from_pandas(ctx.to_pandas()) == ctx,\
        'FormalContext.to_pandas failed. Double converted FormalContext does not match the initial one'

    assert FormalContext.from_pandas(ctx.to_pandas()),\
        'FormalContext.from_pandas failed. Double converted FormalContext does not match initial one'


def test_print_data(animal_movement_data):
    data, obj_names, attr_names, printed_data_short = \
        itemgetter('data', 'obj_names', 'attr_names', 'printed_data_short')(animal_movement_data)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    s = ctx.print_data(max_n_objects=4, max_n_attributes=2)
    assert s == printed_data_short, 'FormalContext.print_data failed. Check data formatting.'


def test_repr(animal_movement_data):
    data, obj_names, attr_names, repr_data = \
        itemgetter('data', 'obj_names', 'attr_names', 'repr_data')(animal_movement_data)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    s = ctx.__repr__()
    assert s == repr_data, "FormalContext.__repr__ failed. '" \
                           + "Check print_data parameters: max_n_objects=20, max_n_attributes=10."


def test_eq_neq(animal_movement_data):
    data, obj_names, attr_names = itemgetter('data', 'obj_names', 'attr_names')(animal_movement_data)
    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)

    for func in [ctx.__eq__, ctx.__ne__]:
        ctx_neq = FormalContext(data=data[:-1], object_names=obj_names[:-1], attribute_names=attr_names)
        with pytest.raises(ValueError) as excinfo:
            func(ctx_neq)
        msg = 'Two FormalContext objects can not be compared since they have different object_names'
        assert excinfo.value.args[0] == msg,\
            f'FormalContext.{func.__name__} failed. ' + \
            f'Error message when comparing object_names differs from the expected one'

        ctx_neq = FormalContext(data=[g_ms[:-1] for g_ms in data],
                                object_names=obj_names, attribute_names=attr_names[:-1])
        with pytest.raises(ValueError) as excinfo:
            func(ctx_neq)
        msg = 'Two FormalContext objects can not be compared since they have different attribute_names'
        assert excinfo.value.args[0] == msg,\
            f'FormalContext.{func.__name__} failed. ' +\
            'Error message when comparing attribute_names differs from the expected one'

    ctx_eq = FormalContext(data=[g_ms for g_ms in data], object_names=obj_names, attribute_names=attr_names)

    ctx_neq = FormalContext(data=[g_ms[:-1]+[not g_ms[-1]] for g_ms in data], object_names=obj_names,
                            attribute_names=attr_names)

    assert ctx == ctx_eq, 'FormalContext.__eq__ failed. The same FormalContext objects are classified as different'
    assert not ctx == ctx_neq,\
        'FormalContext.__eq__ failed. Two different FormalContext objects are classified as the same'
    assert ctx != ctx_neq,\
        'FormalContext.__ne__ failed. Two different FormalContext objects do not classified as different'
    assert not ctx != ctx_eq,\
        'FormalContext.__ne__ failed. The same FormalContext objects are classified as different'


def test_len():
    data = [[False, True, True], [False, False, True], [False, False, True]]
    ctx = FormalContext(data)
    assert len(ctx) == 3


def test_transpose():
    data = [[False, True, True], [False, False, True], [False, False, True]]
    K = FormalContext(data)
    assert K.T.T == K


def test_getitem():
    data = [[False, True, True], [False, False, True], [False, False, True]]
    ctx = FormalContext(data)
    assert ctx[0, 0] is False, "FormalContext.__getitem__ failed."

    ctx_small = FormalContext([row[:2] for row in data[:2]])
    assert ctx[:2, :2] == ctx_small, "FormalContext.__getitem__ failed"

    ctx_oneobject = FormalContext(data[:1])
    assert ctx[:1] == ctx_oneobject, "FormalContext.__getitem__ failed"
    assert ctx[[0]] == ctx_oneobject, "FormalContext.__getitem__ failed"

    ctx_oneattribute = FormalContext([row[:1] for row in data])
    assert ctx[:, :1] == ctx_oneattribute, "FormalContext.__getitem__ failed"
    assert ctx[:, [0]] == ctx_oneattribute, "FormalContext.__getitem__ failed"


def test_get_minimal_generators():
    ctx = read_csv('data/mango_bin.csv')
    int_ = ['fruit', 'color_is_yellow', 'form_is_round']
    min_gens = ctx.get_minimal_generators(int_, use_indexes=False)
    assert min_gens == [('color_is_yellow',)], "FormalContext.get_minimal_generators failed"

    min_gens = ctx.get_minimal_generators(int_, base_generator=['form_is_round'], use_indexes=False)
    assert set(min_gens) == {('color_is_yellow', 'form_is_round'), ('fruit', 'form_is_round')},\
        "FormalContext.get_minimal_generators failed"

    ltc = ConceptLattice.from_context(ctx)
    for c in ltc:
        ctx.get_minimal_generators(c.intent)


def test_invert():
    ctx = read_csv('data/mango_bin.csv')
    assert ~~ctx == ctx, 'FormalContext.__invert__ failed'

