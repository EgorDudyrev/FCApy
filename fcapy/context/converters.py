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
