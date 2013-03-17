import nose
from math import fabs
from pathfinder import GeometryOperations, Pathfinder


class TestHelpers:
    @staticmethod
    def assert_close_enough(value1, value2, epsilon = 0.00001):
        assert fabs(value1-value2) < epsilon

    @staticmethod
    def assert_points_match(points1, points2):
        for point1, point2 in zip(points1, points2):
            TestHelpers.assert_close_enough(point1[0], point2[0])
            TestHelpers.assert_close_enough(point1[1], point2[1])

class TestGeometryOperations:

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
            rotated = GeometryOperations.rotate(points, center, 0)
            expected = [(1, 0), (1, 1), (0, 1), (0,0 )]
            TestHelpers.assert_points_match(points, rotated)

        test_no_rotate_does_nothing()
        test_rotate_ninety_degrees()

    def integration_test(self):
        def test_square():
            plane_location = 1, 1
            boundaries = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
            wind_angle_degrees = 45
            finder = Pathfinder(plane_location, boundaries, wind_angle_degrees)
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


