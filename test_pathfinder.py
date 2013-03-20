from pathfinder import Pathfinder
from image_generator import ImageGenerator

class TestPathfinder:

    @staticmethod
    def integration_test():
        def test_square():
            plane_location = 1, 1
            boundaries = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
            options = {
                "wind_angle_degrees": 45,
                "max_distance_between_waypoints": 150
            }
            finder = Pathfinder(plane_location, boundaries, options)
            ImageGenerator(finder).create_image("square.jpg")

        def test_square_scaled():
            plane_location = 0.1, 0.1
            boundaries = [(0, 0), (0.1, 0), (0.1, 0.1), (0, 0.1)]
            options = {
                    "wind_angle_degrees": 90,
                    "overshoot_distance": 0.0006,
                    "path_width": 0.006
            }
            finder = Pathfinder(plane_location, boundaries, options)
            ImageGenerator(finder).create_image("square_scaled.jpg")

        def test_rot_square():
            plane_location = 1, 1
            boundaries = [(500, 0), (0, 500), (-500, 0), (0, -500)]
            options = {
                "wind_angle_degrees": 90        
            }
            finder = Pathfinder(plane_location, boundaries, options)
            ImageGenerator(finder).create_image("rot_square.jpg")

        def test_concave():
            plane_location = 1, 1
            boundaries = [(0, 0), (1000, 0), (500, 500), (1000, 1000), (0, 1000)]
            options = {
                "wind_angle_degrees": 90        
            }
            finder = Pathfinder(plane_location, boundaries, options)
            ImageGenerator(finder).create_image("concave.jpg")

        def test_gps_coords():
            plane_location = 32.961043, -117.190664
            boundaries = [(32.961043, -117.190664),
            (32.961132, -117.188443),
            (32.962393, -117.187006),
            (32.962321, -117.189924)]
            options = {
                "wind_angle_degrees": 90,
                "overshoot_distance": 0.0001,
                "path_width": 0.0001
            }
            finder = Pathfinder(plane_location, boundaries, options)
            ImageGenerator(finder).create_image("gps.jpg")


        test_square()
        test_square_scaled()
        test_rot_square()
        test_concave()
        test_gps_coords()

    def __init__(self):
        print "Use `nosetests` in the shell to run this file"
