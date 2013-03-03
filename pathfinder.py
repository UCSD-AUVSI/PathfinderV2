PATH_WIDTH = 61
OVERSHOOT_DISTANCE = 61
MAX_DISTANCE_BETWEEN_WAYPOINTS = 50

def rotate(points,cnt,angle_radians):
    import scipy
    dot = scipy.dot
    ar = scipy.array
    cos = scipy.cos
    sin = scipy.sin
    pts = ar(points)
    '''pts = {} Rotates points(nx2) about center cnt(2) by angle ang(1) in radian'''
    rotated = dot(pts-cnt,ar([[cos(angle_radians),sin(angle_radians)],[-sin(angle_radians),cos(angle_radians)]]))+cnt
    return list(rotated)


def get_largest_x(points):
    return max([point[0] for point in points])

def get_largest_y(points):
    return max([point[1] for point in points])

def get_smallest_x(points):
    return min([point[0] for point in points])

def get_smallest_y(points):
    return min([point[1] for point in points])

def get_left_top(boundaries):
    return get_smallest_x(boundaries), get_smallest_y(boundaries)

def calculate_line_segments(boundaries, path_width = PATH_WIDTH,
                            overshoot_distance = OVERSHOOT_DISTANCE):
    import numpy

    def pad(line_segment):
        top, bottom = line_segment
        if top[1] > bottom[1]:
            top, bottom = bottom, top 

        top = (top[0],  top[1] - overshoot_distance)
        bottom = (bottom[0], bottom[1] + overshoot_distance)
        
        return (top, bottom)

    dx = path_width
    start_x,y = get_left_top(boundaries)
    stop_x = get_largest_x(boundaries)
    line_segments_list = [calculate_line_segments_thru(x, boundaries, overshoot_distance) for x in
                        numpy.arange(start_x,stop_x,dx)]

    # Flatten
    return [pad(line_segment) for line_segments in line_segments_list for line_segment in line_segments]

def calculate_line_segments_thru(x, boundaries, overshoot_distance):
    def sort_by_y(point):
        return point[1]

    def calculate_path_line_to_split(x):
        min_y = get_smallest_y(boundaries)
        max_y = get_largest_y(boundaries)
        return ((x, min_y), (x, max_y))
    
    line = calculate_path_line_to_split(x)
    intersections = calculate_intersections(line, boundaries)

    if not intersections:
        return []
    else:
        if len(intersections) == 1:
           intersections += intersections
        ordered_intersections = sorted(intersections, key = sort_by_y) 
        segments = calculate_perimeters(ordered_intersections)[:-1] 
        return segments[::2]

def calculate_intersections(line, boundaries):
    from shapely.geometry import LineString, Point

    s_line = LineString(line)
    s_boundaries = LineString(boundaries + [boundaries[0]])
    intersection = s_line.intersection(s_boundaries)
    if isinstance(intersection, Point) or isinstance(intersection, LineString):
        return list(intersection.coords)
    intersect_points = [list(geometry.coords) for geometry in intersection]
    return [point for points in intersect_points for point in points]


def dist(point1, point2):
    from math import sqrt
    return sqrt( (point2[1] - point1[1]) ** 2 + (point2[0] - point1[0]) ** 2 )

def calculate_perimeters(boundaries):
    if len(boundaries) < 2:
        return 0
    else:
        return zip(boundaries,boundaries[1:] + [boundaries[-1]]) + [(boundaries[-1],
            boundaries[0])]


def calculate_path(plane_location, perimeters):
    def find_closest_perimeter(point, perimeters):
        distance, perimeter = min([ 
                (min( dist(point, perimeter[0]), dist(point, perimeter[1]) ), perimeter )
                for perimeter in perimeters] )
        return perimeter

    path = [plane_location]
    _perimeters = list(perimeters)

    while _perimeters:
        perimeter = find_closest_perimeter(plane_location, _perimeters)
        if dist(plane_location, perimeter[0]) < dist(plane_location, perimeter[1]):
            first_point, second_point = perimeter
        else:
            second_point, first_point = perimeter
        path += [first_point, second_point]
        _perimeters.remove(perimeter)
        plane_location = second_point

    return path

def calculate_center(polygon):
    sum_x = sum(point[0] for point in polygon)
    sum_y = sum(point[1] for point in polygon)
    return float(sum_x) / len(polygon), float(sum_y) / len(polygon)

def add_intermediate_waypoints(path, distance_between_waypoints):
    return path

