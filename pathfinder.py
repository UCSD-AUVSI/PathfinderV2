PATH_WIDTH = 61
OVERSHOOT_DISTANCE = 61
MAX_DISTANCE_BETWEEN_WAYPOINTS = 50
FONT_SIZE = 42

class Pathfinder:
    def __rotate(self, points, cnt, angle_radians):
        import scipy
        ar = scipy.array
        from scipy import dot, cos, sin

        pts = ar(points)
        rotated = dot(pts-cnt,ar([[cos(angle_radians),sin(angle_radians)],[-sin(angle_radians),cos(angle_radians)]]))+cnt
        return list(rotated)

    def __get_largest_x(self, points):
        return max([point[0] for point in points])

    def __get_largest_y(self, points):
        return max([point[1] for point in points])

    def __get_smallest_x(self, points):
        return min([point[0] for point in points])

    def __get_smallest_y(self, points):
        return min([point[1] for point in points])

    def __get_left_top(self, boundaries):
        return self.__get_smallest_x(boundaries), self.__get_smallest_y(boundaries)

    def __calculate_line_segments(self, boundaries):
        import numpy

        def pad(line_segment):
            top, bottom = line_segment
            if top[1] > bottom[1]:
                top, bottom = bottom, top 

            top = (top[0],  top[1] - self.overshoot_distance)
            bottom = (bottom[0], bottom[1] + self.overshoot_distance)
            
            return top, bottom

        dx = self.path_width
        start_x,y = self.__get_left_top(boundaries)
        stop_x = self.__get_largest_x(boundaries)
        line_segments_list = [self.__calculate_line_segments_thru(x, boundaries) for x in
                            numpy.arange(start_x,stop_x,dx)]

        # Flatten
        return [pad(line_segment) for line_segments in line_segments_list for line_segment in line_segments]

    def __calculate_line_segments_thru(self, x, boundaries):
        def sort_by_y(point):
            return point[1]

        def calculate_path_line_to_split(x):
            min_y = self.__get_smallest_y(boundaries)
            max_y = self.__get_largest_y(boundaries)
            return (x, min_y), (x, max_y)
        
        line = calculate_path_line_to_split(x)
        intersections = self.__calculate_intersections(line, boundaries)

        if not intersections:
            return []
        else:
            if len(intersections) == 1:
               intersections += intersections
            ordered_intersections = sorted(intersections, key = sort_by_y) 
            segments = self.__calculate_perimeters(ordered_intersections)[:-1] 
            return segments[::2]

    def __calculate_intersections(self, line, boundaries):
        from shapely.geometry import LineString, Point

        s_line = LineString(line)
        s_boundaries = LineString(boundaries + [boundaries[0]])
        intersection = s_line.intersection(s_boundaries)

        if isinstance(intersection, Point) or isinstance(intersection, LineString):
            return list(intersection.coords)

        intersect_points = [list(geometry.coords) for geometry in intersection]

        return [point for points in intersect_points for point in points]


    def __dist(self, point1, point2):
        from math import sqrt
        return sqrt( (point2[1] - point1[1]) ** 2 + (point2[0] - point1[0]) ** 2 )

    def __calculate_perimeters(self, boundaries):
        if len(boundaries) < 2:
            return 0
        else:
            return zip(boundaries,boundaries[1:] + [boundaries[-1]]) + [(boundaries[-1],
                boundaries[0])]


    def __calculate_path(self, plane_location, perimeters):
        def find_closest_perimeter(point, perimeters):
            distance, perimeter = min([ 
                    (min( self.__dist(point, perimeter[0]), self.__dist(point, perimeter[1]) ), perimeter )
                    for perimeter in perimeters] )
            return perimeter

        path = [plane_location]
        _perimeters = list(perimeters)

        while _perimeters:
            perimeter = find_closest_perimeter(plane_location, _perimeters)
            if self.__dist(plane_location, perimeter[0]) < self.__dist(plane_location, perimeter[1]):
                first_point, second_point = perimeter
            else:
                second_point, first_point = perimeter
            path += [first_point, second_point]
            _perimeters.remove(perimeter)
            plane_location = second_point

        return path

    def __calculate_center(self, polygon):
        sum_x = sum(point[0] for point in polygon)
        sum_y = sum(point[1] for point in polygon)
        return float(sum_x) / len(polygon), float(sum_y) / len(polygon)

    def __add_intermediate_waypoints(self, path):
        from numpy import arange
        def add_intermediates(start,stop):
            if start[0] != stop[0]:
                return [start, stop]
            else:
                if start[1] > stop[1]:
                    distance = -self.max_distance_between_waypoints
                else:
                    distance = self.max_distance_between_waypoints
                return [(start[0], y) for y in arange(start[1], stop[1],
                    distance)] + [stop]

        path_lines = self.__calculate_perimeters(path)[:-1]
        new_path = [add_intermediates(start, stop) for start, stop in path_lines]
        return [point for points in new_path for point in points]

    def __init__(self, plane_location, boundaries, wind_angle_degrees, path_width =
            PATH_WIDTH, overshoot_distance = OVERSHOOT_DISTANCE,
            max_distance_between_waypoints = MAX_DISTANCE_BETWEEN_WAYPOINTS):

        self.plane_location = plane_location
        self.path_width = path_width
        self.overshoot_distance = overshoot_distance
        self.max_distance_between_waypoints = max_distance_between_waypoints
        self.wind_angle_radians = wind_angle_degrees / 180.0 * 3.14159
        self.boundaries_center = self.__calculate_center(boundaries)
        self.boundaries = self.__rotate(boundaries, self.boundaries_center, self.wind_angle_radians)
        self.line_segments = self.__calculate_line_segments(self.boundaries)
        self.path = self.__calculate_path(plane_location, self.line_segments)
        self.path = self.__add_intermediate_waypoints(self.path)
        self.path = self.__rotate(self.path, self.boundaries_center, -self.wind_angle_radians)

    def __compute_ratio(self, points):
        smallest_x = min([point[0] for point in points])
        smallest_y = min([point[1] for point in points])

        largest_x = max([point[0] for point in points])
        largest_y = max([point[1] for point in points])

        dx = largest_x - smallest_x
        dy = largest_y - smallest_y

        return float(dy) / dx

    def create_image(self, filename, size = None):
        from PIL import Image, ImageDraw, ImageFont
        BORDER_PX = 50

        def pad_dimensions(x, y, padding):
            return x + 2*padding, y + 2*padding

        def pad_points(points, padding):
            def pad_point(point, padding):
                x, y = point
                return (x + padding, y + padding)

            return [pad_point(point, padding) for point in points]


        def normalize(path, boundaries, max_x, max_y):

            def normalize_points(points):
                def normalize_point(point):
                    x = float(point[0] - smallest_x)
                    y = float(point[1] - smallest_y)
                    return ((x/dx) * max_x, (y/dy) * max_y)

                return [normalize_point(point) for point in points]

            if not boundaries and not path:
                return [], []

            if len(boundaries) and not len(path):
                smallest_x = self.__get_smallest_x(boundaries)
                smallest_y = self.__get_smallest_y(boundaries)
                largest_x = self.__get_largest_x(boundaries)
                largest_y = self.__get_largest_y(boundaries)
            else:
                smallest_x = min(self.__get_smallest_x(path), self.__get_smallest_x(boundaries))
                smallest_y = min(self.__get_smallest_y(path), self.__get_smallest_y(boundaries))
                largest_x = max(self.__get_largest_x(path), self.__get_largest_x(boundaries))
                largest_y = max(self.__get_largest_y(path), self.__get_largest_y(boundaries))

            dx = largest_x - smallest_x
            dy = largest_y - smallest_y

            return (normalize_points(path), normalize_points(boundaries))

        if not size: 
            image_x = 1024
            image_y = int(1024 * self.__compute_ratio(self.boundaries))
        else:
            image_x, image_y = size

        padded_image_x, padded_image_y = pad_dimensions(image_x, image_y, BORDER_PX)

        image = Image.new("RGB", (padded_image_x, padded_image_y), '#FFFFFF')
        draw = ImageDraw.Draw(image)

        path, boundaries = normalize(self.path, self.boundaries, image_x, image_y)

        path = pad_points(path, BORDER_PX)
        boundaries = pad_points(boundaries, BORDER_PX)


        # for segment in calculate_perimeters(boundaries):
        draw.polygon(boundaries, '#999999')
        font = ImageFont.truetype('arial.ttf', FONT_SIZE)

        if len(path) > 1:
            for index,segment in enumerate(self.__calculate_perimeters(path)[:-1]):
                draw.line(segment, '#000000')
                draw.text(segment[0], str(index+1), fill='#FF0000', font=font)

        image.save(filename, 'jpeg')


    def export_qgc_waypoints(self):
        def print_header():
            print "QGC WPL 110"
        def print_home_location():
            print "0\t1\t0\t16\t0\t0\t0\t0\t" + str(self.plane_location[0]) + "\t"\
                                              + str(self.plane_location[1]) + "\t300.000000\t1"
        def print_path():
            for index,(x,y) in enumerate(self.path):
                xstr = "%.6f" % x
                ystr = "%.6f" % y
                print str(index+1)\
                    +"\t0\t3\t16\t0.000000\t0.000000\t0.000000\t0.000000\t"+\
                    xstr+ "\t" + ystr + "\t300.000000\t1" 
        
        print_header()
        print_home_location()
        print_path()

def integration_test():
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

if __name__ == '__main__':
    integration_test()

    def meters_to_gps(meters):
        return meters / 111122.0

    plane_location = 32.961043, -117.190664
    boundaries = [(32.961043,-117.190664),
                  (32.961132,-117.188443),
                  (32.962393,-117.187006),
                  (32.962321,-117.189924)]

    wind_angle_degrees = 30
    path_width = meters_to_gps(30)
    overshoot_distance = meters_to_gps(30)
    dist_between = meters_to_gps(30)

    finder = Pathfinder(plane_location, boundaries,
                wind_angle_degrees, path_width, overshoot_distance, dist_between)

    finder.export_qgc_waypoints()
        
    finder.create_image("output.jpg")
