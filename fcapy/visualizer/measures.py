from fcapy.poset import POSet


def check_intersection(
        line0: (float, float, float, float), line1: (float, float, float, float),
        k0: float, k1: float, b0: float, b1: float, close_dist:float = 1e-2
):
    """Check whether there is an intersection between lines ``line0`` and ``line1``

    Parameters
    ----------
    line0: `tuple` of 4 `float`
        Start and stop coordinates of the first line (x0, y0, x1, y1)
    line1: `tuple` of 4 `float`
        Start and stop coordinates of the second line (x0, y0, x1, y1)
    k0: `float`
        Slope of the first line
    k1: `float`
        Slope of the second line
    b0: `float`
        Bias of the first line
    b1: `float`
        Bias of the second line
    close_dist: `float`visualizer.Visualizer:
    A class to visualize the `ConceptLattice`

        Minimum distance between lines to consider them intersecting

    Returns
    -------
    is_intersect: `bool`
        A flag whether there is an intersection between lines ``line0`` and ``line1``

    """
    x00, y00, x01, y01 = [coord for coord in line0]
    x10, y10, x11, y11 = [coord for coord in line1]

    bottom0, top0 = (y00, y01) if y00 < y01 else (y01, y00)
    bottom1, top1 = (y10, y11) if y10 < y11 else (y11, y10)
    left0, right0 = (x00, x01) if x00 < x01 else (x01, x00)
    left1, right1 = (x10, x11) if x10 < x11 else (x11, x10)

    if bottom0 >= top1 or bottom1 >= top0:
        return False
    if left0 >= right1 or left1 >= right0:
        return False

    def is_equal(a, b, close_dist=close_dist):
        return (a - b) ** 2 < close_dist ** 2

    if is_equal(k0, k1):
        return is_equal(b0, b1)

    x = -(b1 - b0) / (k1 - k0)
    y = k0 * x + b0

    if (is_equal(y, top0) and is_equal(y, top1)) \
            or (is_equal(y, bottom0) and is_equal(y, bottom1)) \
            or (is_equal(x, left0) and is_equal(x, left1)) \
            or (is_equal(x, right0) and is_equal(x, right1)) \
            :
        return False

    if left0 <= x <= right0 and left1 <= x <= right1 \
            and bottom0 <= y <= top0 and bottom1 <= y <= top1:
        return True  # x, y
    return False


def count_line_intersections(pos: dict, poset: POSet, close_dist=1e-2):
    """Count intersections of lines between direct neighbours from ``poset`` placed in ``pos`` coordinates"""
    # at first we have lines: x0, y0, x1, y1: y1 < y0
    lines = [pos[el_i][::-1] + pos[dsub_i][::-1]
             for el_i, dsubs in poset.children_dict.items() for dsub_i in dsubs]
    # we switch `x` and `y` coordinates to avoid zero division error when computing `k`
    # thus lines become: x0, y0, x1, y1: x1<x0

    n_lines = len(lines)

    ks = [(y1 - y0) / (x1 - x0) for (x0, y0, x1, y1) in lines]
    bs = [y0 - x0 * k for (x0, y0, _, _), k in zip(lines, ks)]

    n_intersections = sum([
        check_intersection(lines[i], lines[j], ks[i], ks[j], bs[i], bs[j], close_dist)
        for i in range(n_lines) for j in range(i + 1, n_lines)
    ])
    return n_intersections
