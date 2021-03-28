import pytest


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
    obj_names = ('dove', 'hen', 'duck', 'goose', 'owl',
                 'hawk', 'eagle', 'fox', 'dog', 'wolf',
                 'cat', 'tiger', 'lion', 'horse', 'zebra', 'cow')
    attr_names = ('fly', 'hunt', 'run', 'swim')
    path = 'data/animal_movement'
    repr_data = """FormalContext (16 objects, 4 attributes, 24 connections)
     |fly|hunt|run|swim|
dove |  X|    |   |    |
hen  |   |    |   |    |
duck |  X|    |   |   X|
goose|  X|    |   |   X|
owl  |  X|   X|   |    |
hawk |  X|   X|   |    |
eagle|  X|   X|   |    |
fox  |   |   X|  X|    |
dog  |   |    |  X|    |
wolf |   |   X|  X|    |
cat  |   |   X|  X|    |
tiger|   |   X|  X|    |
lion |   |   X|  X|    |
horse|   |    |  X|    |
zebra|   |    |  X|    |
cow  |   |    |   |    |"""

    printed_data_short = """     |fly|...|swim|
dove |  X|...|    |
hen  |   |...|    |
...................
...................
zebra|   |...|    |
cow  |   |...|    |"""

    data_dict = {'data': data, 'obj_names': obj_names, 'attr_names': attr_names,
                 'path': path,
                 'repr_data': repr_data, 'printed_data_short': printed_data_short}
    return data_dict
