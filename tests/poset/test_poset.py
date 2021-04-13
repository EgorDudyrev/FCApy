from fcapy.poset import POSet


def test_init():
    s = POSet()

    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x,y: x in y
    s = POSet(elements, leq_func)
    assert s._elements == elements
    assert s._leq_func == leq_func


def test_join_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    join = s.join_elements([1, 2])

    assert join == 0


def test_meet_elements():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    join = s.join_elements([1, 2])

    # in the case of linear order, meet is the same as minimum
    assert join == 3


def test_getitem():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    assert s[0] == ''
    assert s[1] == 'a'
    assert s[2] == 'b'
    assert s[3] == 'ab'


def test_eq():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    other = POSet(elements, leq_func)
    assert s == other

    other = POSet(elements[:-1], leq_func)
    assert s != other

    elements_1 = ['', 'a', 'b', 'abc']
    other = POSet(elements_1, leq_func)
    assert s != other

    leq_func_1 = lambda x, y: not x  in y
    other = POSet(elements, leq_func_1)
    assert s != other

    other = POSet(elements_1, leq_func_1)
    assert s != other


def test_and():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s1 = POSet(elements[:-1], leq_func)
    s2 = POSet(elements[1:], leq_func)
    s_and = POSet(elements[1:-1], leq_func)
    assert s1 & s2 == s_and


def test_or():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s1 = POSet(elements[:-1], leq_func)
    s2 = POSet(elements[1:], leq_func)
    s_or = POSet(elements, leq_func)
    assert s1 | s2 == s_or


def test_xor():
    elements = ['', 'a', 'b', 'ab']
    elements_xor = ['', 'ab']
    leq_func = lambda x, y: x in y
    s1 = POSet(elements[:-1], leq_func)
    s2 = POSet(elements[1:], leq_func)
    s_xor = POSet(elements_xor, leq_func)
    assert s1 | s2 == s_xor


def test_len():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    assert len(s) == len(elements)


def test_delitem():
    elements = ['', 'a', 'b', 'ab']
    del_i = 1
    elements_del = [el for i, el in enumerate(elements) if i != del_i]
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    del s[del_i]
    assert s.elements == elements_del


def test_add():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements[:-1], leq_func)
    s.add(elements[-1])
    assert s.elements == elements


def test_remove():
    elements = ['', 'a', 'b', 'ab']
    leq_func = lambda x, y: x in y
    s = POSet(elements, leq_func)
    s.remove(elements[-1])
    assert s.elements == elements[:-1]
