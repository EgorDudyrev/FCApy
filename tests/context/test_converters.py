import pytest
from fcapy.context import converters


@pytest.fixture
def animal_movement_data():
    data = [[True, False, False, False],
            [False, False, False, False],
            [True, False, False, True],
            [True, False, False, True],
            [True, True, False, False],
            [True, True, False, False],
            [True, True, False, False],
            [False, True, True, False],
            [False, False, True, False],
            [False, True, True, False],
            [False, True, True, False],
            [False, True, True, False],
            [False, True, True, False],
            [False, False, True, False],
            [False, False, True, False],
            [False, False, False, False]]
    obj_names = ['dove', 'hen', 'duck', 'goose', 'owl',
                 'hawk', 'eagle', 'fox', 'dog', 'wolf',
                 'cat', 'tiger', 'lion', 'horse', 'zebra', 'cow']
    attr_names = ['fly', 'hunt', 'run', 'swim']
    path = 'data/animal_movement'
    return data, obj_names, attr_names, path


def test_read_converter(animal_movement_data):
    data, obj_names, attr_names, path = animal_movement_data

    for fnc, file_extension in [(converters.read_json, '.json'),
                                (converters.read_cxt, '.cxt'),
                                (converters.read_csv, '.csv')
                                ]:
        fnc_name = fnc.__name__
        path_ext = path+file_extension

        ctx = fnc(path_ext)
        assert ctx.n_objects == len(obj_names),\
            f'Converters.{fnc_name} failed. n_objects should be equal {len(obj_names)}'
        assert ctx.n_attributes == len(attr_names),\
            f'Converters.{fnc_name} failed. n_attributes should be equal {len(obj_names)}'
        assert ctx.object_names == obj_names, f'Converters.{fnc_name} failed. Objects names should be {obj_names}'
        assert ctx.attribute_names == attr_names, f'Converters.{fnc_name} failed. Attributes names should be {attr_names}'
        assert ctx.data == data, f'Converters.{fnc_name} failed. Data should be {data}'


def test_write_converter():
    import os
    path_from = 'data/animal_movement'
    path_to = 'data/animal_movement_test'

    for params in [(converters.read_json, converters.write_json, '.json'),
                   (converters.read_cxt, converters.write_cxt, '.cxt'),
                   (converters.read_csv, converters.write_csv, '.csv')
                   ]:
        fnc_read, fnc_write, file_extension = params

        fnc_name = fnc_write.__name__
        path_from_ext = path_from+file_extension
        path_to_ext = path_to+file_extension

        with open(path_from_ext, 'r') as f:
            file_from = f.read()

        ctx = fnc_read(path_from_ext)
        assert fnc_write(ctx) == file_from,\
            f"Converters.{fnc_name} failed. The function should return output file text if given path=None"

        fnc_write(ctx, path_to_ext)

        with open(path_to_ext, 'r') as f:
            file_to = f.read()
        os.remove(path_to_ext)
        assert file_from == file_to, f"Converters.{fnc_name} failed. Output file does not match the input file"


def test_csv_true_false_words(animal_movement_data):
    path = animal_movement_data[3]
    path += '.csv'

    with pytest.raises(ValueError):
        converters.read_csv(path, word_false='test_word')

    with pytest.raises(ValueError):
        converters.read_csv(path, word_true='test_word')
