import geometry_operations

from test_helpers import assert_close_enough, \
                         assert_points_match, \
                         assert_requires_nonempty_list_input, \
                         assert_should_raise_exception

from functools import partial

class TestGeometry:

    def test_get_bounding_box(self):
        from geometry_operations import get_bounding_box

        assert_requires_nonempty_list_input(get_bounding_box)

        def test_single_point():
            point = 17, -34.2
            box = get_bounding_box([point])
            assert box[0] == point
            assert box[1] == point

        def test_multipoint():
            points = [(-5, 3), (4, 12), (3.324, 9.874), (17.4, 98.3)] 
            box = get_bounding_box(points)
            (min_x, min_y), (max_x, max_y) = box
            assert min_x == -5
            assert min_y == 3
            assert max_x == 17.4
            assert max_y == 98.3

        test_single_point()
        test_multipoint()

    def test_to_radians(self):
        from geometry_operations import to_radians

        def test_zero():
            assert_close_enough(0, to_radians(0))

        def test_fortyfive():
            assert_close_enough(3.14159 / 4, to_radians(45))

        def test_ninety():
            assert_close_enough(3.14159 / 2, to_radians(90))

        test_zero()
        test_fortyfive()
        test_ninety()

    def test_compute_ratio(self):

        from geometry_operations import compute_ratio

        def test_ratio_equals_one():
            box = (0,0), (1,1)
            ratio = compute_ratio(box)
            assert ratio == 1

        def test_ratio_equals_five():
            box = (0,0), (1,5)
            ratio = compute_ratio(box)
            assert ratio == 5

        def test_ratio_equals_one_over_five():
            box = (1.1,2.1), (3.6,2.6)
            ratio = compute_ratio(box)
            assert ratio == 0.2

        def test_no_negative_ratio():
            box = (1.1,2.1), (3.6,1.6)
            ratio = compute_ratio(box)
            assert_close_enough(ratio, 0.2)


        test_ratio_equals_one()
        test_ratio_equals_five()
        test_ratio_equals_one_over_five()
        test_no_negative_ratio()

    def test_rotate(self):

        def test_no_rotate_does_nothing():
            points = [(0, 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5, 0.5 
            rotated = geometry_operations.rotate(points, center, 0)
            assert_points_match(points, rotated)

        def test_rotate_ninety_degrees():
            points = [(0, 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5, 0.5 
            rotated = geometry_operations.rotate(points, center,
                    geometry_operations.to_radians(90))
            expected = [(1, 0), (1, 1), (0, 1), (0, 0)]
            assert_points_match(expected, rotated)

        def test_rotate_fortyfive_degrees():
            points = [(0, 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5, 0.5 
            rotated = geometry_operations.rotate(points, center, 45)
            expected = [(0.66279077, -0.18811276), (1.18811276, 0.66279077),
            (0.33720923,  1.18811276 ), (-0.18811276,  0.33720923)]
            assert_points_match(rotated, expected)


        test_no_rotate_does_nothing()
        test_rotate_ninety_degrees()
        test_rotate_fortyfive_degrees()

    def test_max_min(self):

        from geometry_operations import get_max_x, get_max_y, get_min_x,\
                                        get_min_y
        
        assert_requires_nonempty_list_input(get_max_x)
        assert_requires_nonempty_list_input(get_max_y)
        assert_requires_nonempty_list_input(get_min_x)
        assert_requires_nonempty_list_input(get_min_y)

        def test_single_point():
            points = [(1, 0)]
            assert_close_enough(get_max_x(points), 1)
            assert_close_enough(get_min_x(points), 1)
            assert_close_enough(get_max_y(points), 0)
            assert_close_enough(get_min_y(points), 0)

        def test_several_points():
            points = [(-5, 3), (4, 12), (3.324, 9.874), (17.4, 98.3)] 
            assert_close_enough(get_max_x(points), 17.4)
            assert_close_enough(get_min_x(points), -5)
            assert_close_enough(get_max_y(points), 98.3)
            assert_close_enough(get_min_y(points), 3)

        test_single_point()
        test_several_points()

    def test_calculate_line_segments_thru(self):
        from geometry_operations import calculate_line_segments_thru

        def test_no_intersection():
            x = -1
            boundaries = [(0,0), (100, 0), (50, 100)]
            assert calculate_line_segments_thru(x, boundaries) == []

        def test_intersection_at_point():
            x = 0
            boundaries = [(0, 0), (100, 0), (100, 100)]
            expected = [((0,0), (0,0))]
            actual = calculate_line_segments_thru(x, boundaries)
            assert expected == actual

        def test_intersection_thru_boundaries():
            x = 50
            boundaries = [(0,0), (1000, 0), (1000, 1000), (0, 1000)]
            expected = [((50,0), (50, 1000))]
            actual = calculate_line_segments_thru(x, boundaries)
            assert expected == actual

        test_no_intersection()
        test_intersection_at_point()
        test_intersection_thru_boundaries()

    def test_calculate_intersections(self):
        from geometry_operations import calculate_intersections

        def test_no_intersection():
            line_segment = [(-50, -50), (-50, 100)]
            boundaries = [(0,0), (100, 0), (50, 100)]
            assert calculate_intersections(line_segment, boundaries) == []

        def test_intersection_at_point():
            line_segment = [(0, 0), (0, 100)]
            boundaries = [(0, 0), (100, 0), (100, 100)]
            expected = [(0,0)]
            actual = calculate_intersections(line_segment, boundaries)
            assert expected == actual

        def test_intersection_thru_boundaries():
            line_segment = [(50, 0), (50, 1000)]
            boundaries = [(0,0), (1000, 0), (1000, 1000), (0, 1000)]
            expected = [(50,0), (50, 1000)]
            actual = calculate_intersections(line_segment, boundaries)
            assert expected == actual

        test_no_intersection()
        test_intersection_at_point()
        test_intersection_thru_boundaries()

    def test_dist(self):
        from geometry_operations import dist

        def test_simple_distance():
            assert dist((0,3),(4,0)) == 5

        def test_negative_distance():
            assert dist((0,-3),(-4,0)) == 5
            assert dist((0,3), (-4 ,0)) == 5

        def test_decimal_distance():
            assert dist((0,.3),(.4,0)) == .5

        test_simple_distance()
        test_negative_distance()
        test_decimal_distance()

    def test_to_line_segments(self):
        from geometry_operations import to_line_segments

        def test_no_points():
            assert to_line_segments([]) == []

        def test_one_point():
            assert to_line_segments([(13,4)]) == []

        def test_triangle():
            triangle_points = [(0,0), (0, 100), (100, 0)]
            expected = [((0,0), (0, 100)), ((0, 100), (100, 0)), ((100, 0), (0,
                0))]
            actual = to_line_segments(triangle_points)
            assert actual == expected

        test_no_points()
        test_one_point()
        test_triangle()

    def test_calculate_center(self):
        from geometry_operations import calculate_center

        assert_requires_nonempty_list_input(calculate_center)

        def test_single_point():
            assert calculate_center([(34, 39)]) == (34, 39)

        def test_rectangle():
            rectangle = [(0,0) , (1000, 0), (1000, 500), (0, 500)]
            print calculate_center(rectangle)
            assert calculate_center(rectangle) == (500, 250)

        def test_triangle():
            triangle = [(0,0), (100,0), (100,100)]
            expected = 66 + 2.0/3, 33 + 1.0/3
            assert(calculate_center(triangle)) == expected

        test_single_point()
        test_rectangle()
        test_triangle()

    def test_find_closest_line_segment(self):
        from geometry_operations import find_closest_line_segment

        point = 0, 0
        segments = [((5, 3), (1,1)), ((12, 9), (9, 12)), ((-5, -5), (5, 5))]

        assert_requires_nonempty_list_input(partial(find_closest_line_segment,
            point))
        
        assert find_closest_line_segment(point, segments) == segments[0]

    def test_pad_vertical(self):
        from geometry_operations import pad_vertical

        def test_fail_on_nonvertical_line_segment():
            line_segment = (0, 0), (1, 1)
            padding = 5
            failing_func = partial(pad_vertical, line_segment, padding)
            assert_should_raise_exception(failing_func)

        def test_padding():
            line_segment = (5, 10), (5, 20)
            padding = 2.5
            expected = (5, 7.5), (5, 22.5)
            assert pad_vertical(line_segment, padding) == expected

            line_segment = (5, 20), (5, 10)
            expected = (5, 22.5), (5, 7.5)
            assert pad_vertical(line_segment, padding) == expected

        test_fail_on_nonvertical_line_segment()
        test_padding()

    def test_is_vertical(self):
        from geometry_operations import is_vertical

        def test_not_vertical():
            line_segment = (0, 0), (1, 1)
            assert not is_vertical(line_segment)

        def test_vertical():
            line_segment = (50, 50), (50, 100)
            assert is_vertical(line_segment)

        test_not_vertical()
        test_vertical()

    def test_partition_line_segment_if_vertical(self):
        from geometry_operations import partition_line_segment_if_vertical,\
                                        to_line_segments, dist

        def test_distance_must_be_positive():
            line_segment = [(0,0), (5,0)]
            distance = -5
            failing_func = partial(partition_line_segment_if_vertical,
                    line_segment, distance)
            assert_should_raise_exception(failing_func)

        def test_should_return_segment_if_not_vertical():
            line_segment = (0,0), (100,100)
            distance = 1
            assert partition_line_segment_if_vertical(line_segment, distance) == line_segment

        def assert_results_valid(input, output, distance):
            in_start, in_end = input
            out_start = output[0]
            out_end = output[-1]
            assert in_start == out_start
            assert in_end == out_end
            for segment in to_line_segments(output)[:-1]:
                start, end = segment
                assert dist(start, end) <= distance + 0.000001

        def test_valid_results_for_vertical():
            line_segment = (0,0), (0, 100)
            distance = 2.3
            result = partition_line_segment_if_vertical(line_segment, distance)
            assert_results_valid(line_segment, result, distance)

        test_valid_results_for_vertical()
        test_should_return_segment_if_not_vertical()
