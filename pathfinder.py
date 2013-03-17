import geometry_operations

class Pathfinder:
    PATH_WIDTH = 61
    OVERSHOOT_DISTANCE = 61
    MAX_DISTANCE_BETWEEN_WAYPOINTS = 50
    FONT_SIZE = 42

    def __calculate_path(self, plane_location, perimeters):

        path = [plane_location]
        _perimeters = list(perimeters)

        while _perimeters:
            perimeter = geometry_operations.find_closest_perimeter(plane_location, _perimeters)
            if geometry_operations.dist(plane_location, perimeter[0]) < geometry_operations.dist(plane_location, perimeter[1]):
                first_point, second_point = perimeter
            else:
                second_point, first_point = perimeter
            path += [first_point, second_point]
            _perimeters.remove(perimeter)
            plane_location = second_point

        return path


    def __add_intermediate_waypoints(self, path):
        def add_intermediates(line):
            return geometry_operations.add_intermediates(line, self.max_distance_between_waypoints)

        path_lines = geometry_operations.calculate_perimeters(path)[:-1]
        new_path = [add_intermediates(line) for line in path_lines]
        return [point for points in new_path for point in points]

    def __init__(self, plane_location, boundaries, wind_angle_degrees, path_width =
            PATH_WIDTH, overshoot_distance = OVERSHOOT_DISTANCE,
            max_distance_between_waypoints = MAX_DISTANCE_BETWEEN_WAYPOINTS):

        def rotate_boundaries(boundaries, boundaries_center, wind_angle_radians):
            return geometry_operations.rotate(boundaries, boundaries_center, wind_angle_radians)

        def compute_path(boundaries, plane_location):
            line_segments = geometry_operations.calculate_line_segments(boundaries,
                    self.path_width, self.overshoot_distance)
            path = self.__calculate_path(plane_location, line_segments)
            return self.__add_intermediate_waypoints(path)

        def unrotate_path(path, boundaries_center, wind_angle_radians):
            return geometry_operations.rotate(path, boundaries_center, -wind_angle_radians)

        self.path_width = path_width
        self.overshoot_distance = overshoot_distance
        self.max_distance_between_waypoints = max_distance_between_waypoints
        self.boundaries = boundaries
        self.plane_location = plane_location

        wind_angle_radians = wind_angle_degrees / 180.0 * 3.14159
        boundaries_center = geometry_operations.calculate_center(boundaries)
        rotated_boundaries = rotate_boundaries(boundaries, boundaries_center,  wind_angle_radians)
        rotated_path = compute_path(rotated_boundaries, plane_location)
        self.path = unrotate_path(rotated_path, boundaries_center, wind_angle_radians)


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

            get_smallest_x = geometry_operations.get_smallest_x
            get_smallest_y = geometry_operations.get_smallest_y
            get_largest_x = geometry_operations.get_largest_x
            get_largest_y = geometry_operations.get_largest_y

            def normalize_points(points):
                def normalize_point(point):
                    x = float(point[0] - smallest_x)
                    y = float(point[1] - smallest_y)
                    return ((x/dx) * max_x, (y/dy) * max_y)

                return [normalize_point(point) for point in points]

            if not boundaries and not path:
                return [], []

            if len(boundaries) and not len(path):
                smallest_x = get_smallest_x(boundaries)
                smallest_y = get_smallest_y(boundaries)
                largest_x = get_largest_x(boundaries)
                largest_y = get_largest_y(boundaries)
            else:
                smallest_x = min(get_smallest_x(path), get_smallest_x(boundaries))
                smallest_y = min(get_smallest_y(path), get_smallest_y(boundaries))
                largest_x = max(get_largest_x(path), get_largest_x(boundaries))
                largest_y = max(get_largest_y(path), get_largest_y(boundaries))

            dx = largest_x - smallest_x
            dy = largest_y - smallest_y

            return (normalize_points(path), normalize_points(boundaries))

        if not size: 
            image_x = 1024
            image_y = int(1024 * geometry_operations.compute_ratio(self.boundaries))
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
        font = ImageFont.truetype('arial.ttf', Pathfinder.FONT_SIZE)

        if len(path) > 1:
            for index,segment in enumerate(geometry_operations.calculate_perimeters(path)[:-1]):
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


if __name__ == '__main__':

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
