from fcapy.context import FormalContext


def read_cxt(path):
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
    file_data = 'B\n\n'
    file_data += f"{context.n_objects}\n{context.n_attributes}\n"
    file_data += '\n'
    file_data += '\n'.join(context.object_names) + '\n'
    file_data += '\n'.join(context.attribute_names) + '\n'

    file_data += '\n'.join([''.join(['X' if b else '.' for b in line]) for line in context.data]) + '\n'

    if path is None:
        return file_data

    with open(path, 'w') as f:
        f.write(file_data)


def read_json(path):
    import json

    with open(path, 'r') as f:
        file_data = json.load(f)

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
        for g_ms in context.data
    ]
    file_data = json.dumps([ctx_metadata, object_info], separators=(',', ':'))

    if path is None:
        return file_data

    with open(path, 'w') as f:
        f.write(file_data)


def read_csv(path, sep=',', word_true='True', word_false='False'):
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
    file_data = sep+sep.join(context.attribute_names)+'\n'
    for obj_name, data_line in zip(context.object_names, context.data):
        file_data += obj_name+sep+sep.join([word_true if val else word_false for val in data_line])+'\n'
    file_data = file_data

    if path is None:
        return file_data

    with open(path, 'w') as f:
        f.write(file_data)
