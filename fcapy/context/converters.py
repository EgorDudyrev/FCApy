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


def to_cxt(context, path=None):
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
