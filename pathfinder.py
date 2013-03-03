PATH_WIDTH_METERS = 61
OVERSHOOT_DISTANCE_METERS = 61

def point_inside_polygon(point, polygon):
    from shapely.geometry import Polygon, Point
    _polygon = Polygon([point1 for point1, point2 in polygon])
    _point = Point(point) 
    return _point.within(_polygon) or _polygon.boundary.contains(_point)

def get_left_top(perimeters):
    left = min([min(point1[0],point2[0]) for point1, point2 in perimeters])
    top = min([min(point1[1],point2[1]) for point1, point2 in perimeters])
    return left,top

def get_rightmost(perimeters):
    return max([max(point1[0] ,point2[0]) for point1, point2 in perimeters])

def to_radians(degrees):
    return degrees * PI / 180

def calculate_line_segments(perimeters, 
                            path_width_meters = PATH_WIDTH_METERS,
                            overshoot_distance_meters = OVERSHOOT_DISTANCE_METERS):

    dx = path_width_meters
    start_x,y = get_left_top(perimeters)
    stop_x = get_rightmost(perimeters)
    line_segments_list = [calculate_line_segments_thru((x,y),
                        perimeters,
                        overshoot_distance_meters) for x in
                        range(start_x,stop_x,dx)]


    # Flatten
    return [line_segment for line_segments in line_segments_list for
        line_segment in line_segments]

def calculate_line_segments_thru(point, perimeters, overshoot_distance_meters):

    below_point = calculate_intersection_below(point,
                                               perimeters,
                                               overshoot_distance_meters)

    print "Point: ",point
    print "Below_Point: ",below_point

    if not below_point and point_inside_polygon(point,perimeters):
        below_point = point 


    above_point = calculate_intersection_above(point,
                                               perimeters,
                                               overshoot_distance_meters)

    if not above_point and point_inside_polygon(point,perimeters):
        above_point = point 

    if above_point == below_point:
        return []

    # print "Below_Point: ", below_point
    # print "Above_Point: ", above_point

    if above_point:
        segments_above = calculate_segments_above(above_point,
                                                  perimeters,
                                                  overshoot_distance_meters)
    else:
        segments_above = []

    if below_point:
        segments_below = calculate_segments_below(below_point,
                                                  perimeters,
                                                  overshoot_distance_meters)
    else:
        segments_below = []

    if point_inside_polygon(point, perimeters) and above_point and below_point:
        segment = ((below_point[0], below_point[1] + overshoot_distance_meters),
                   (above_point[0], above_point[1] - overshoot_distance_meters))
        return segments_below + [segment] + segments_above
    else:
        return segments_below + segments_above

def calculate_segments_above(point, perimeters, overshoot_distance_meters):
            below_point = calculate_intersection_above(point,
                                                       perimeters,
                                                       overshoot_distance_meters)

            if below_point:
                above_point = calculate_intersection_above(below_point,
                                                           perimeters,
                                                           overshoot_distance_meters)

                if above_point:
                    segments_above_this = calculate_segments_above(above_point,
                                                                   perimeters,
                                                                   overshoot_distance_meters)
                    
                    if point_inside(point, perimeters):
                        segment = ((below_point[0], below_point[1] + overshoot_distance_meters),
                                   (above_point[0], above_point[1] - overshoot_distance_meters))
                        return [segment] + segments_above_this
                    else:
                        return segments_above_this

                else:
                    return []
            else:
                return []


def calculate_segments_below(point, perimeters, overshoot_distance_meters):
            above_point = calculate_intersection_below(point,
                                                       perimeters,
                                                       overshoot_distance_meters)

            if above_point:
                below_point = calculate_intersection_below(above_point,
                                                           perimeters,
                                                           overshoot_distance_meters)

                if below_point:
                    segments_below_this = calculate_segments_below(below_point,
                                                                   perimeters,
                                                                   overshoot_distance_meters)
                    
                    if (point_inside_polygon(point,perimeters)):
                        segment = ((below_point[0], below_point[1] + overshoot_distance_meters),
                                   (above_point[0], above_point[1] - overshoot_distance_meters))
                        return [segment] + segments_below_this
                    else:
                        return segments_below_this

                else:
                    return []
            else:
                return []

