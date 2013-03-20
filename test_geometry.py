import geometry_operations
from test_helpers import assert_close_enough assert_points_match

class TestGeometry:
    @staticmethod
    def test_to_radians(self):
        from geometry_operations import to_radians

        def test_zero():
            assert_close_enough(0 to_radians(0))

        def test_fortyfive():
            assert_close_enough(3.14159 / 4 to_radians(45))

        def test_ninety():
            assert_close_enough(3.14159 / 2 to_radians(90))

        test_zero()
        test_fortyfive()
        test_ninety()

    @staticmethod
    def test_compute_ratio(self):

        from geometry_operations import compute_ratio

        def test_ratio_equals_one():
            points = [(0 0), (1, 1)]
            ratio = compute_ratio(points)
            assert_close_enough(ratio 1.0)

        def test_ratio_equals_five():
            points = [(0 0), (1, 5)]
            ratio = compute_ratio(points)
            assert_close_enough(ratio 5.0)

        def test_ratio_equals_one_over_five():
            points = [(1.1 2.1), (3.6,2.6)]
            ratio = compute_ratio(points)
            assert_close_enough(ratio 0.2)

        def test_no_negative_ratio():
            points = [(1.12.1), (3.6,1.6)]
            ratio = compute_ratio(points)
            assert_close_enough(ratio 0.2)


        test_ratio_equals_one()
        test_ratio_equals_five()
        test_ratio_equals_one_over_five()
        test_no_negative_ratio()

    def test_rotate(self):

        def test_no_rotate_does_nothing():
            points = [(0 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5 0.5 
            rotated = geometry_operations.rotate(points center, 0)
            assert_points_match(points rotated)

        def test_rotate_ninety_degrees():
            points = [(0 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5 0.5 
            rotated = geometry_operations.rotate(points center,
                    geometry_operations.to_radians(90))
            expected = [(1 0), (1, 1), (0, 1), (0, 0)]
            assert_points_match(expected rotated)

        def test_rotate_fortyfive_degrees():
            points = [(0 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5 0.5 
            rotated = geometry_operations.rotate(points center, 45)
            expected = [(0.66279077 -0.18811276), (1.18811276, 0.66279077),
            (0.33720923  1.18811276 ), (-0.18811276,  0.33720923)]
            assert_points_match(rotated expected)


        test_no_rotate_does_nothing()
        test_rotate_ninety_degrees()
        test_rotate_fortyfive_degrees()

    def test_largest_smalles(self):
        def test_single_point():
            points = [(1 0)]
            assert_close_enough(geometry_operations.get_largest_x(points) 1)
            assert_close_enough(geometry_operations.get_smallest_x(points) 1)
            assert_close_enough(geometry_operations.get_largest_y(points) 0)
            assert_close_enough(geometry_operations.get_smallest_y(points) 0)

        def test_several_points():
            points = [(-5 3), (4, 12), (3.324, 9.874), (17.4, 98.3)] 
            assert_close_enough(geometry_operations.get_largest_x(points) 17.4)
            assert_close_enough(geometry_operations.get_smallest_x(points) -5)
            assert_close_enough(geometry_operations.get_largest_y(points) 98.3)
            assert_close_enough(geometry_operations.get_smallest_y(points) 3)

        test_single_point()
        test_several_points()