def main(plane_location, boundaries, wind_angle_degrees, path_width =
        PATH_WIDTH, overshoot_distance = OVERSHOOT_DISTANCE,
        max_distance_between_waypoints = MAX_DISTANCE_BETWEEN_WAYPOINTS):
    wind_angle_radians = wind_angle_degrees / 180.0 * 3.14159
    boundaires_center = calculate_center(boundaries)
    boundaries = rotate(boundaries, boundaires_center, wind_angle_radians)
    line_segments = calculate_line_segments(boundaries, path_width, overshoot_distance)
    path = calculate_path(plane_location, line_segments)
    path = add_intermediate_waypoints(path, max_distance_between_waypoints)
    path = rotate(path, boundaires_center, -wind_angle_radians)
    return path

def compute_ratio(points):
    smallest_x = min([point[0] for point in points])
    smallest_y = min([point[1] for point in points])

    largest_x = max([point[0] for point in points])
    largest_y = max([point[1] for point in points])

    dx = largest_x - smallest_x
    dy = largest_y - smallest_y

    return float(dy) / dx

def create_image(boundaries, path, filename, size = None):
    from PIL import Image, ImageDraw
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
        image_y = int(1024 * compute_ratio(boundaries))
    else:
        image_x, image_y = size

    padded_image_x, padded_image_y = pad_dimensions(image_x, image_y, BORDER_PX)

    image = Image.new("RGB", (padded_image_x, padded_image_y))
    draw = ImageDraw.Draw(image)

    path, boundaries = normalize(path, boundaries, image_x, image_y)

    path = pad_points(path, BORDER_PX)
    boundaries = pad_points(boundaries, BORDER_PX)


    for segment in calculate_perimeters(boundaries):
        draw.line(segment, '#F00')

    if len(path) > 1:
        for index,segment in enumerate(calculate_perimeters(path)[:-1]):
            draw.line(segment, '#0F0')
            draw.text(segment[0], str(index+1), '#FFF')

    image.save(filename, 'jpeg')

def test():
    def test_square():
        plane_location = 1, 1
        boundaries = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
        wind_angle_degrees = 45
        path = main(plane_location, boundaries, wind_angle_degrees)
        create_image(boundaries, path, "square.jpg")
        return path

    def test_square_scaled():
        plane_location = 0.1, 0.1
        boundaries = [(0, 0), (0.1, 0), (0.1, 0.1), (0, 0.1)]
        wind_angle_degrees = 90
        path = main(plane_location, boundaries, wind_angle_degrees, 0.006, 0.006)
        create_image(boundaries, path, "square_scaled.jpg")

    def test_rot_square():
        plane_location = 1, 1
        boundaries = [(500, 0), (0,500), (-500, 0), (0, -500)]
        wind_angle_degrees = 90
        path = main(plane_location, boundaries, wind_angle_degrees)
        create_image(boundaries, path, "rot_square.jpg")

    def test_concave():
        plane_location = 1, 1
        boundaries = [(0, 0), (1000, 0), (500,500), (1000, 1000), (0, 1000)]
        wind_angle_degrees = 90
        path = main(plane_location, boundaries, wind_angle_degrees)
        create_image(boundaries, path, "concave.jpg")

    def test_gps_coords():
        plane_location = 32.961043, -117.190664
        boundaries = [(32.961043,-117.190664),
        (32.961132,-117.188443),
        (32.962393,-117.187006),
        (32.962321,-117.189924)]
        wind_angle_degrees = 90
        path = main(plane_location, boundaries, wind_angle_degrees, 0.0001, 0.0001)
        create_image(boundaries, path, "gps.jpg")
        return path


    test_square()
    test_square_scaled()
    test_rot_square()
    test_concave()
    test_gps_coords()

if __name__ == '__main__':
    test()

    def meters_to_gps(meters):
        return meters / 111122.0

    plane_location = 32.961043, -117.190664
    boundaries = [(32.961043,-117.190664),
                  (32.961132,-117.188443),
                  (32.962393,-117.187006),
                  (32.962321,-117.189924)]

    wind_angle_degrees = 0
    path_width = meters_to_gps(30)
    overshoot_distance = meters_to_gps(30)

    path = main(plane_location, boundaries, 
                wind_angle_degrees, path_width, overshoot_distance)

    print "QGC WPL 110"
    print "0\t1\t0\t16\t0\t0\t0\t0\t" + str(plane_location[0]) + "\t" + str(plane_location[1]) + "\t300.000000"+"\t1"
    for index,(x,y) in enumerate(path):
        xstr = "%.6f" % x
        ystr = "%.6f" % y
        print str(index+1) +"\t0\t3\t16\t0.000000\t0.000000\t0.000000\t0.000000\t"+ xstr+ "\t" + ystr + "\t300.000000\t1" 
        
    create_image(boundaries, path, "output.jpg")
