"""
This module provides a number of functions to read/write FormalContext object from/to a file

"""
from fcapy.context.formal_context import FormalContext


def read_cxt(path=None, data=None):
    """Read FormalContext from .cxt file or from ``data`` attribute

    Parameters
    ----------
    path : `str`
        A path to requested .cxt file
    data : `str`
        CXT formatted data (if it is already loaded into python)
    Returns
    -------
    ctx : `FormalContext`
        The loaded FormalContext object

    """
    assert path is not None or data is not None, 'converters.read_cxt error. Either path or data should be given'

    if data is None:
        with open(path, 'r') as f:
            data = f.read()

    _, ns, data = data.split('\n\n')
    n_objs, n_attrs = [int(x) for x in ns.split('\n')]

    data = data.strip().split('\n')
    obj_names, data = data[:n_objs], data[n_objs:]
    attr_names, data = data[:n_attrs], data[n_attrs:]
    data = [[c == 'X' for c in line] for line in data]

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    return ctx


def write_cxt(context, path=None):
    """Write FormalContext object to the .cxt file

    Parameters
    ----------
    context : `FormalContext`
        A context to write to a file
    path : `str`
        A path to the file to write a FormalContext object
    Returns
    -------
    file_data : `str`
        The date from the .cxt file. Returned if ``path`` is None

    """
    file_data = 'B\n\n'
    file_data += f"{context.n_objects}\n{context.n_attributes}\n"
    file_data += '\n'
    file_data += '\n'.join(context.object_names) + '\n'
    file_data += '\n'.join(context.attribute_names) + '\n'

    file_data += '\n'.join([''.join(['X' if b else '.' for b in line]) for line in context.data.to_list()]) + '\n'

    if path is None:
        return file_data

    with open(path, 'w') as f:
        f.write(file_data)


def read_json(path=None, data=None):
    """Read FormalContext from .json file or from ``data`` attribute

    Parameters
    ----------
    path : `str`
        A path to requested .json file
    data : `str`
        JSON formatted data (if it is already loaded into python)
    Returns
    -------
    ctx : `FormalContext`
        The loaded FormalContext object

    """
    assert path is not None or data is not None, 'converters.read_json error. Either path or data should be given'

    import json

    if data is None:
        with open(path, 'r') as f:
            data = f.read()
    file_data = json.loads(data)

    ctx_metadata = file_data[0]
    object_info = file_data[1]

    object_names = ctx_metadata.get('ObjNames')
    attribute_names = ctx_metadata['Params'].get('AttrNames') if 'Params' in ctx_metadata else None
    description = ctx_metadata.get('Description')
    data_inds = [set(line['Inds']) for line in object_info['Data']]
    data = [[ind in inds for ind in range(len(attribute_names))] for inds in data_inds]

    ctx = FormalContext(data=data, object_names=object_names, attribute_names=attribute_names, description=description)
    return ctx


def write_json(context, path=None):
    """Write FormalContext object to the .json file

    Parameters
    ----------
    context : `FormalContext`
        A context to write to a file
    path : `str`
        A path to the file to write a FormalContext object
    Returns
    -------
    file_data : `str`
        The date from the .json file. Returned if ``path`` is None

    """
    import json

    ctx_metadata, object_info = {}, {}
    if context.description is not None:
        ctx_metadata['Description'] = context.description
    ctx_metadata['ObjNames'] = context.object_names
    ctx_metadata['Params'] = {}
    ctx_metadata['Params']['AttrNames'] = context.attribute_names

    object_info['Count'] = context.n_objects
    object_info['Data'] = [
        {'Count': sum(g_ms), 'Inds': [ind for ind in range(context.n_attributes) if g_ms[ind]]}
        for g_ms in context.data.to_list()
    ]
    file_data = json.dumps([ctx_metadata, object_info], separators=(',', ':'))

    if path is None:
        return file_data

    with open(path, 'w') as f:
        f.write(file_data)


def read_csv(path, sep=',', word_true='True', word_false='False'):
    """Read FormalContext from .csv file

    Parameters
    ----------
    path : `str`
        A path to requested .csv file
    sep : `str`
        A separator in the .csv file
    word_true : `str`
        A string placeholder corresponding to True values in the .csv file
    word_false : `str`
        A string placeholder corresponding to False values in the .csv file
    Returns
    -------
    ctx : `FormalContext`
        The loaded FormalContext object

    """
    # TODO: add `data` parameter
    with open(path, 'r') as f:
        file_data = f.read().strip().split('\n')
    header, file_data = file_data[0], file_data[1:]

    attr_names = header.split(sep)[1:]
    obj_names, data = [], []
    for line in file_data:
        line = line.split(sep)
        obj_names.append(line[0])
        val_error = ValueError(f'Csv file {path} has values that differ from "{word_true}" and "{word_false}". ' + \
                               'Binarize the file or change values of parameters "word_true", "word_false"')
        data_line = []
        for val in line[1:]:
            if val in {word_true, word_false}:
                data_line.append(val == word_true)
            else:
                raise val_error
        data.append(data_line)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    return ctx


def write_csv(context, path=None, sep=',', word_true='True', word_false='False'):
    """Write FormalContext object to the .csv file

    Parameters
    ----------
    context : `FormalContext`
        A context to write to a file
    path : `str`
        A path to the file to write a FormalContext object
    sep : `str`
        A separator in the .csv file
    word_true : `str`
        A string placeholder corresponding to True values in the .csv file
    word_false : `str`
        A string placeholder corresponding to False values in the .csv file
    Returns
    -------
    file_data : `str`
        The date from the .csv file. Returned if ``path`` is None

    """
    file_data = sep+sep.join(context.attribute_names)+'\n'
    for obj_name, data_line in zip(context.object_names, context.data.to_list()):
        file_data += obj_name+sep+sep.join([word_true if val else word_false for val in data_line])+'\n'
    file_data = file_data

    if path is None:
        return file_data

    with open(path, 'w') as f:
        f.write(file_data)


def from_pandas(dataframe):
    """Create FormalContext object based on pandas.DataFrame

    ``context.object_names`` are parsed from ``dataframe.index``.
    ``context.column_names`` are parsed from ``dataframe.columns``

    Parameters
    ----------
    dataframe : `pandas.DataFrame`

    Returns
    -------
    ctx : `FormalContext`

    """
    ctx = FormalContext(data=dataframe.values.tolist(),
                        object_names=dataframe.index.tolist(), attribute_names=dataframe.columns.tolist())
    return ctx


def to_pandas(context):
    """Convert FormalContext object to pandas.DataFrame object

    ``context.object_names`` are turned into ``df.index``.
    ``context.column_names`` are turned into ``df.columns``

    Parameters
    ----------
    context : `FormalContext`
        A context to convert
    Returns
    -------
    df : `pandas.DataFrame`
        The binary dataframe based on FormalContext object

    """
    import pandas as pd
    df = pd.DataFrame(context.data.to_list(), columns=context.attribute_names, index=context.object_names)
    return df
