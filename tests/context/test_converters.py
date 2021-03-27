import pytest
from fcapy.context import converters, FormalContext
from .data_to_test import animal_movement_data
import pandas
from operator import itemgetter


def test_read_converter(animal_movement_data):
    data, obj_names, attr_names, path = itemgetter('data', 'obj_names', 'attr_names', 'path')(animal_movement_data)

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
        assert ctx.data.to_list() == data, f'Converters.{fnc_name} failed. Data should be {data}'


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
    path = animal_movement_data['path']
    path += '.csv'

    with pytest.raises(ValueError):
        converters.read_csv(path, word_false='test_word')

    with pytest.raises(ValueError):
        converters.read_csv(path, word_true='test_word')


def test_pandas_converted(animal_movement_data):
    data, obj_names, attr_names = itemgetter('data', 'obj_names', 'attr_names')(animal_movement_data)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    df = pandas.DataFrame(data, columns=attr_names, index=obj_names)
    assert all(converters.to_pandas(ctx) == df), 'Converters.to_pandas failed. Converted frame does not match the input data'

    ctx_post = converters.from_pandas(df)
    assert ctx_post.data, 'Converters.from_pandas failed. Converted context does not match the initial dataframe'

    assert ctx == ctx_post,\
        'Converters.{to_pandas, from_pandas} failed. Double converted context does not match the initial one'
