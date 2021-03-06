from math import fabs

def assert_close_enough(value1, value2, epsilon = 0.00001):
    print value1, " vs ", value2
    assert fabs(value1-value2) < epsilon

def assert_points_match(points1, points2):
    print points1
    print points2
    for point1, point2 in zip(points1, points2):
        assert_close_enough(point1[0], point2[0])
        assert_close_enough(point1[1], point2[1])

def assert_requires_nonempty_list_input(function):
    try:
        function([])
        raise AssertionError("Expected an AssertionError in " + str(function) +
                ", but no exception was thrown")
    except AssertionError:
        # An assertion failed in the function, as expected
        pass

def assert_should_raise_exception(function):
    try:
        function()
        raise AssertionError("Expected an Exception in " + str(function) + 
                ", but no exception was thrown")
    except:
        # An exception was thrown, as expected
        pass
