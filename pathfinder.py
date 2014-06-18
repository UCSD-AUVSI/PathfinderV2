import geometry_operations
from geometry_operations import to_radians, dist
from waypoint_generator import WaypointGenerator
from image_generator import ImageGenerator
from kml_generator import KMLGenerator
from functools import partial

class Pathfinder:
    """
        Generates a path to search an area with the UAV. It accepts input in any
        coordinate system, but the default options are valid for meters only.
    """
    PATH_WIDTH = 61
    OVERSHOOT_DISTANCE = 61
    MAX_DISTANCE_BETWEEN_WAYPOINTS = 50
    DEFAULT_ALTITUDE = 400

    @staticmethod
    def __remove_sequential_duplicates(path):
        """
            Removes sequential identical points from the path. 
            The final path may still have duplicates, but it will not 
            have any **sequential** duplicates.
        """
        new_path = [path[0]]
        for point in path[1:]:
            if new_path[-1] != point:
                new_path.append(point)

        return new_path

    @staticmethod
    def __connect_path_line_segments(start_point, line_segments):
        """
            Returns a path generated from the line_segments that must be
            traversed to search the field
        """

        path = [start_point]
        _line_segments = list(line_segments)

        while _line_segments:
            nearest_segment = geometry_operations.find_closest_line_segment(start_point, _line_segments)

            segment_start, segment_end = nearest_segment
            close_point, far_point = sorted([segment_start, segment_end], key =
                    partial(dist, start_point))
            # Always travel to the closer point on the line_segment_first
            path += [close_point, far_point]
            _line_segments.remove(nearest_segment)
            start_point = far_point

        return path


    def __add_intermediate_waypoints(self, path):
        """
            Adds intermediate waypoints to the search path, between the vertical
            lines. This is necessary for ardupilot to navigate the field without
            starying too far from the vertical lines.
        """
        def add_intermediates(line):
            return geometry_operations.partition_line_segment_if_vertical(line, self.max_distance_between_waypoints)

        path_lines = geometry_operations.to_line_segments(path)[:-1]
        new_path = [add_intermediates(line) for line in path_lines]
        return [point for points in new_path for point in points]

    def get_path(self):
        """
            Calculates the path if necessary, then returns it
        """
        if self.__path is None:
            self.__path = self.__calculate_path()

        return self.__path

    def __calculate_path(self):
        """
            Calculates the list of waypoints that the plane must navigate to traverse 
            the search area. 
            1. Rotates the search area such that the wind direction points
               lies on the line x = 0 (wind points straight up)
            2. Generates vertical line segments through the boundaries, that are
               *path_width* apart from each other
            3. Connects the line_segments to each other to form the most
               efficient path between them
            4. "Unrotates" to return a path that is valid for the original
               orientation of the search area boundaries
        """

        def compute_path_rotated(boundaries, plane_location):
            line_segments = geometry_operations.calculate_line_segments(boundaries,
                    self.path_width, self.overshoot_distance)
            path = Pathfinder.__connect_path_line_segments(plane_location, line_segments)
            path = self.__add_intermediate_waypoints(path)
            return self.__remove_sequential_duplicates(path)

        def unrotate_path(path, boundaries_center, wind_angle_radians):
            return geometry_operations.rotate(path, boundaries_center, -wind_angle_radians)

        wind_angle_radians = to_radians(self.wind_angle_degrees)
        boundaries_center = geometry_operations.calculate_center(self.searcharea)
        rotated_boundaries = geometry_operations.rotate(self.searcharea, boundaries_center,
                                                        wind_angle_radians)
        rotated_path = compute_path_rotated(rotated_boundaries, self.plane_location)
        return unrotate_path(rotated_path, boundaries_center, wind_angle_radians)

    def get_altitude(self):
	return self.wp_altitude

    def get_searcharea(self):
	return self.searcharea

    def get_boundaries(self):
	return self.boundaries

    def __init__(self, plane_location, searcharea, boundaries, options = dict()):
        """
            Constructor for pathfinder object. 

            plane_location: Starting point of the path

            boundaries: A list of points that represent the boundaries of the
                        search area
            options:
                "path_width": 
                    The distance between each of the plane's passes. This should
                    be no wider than the horizontal distance that the plane's
                    camera can capture in one shot.
                "overshoot_distance":
                    The distance that it takes the plane to level-out from a
                    turn
                "max_distance_between_waypoints":
                    The maximum distance between any two waypoints on the path 
                    that the plane must travel. Lowering this value will
                    increase the plane's tendency to stay on the path
                "wind_angle_degrees":
                    The orientation of the wind. This value should be a floating
                    point number or integer. For reference, the line_segment
                    ((0,0) (1,0)), would have a zero degree angle.
        """

        self.path_width = options.get("path_width", Pathfinder.PATH_WIDTH)
        self.overshoot_distance = options.get("overshoot_distance",
                                              Pathfinder.OVERSHOOT_DISTANCE)
        self.max_distance_between_waypoints = \
        options.get("max_distance_between_waypoints", 
                    Pathfinder.MAX_DISTANCE_BETWEEN_WAYPOINTS)
        self.wind_angle_degrees = options.get("wind_angle_degrees", 0)
        self.searcharea = searcharea
	self.boundaries = boundaries
        self.plane_location = plane_location
	self.wp_altitude = options.get("wp_altitude", Pathfinder.DEFAULT_ALTITUDE)
        self.__path = None # Will be evaluated lazily

def main():

    def meters_to_gps(meters):
        return meters / 111122.0

    def meters_to_feet(meters):
	return meters * 0.3048

    plane_location = 38.144889, -76.428386
    flightboundaries = [(38.1510961533167,-76.43468776546464),
		    (38.14537514977575, -76.4315679330514),
		    (38.14340623193864, -76.43535575559602),
		    (38.14041281165054, -76.43258795871857),
		    (38.14157742394668, -76.42954167566813),
		    (38.13979202896091, -76.4261887452482),
		    (38.14159881738863, -76.42357363169077),
		    (38.14411183880505, -76.4257379185068),
		    (38.14586589933084, -76.42207661775097),
		    (38.14736951740486, -76.42292706869287),
		    (38.14604797919601, -76.4270922043564),
		    (38.15131594958007, -76.42913638660615),
		    (38.1510961533167, -76.43468776546464)]

    searcharea = [(38.14325436740429, -76.43484836856422),
			(38.14096581012227, -76.43249836715462),
			(38.14199681234503, -76.42929890209555),
			(38.14013480600455, -76.42625898927464),
			(38.14178878943476, -76.42407623343071),
			(38.14382186643293, -76.42586928641738),
			(38.14452836874776, -76.4310129102313),
			(38.14325436740429, -76.43484836856422)]

    options = {
        "wind_angle_degrees": 30,
        "path_width": meters_to_gps(30),
        "overshoot_distance": meters_to_gps(-30),
        "dist_between": meters_to_gps(30),
	"wp_altitude": 300.0
    }
    # FIXME is wp_altitude in m or ft?

    finder = Pathfinder(plane_location, searcharea, flightboundaries, options)
    waypoint_generator = WaypointGenerator(finder)
    image_generator = ImageGenerator(finder)
    kml_generator = KMLGenerator(finder)
                
    #waypoint_generator.export_qgc_waypoints()
    image_generator.create_image("output.jpg")
    kml_generator.export_kml()

if __name__ == '__main__':
    main()
