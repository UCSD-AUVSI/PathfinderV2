import geometry_operations
from geometry_operations import to_radians
from waypoint_generator import WaypointGenerator
from image_generator import ImageGenerator

class Pathfinder:
    PATH_WIDTH = 61
    OVERSHOOT_DISTANCE = 61
    MAX_DISTANCE_BETWEEN_WAYPOINTS = 50
    FONT_SIZE = 42

    @staticmethod
    def __calculate_path_rotated(start_point, perimeters):

        path = [start_point]
        _perimeters = list(perimeters)

        while _perimeters:
            perimeter = geometry_operations.find_closest_perimeter(start_point, _perimeters)
            if geometry_operations.dist(start_point, perimeter[0]) <\
               geometry_operations.dist(start_point, perimeter[1]):
                first_point, second_point = perimeter
            else:
                second_point, first_point = perimeter
            path += [first_point, second_point]
            _perimeters.remove(perimeter)
            start_point = second_point

        return path


    def __add_intermediate_waypoints(self, path):
        def add_intermediates(line):
            return geometry_operations.add_intermediates(line, self.max_distance_between_waypoints)

        path_lines = geometry_operations.calculate_perimeters(path)[:-1]
        new_path = [add_intermediates(line) for line in path_lines]
        return [point for points in new_path for point in points]

    def get_path(self):
        if self.__path is not None:
            return self.__path
        else:
            self.__path = self.calculate_path()
            return self.__path

    def calculate_path(self):

        def compute_path_rotated(boundaries, plane_location):
            line_segments = geometry_operations.calculate_line_segments(boundaries,
                    self.path_width, self.overshoot_distance)
            path = Pathfinder.__calculate_path_rotated(plane_location, line_segments)
            return self.__add_intermediate_waypoints(path)

        def unrotate_path(path, boundaries_center, wind_angle_radians):
            return geometry_operations.rotate(path, boundaries_center, -wind_angle_radians)

        wind_angle_radians = to_radians(self.wind_angle_degrees)
        boundaries_center = geometry_operations.calculate_center(self.boundaries)
        rotated_boundaries = geometry_operations.rotate(self.boundaries, boundaries_center,
                                                        wind_angle_radians)
        rotated_path = compute_path_rotated(rotated_boundaries, self.plane_location)
        self.__path = unrotate_path(rotated_path, boundaries_center, wind_angle_radians)

    def __init__(self, plane_location, boundaries, options = dict()):

        self.path_width = options.get("path_width", Pathfinder.PATH_WIDTH)
        self.overshoot_distance = options.get("overshoot_distance",
                                              Pathfinder.OVERSHOOT_DISTANCE)
        self.max_distance_between_waypoints = \
        options.get("max_distance_between_waypoints", 
                    Pathfinder.MAX_DISTANCE_BETWEEN_WAYPOINTS)
        self.wind_angle_degrees = options.get("wind_angle_degrees", 0)
        self.boundaries = boundaries
        self.plane_location = plane_location
        self.__path = None # Will be evaluated lazily

def main():

    def meters_to_gps(meters):
        return meters / 111122.0

    plane_location = 32.961043, -117.190664
    boundaries = [(32.961043, -117.190664),
                  (32.961132, -117.188443),
                  (32.962393, -117.187006),
                  (32.962321, -117.189924)]

    options = {
        "wind_angle_degrees": 30,
        "path_width": meters_to_gps(30),
        "overshoot_distance": meters_to_gps(30),
        "dist_between": meters_to_gps(30)
    }

    finder = Pathfinder(plane_location, boundaries, options)
    waypoint_generator = WaypointGenerator(finder)
    image_generator = ImageGenerator(finder)
                
    waypoint_generator.export_qgc_waypoints()
    image_generator.create_image("output.jpg")

if __name__ == '__main__':
    main()
