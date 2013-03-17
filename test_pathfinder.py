import nose
from math import fabs
from pathfinder import GeometryOperations, Pathfinder


class TestHelpers:
    @staticmethod
    def assert_close_enough(value1, value2, epsilon = 0.00001):
        print value1, " vs ", value2
        assert fabs(value1-value2) < epsilon

    @staticmethod
    def assert_points_match(points1, points2):
        print points1
        print points2
        for point1, point2 in zip(points1, points2):
            TestHelpers.assert_close_enough(point1[0], point2[0])
            TestHelpers.assert_close_enough(point1[1], point2[1])

class TestGeometryOperations:

    def test_to_radians(self):

        to_radians = GeometryOperations.to_radians
        def test_zero():
            TestHelpers.assert_close_enough(0, to_radians(0))

        def test_fortyfive():
            TestHelpers.assert_close_enough(3.14159 / 4, to_radians(45))

        def test_ninety():
            TestHelpers.assert_close_enough(3.14159 / 2, to_radians(90))

        test_zero()
        test_fortyfive()
        test_ninety()

    def test_compute_ratio(self):

        def test_ratio_equals_one():
            points = [(0,0), (1,1)]
            ratio = GeometryOperations.compute_ratio(points)
            TestHelpers.assert_close_enough(ratio, 1.0)

        def test_ratio_equals_five():
            points = [(0,0), (1,5)]
            ratio = GeometryOperations.compute_ratio(points)
            TestHelpers.assert_close_enough(ratio, 5.0)

        def test_ratio_equals_one_over_five():
            points = [(1.1,2.1), (3.6,2.6)]
            ratio = GeometryOperations.compute_ratio(points)
            TestHelpers.assert_close_enough(ratio, 0.2)

        def test_no_negative_ratio():
            points = [(1.1,2.1), (3.6,1.6)]
            ratio = GeometryOperations.compute_ratio(points)
            TestHelpers.assert_close_enough(ratio, 0.2)


        test_ratio_equals_one()
        test_ratio_equals_five()
        test_ratio_equals_one_over_five()
        test_no_negative_ratio()

    def test_rotate(self):

        def test_no_rotate_does_nothing():
            points = [(0, 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5, 0.5 
            rotated = GeometryOperations.rotate(points, center, 0)
            TestHelpers.assert_points_match(points, rotated)

        def test_rotate_ninety_degrees():
            points = [(0, 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5, 0.5 
            rotated = GeometryOperations.rotate(points, center,
                    GeometryOperations.to_radians(90))
            expected = [(1, 0), (1, 1), (0, 1), (0, 0)]
            TestHelpers.assert_points_match(expected, rotated)

        def test_rotate_fortyfive_degrees():
            points = [(0, 0), (1, 0), (1, 1), (0, 1)]
            center = 0.5, 0.5 
            rotated = GeometryOperations.rotate(points, center, 45)
            expected = [(0.66279077, -0.18811276), (1.18811276, 0.66279077),
            (0.33720923,  1.18811276 ), (-0.18811276,  0.33720923)]
            TestHelpers.assert_points_match(rotated, expected)


        test_no_rotate_does_nothing()
        test_rotate_ninety_degrees()
        test_rotate_fortyfive_degrees()

    def test_largest_smalles(self):
        def test_single_point():
            points = [(1, 0)]
            TestHelpers.assert_close_enough(GeometryOperations.get_largest_x(points), 1)
            TestHelpers.assert_close_enough(GeometryOperations.get_smallest_x(points), 1)
            TestHelpers.assert_close_enough(GeometryOperations.get_largest_y(points), 0)
            TestHelpers.assert_close_enough(GeometryOperations.get_smallest_y(points), 0)

        def test_several_points():
            points = [(-5, 3), (4, 12), (3.324, 9.874), (17.4, 98.3)] 
            TestHelpers.assert_close_enough(GeometryOperations.get_largest_x(points), 17.4)
            TestHelpers.assert_close_enough(GeometryOperations.get_smallest_x(points), -5)
            TestHelpers.assert_close_enough(GeometryOperations.get_largest_y(points), 98.3)
            TestHelpers.assert_close_enough(GeometryOperations.get_smallest_y(points), 3)

        test_single_point()
        test_several_points()

    def integration_test(self):

        def test_square():
            plane_location = 1, 1
            boundaries = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
            wind_angle_degrees = 45
            finder = Pathfinder(plane_location, boundaries, wind_angle_degrees,
                    max_distance_between_waypoints = 150)
            finder.create_image("square.jpg")

        def test_square_scaled():
            plane_location = 0.1, 0.1
            boundaries = [(0, 0), (0.1, 0), (0.1, 0.1), (0, 0.1)]
            wind_angle_degrees = 90
            finder = Pathfinder(plane_location, boundaries, wind_angle_degrees, 0.006, 0.006)
            finder.create_image("square_scaled.jpg")

        def test_rot_square():
            plane_location = 1, 1
            boundaries = [(500, 0), (0,500), (-500, 0), (0, -500)]
            wind_angle_degrees = 90
            finder = Pathfinder(plane_location, boundaries, wind_angle_degrees)
            finder.create_image("rot_square.jpg")

        def test_concave():
            plane_location = 1, 1
            boundaries = [(0, 0), (1000, 0), (500,500), (1000, 1000), (0, 1000)]
            wind_angle_degrees = 90
            finder = Pathfinder(plane_location, boundaries, wind_angle_degrees)
            finder.create_image("concave.jpg")

        def test_gps_coords():
            plane_location = 32.961043, -117.190664
            boundaries = [(32.961043,-117.190664),
            (32.961132,-117.188443),
            (32.962393,-117.187006),
            (32.962321,-117.189924)]
            wind_angle_degrees = 90
            finder = Pathfinder(plane_location, boundaries, wind_angle_degrees, 0.0001, 0.0001)
            finder.create_image("gps.jpg")


        test_square()
        test_square_scaled()
        test_rot_square()
        test_concave()
        test_gps_coords()

nose.run()
