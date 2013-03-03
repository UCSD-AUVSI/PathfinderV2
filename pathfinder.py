PATH_WIDTH = 61
OVERSHOOT_DISTANCE = 61

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

def rotate_boundaries(boundaries, wind_angle_degrees):
    return boundaries, 0

def rotate_path(path, rotation_angle):
    return path
        
def main(plane_location, boundaries, wind_angle_degrees, path_width =
        PATH_WIDTH, overshoot_distance = OVERSHOOT_DISTANCE ):
    boundaries, rotation_angle = rotate_boundaries(boundaries, wind_angle_degrees)
    line_segments = calculate_line_segments(boundaries, path_width, overshoot_distance)
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


    def normalize(path, boundaries, max_x, max_y):

        def normalize_points(points):
            def normalize_point(point):
                x = float(point[0] - smallest_x)
                y = float(point[1] - smallest_y)
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

    def test_square_scaled():
        plane_location = 0.1, 0.1
        boundaries = [(0, 0), (0.1, 0), (0.1, 0.1), (0, 0.1)]
        wind_angle_degrees = 90
        path = main(plane_location, boundaries, wind_angle_degrees, 0.006, 0.006)
        print path
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


    test_square()
    test_square_scaled()
    test_rot_square()
    test_concave()

if __name__ == '__main__':
    test()
