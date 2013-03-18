def get_bounding_box(points):
    smallest_x = get_smallest_x(points)
    smallest_y = get_smallest_y(points)
    largest_x = get_largest_x(points)
    largest_y = get_largest_y(points)

    return (smallest_x, smallest_y), (largest_x, largest_y)

def to_radians(degrees):
    return degrees * 3.14159 / 180

def compute_ratio(points):
    (smallest_x, smallest_y), (largest_x, largest_y) = get_bounding_box(points)
    dx = largest_x - smallest_x
    dy = largest_y - smallest_y

    return float(dy) / dx

def rotate(points, cnt, angle_radians):
    import scipy
    ar = scipy.array
    from scipy import dot, cos, sin

    pts = ar(points)
    rotated = dot(pts-cnt, ar([[cos(angle_radians), sin(angle_radians)], \
              [-sin(angle_radians), cos(angle_radians)]]))+cnt
    return list(rotated)

def get_largest_x(points):
    return max([point[0] for point in points])

def get_largest_y(points):
    return max([point[1] for point in points])

def get_smallest_x(points):
    return min([point[0] for point in points])

def get_smallest_y(points):
    return min([point[1] for point in points])

def calculate_line_segments_thru(x, boundaries):
    def sort_by_y(point):
        return point[1]

    def calculate_path_line_to_split(x):
        min_y = get_smallest_y(boundaries)
        max_y = get_largest_y(boundaries)
        return (x, min_y), (x, max_y)
    
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
        return zip(boundaries, boundaries[1:] + [boundaries[-1]]) +\
                [(boundaries[-1], boundaries[0])]

def calculate_center(polygon):
    sum_x = sum(point[0] for point in polygon)
    sum_y = sum(point[1] for point in polygon)
    return float(sum_x) / len(polygon), float(sum_y) / len(polygon)

def find_closest_perimeter(point, perimeters):
    _, perimeter = min([ 
            (min( dist(point, perimeter[0]),
                dist(point, perimeter[1]) ), perimeter )
            for perimeter in perimeters] )
    return perimeter

def pad_vertical(line_segment, padding):
    top, bottom = line_segment
    if top[1] > bottom[1]:
        top, bottom = bottom, top 

    top = (top[0],  top[1] - padding)
    bottom = (bottom[0], bottom[1] + padding)

    return top, bottom

def add_intermediates(line_segment, distance):
    import numpy
    (start_x, start_y), (stop_x, stop_y) = line_segment
    start, stop = line_segment
    if start_x != stop_x:
        # Don't add intermediate waypoints in this case
        return [start, stop]
    else:
        if start_y > stop_y:
            distance = -distance
        result = [(start_x, y) for y in numpy.arange(start_y, stop_y,
            distance)] + [stop]
        return result

def calculate_line_segments(boundaries, dx, overshoot_distance):
    import numpy

    def pad(line_segment):
        return pad_vertical(line_segment, overshoot_distance)

    start_x = get_smallest_x(boundaries)
    stop_x = get_largest_x(boundaries)
    line_segments_list = [calculate_line_segments_thru(x, boundaries)\
                          for x in numpy.arange(start_x,stop_x,dx)]

    # Flatten
    return [pad(line_segment) for line_segments in line_segments_list \
            for line_segment in line_segments]