def within (value, bound1, bound2):
    if bound1 < value:
        return bound1 < value < bound2
    else:
        return bound1 > value > bound2

def calculate_intersections(point, perimeters):
    def intersect(point, segment):
        percent = ( point[0] - segment[0][0] ) / (segment[1][0] - segment[0][0])
        y = (segment[1][1] - segment[0][1]) * percent + segment[0][1]
        return point[0], y

    def intersects(point, perimeter):
        if perimeter[1][0] - perimeter[0][0] == 0:
            return False
        return within(point[0], perimeter[0][0], perimeter[1][0])

    return [intersect(point, perimeter) for perimeter in perimeters if intersects(point, perimeter)]

def calculate_intersection_above(point, perimeters, overshoot_distance_meters):

    intersections = calculate_intersections(point, perimeters)
    above_intersections = [intersect for intersect in intersections if
            intersect[1] < point[1]]

    if len(above_intersections) == 0:
        return None
    
    _, intersection = min([((point[1] - intersect[1]), intersection) for
            intersection in above_intersections])

    return intersection

def calculate_intersection_below(point, perimeters, overshoot_distance_meters):

    intersections = calculate_intersections(point, perimeters)

    below_intersections = [intersect for intersect in intersections if
            intersect[1] > point[1]]

    if len(below_intersections) == 0:
        return None
    
    _, intersection = min([((intersection[1] - point[1]), intersection) for
        intersection in below_intersections])

    return intersection

def dist(point1, point2):
    from math import sqrt
    return sqrt( (point2[1] - point1[1]) ** 2 + (point1[0] - point1[0]) ** 2 )

def calculate_perimeters(boundaries):
    return zip(boundaries,boundaries[1:] + [boundaries[-1]]) + [(boundaries[-1],
        boundaries[0])]

def find_closest_perimeter(point, perimeters):
    distance, perimeter = min([ 
            (min( dist(point, perimeter[0]), dist(point, perimeter[1]) ), perimeter )
            for perimeter in perimeters] )
    return perimeter

def calculate_path(plane_location, perimeters):
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

def rotate_boundaries(boundaries, wind_angle_degrees):
    return boundaries, 0

def rotate_path(path, rotation_angle):
    return path
        
def main(plane_location, boundaries, wind_angle_degrees):
    boundaries, rotation_angle = rotate_boundaries(boundaries, wind_angle_degrees)
    perimeters = calculate_perimeters(boundaries)
    line_segments = calculate_line_segments(perimeters)
    path = calculate_path(plane_location, line_segments)
    path = rotate_path(path, -rotation_angle)
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

    def get_largest_x(points):
        return max([point[0] for point in points])

    def get_largest_y(points):
        return max([point[1] for point in points])

    def get_smallest_x(points):
        return min([point[0] for point in points])

    def get_smallest_y(points):
        return min([point[1] for point in points])

    def normalize(path, boundaries, max_x, max_y):

        def normalize_points(points):
            def normalize_point(point):
                x = float(point[0] - smallest_x)
                y = float(point[1] - smallest_y)
                if x / dx > 1 or y / dy > 1:
                    print smallest_y
                    print "WTF"
                return ((x/dx) * max_x, (y/dy) * max_y)

            return [normalize_point(point) for point in points]

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

    for segment in calculate_perimeters(path)[:-1]:
        draw.line(segment, '#0F0')

    image.save(filename, 'jpeg')

def test():
    def test_square():
        plane_location = 1, 1
        boundaries = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
        wind_angle_degrees = 90
        path = main(plane_location, boundaries, wind_angle_degrees)
        create_image(boundaries, path, "square.jpg")
    def test_rot_square():
        plane_location = 1, 1
        boundaries = [(500, 0), (0,500), (-500, 0), (0, -500)]
        wind_angle_degrees = 90
        path = main(plane_location, boundaries, wind_angle_degrees)
        print path, boundaries
        create_image(boundaries, path, "rot_square.jpg")

    # test_square()
    test_rot_square()

if __name__ == '__main__':
    test()
