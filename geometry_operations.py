import scipy, numpy
import shapely.geometry
from math import pi, sqrt
from scipy import dot, cos, sin

def get_bounding_box(points):
    """
        Returns two points that represent the opposite corners of
        the min box that contains the given points
    """

    assert len(points) > 0
    min_x = get_min_x(points)
    min_y = get_min_y(points)
    max_x = get_max_x(points)
    max_y = get_max_y(points)

    return (min_x, min_y), (max_x, max_y)

def to_radians(degrees):
    return degrees * pi / 180

def compute_ratio(bounding_box):
    """
        Returns the ratio of the bounding box (y/x)
    """
    (min_x, min_y), (max_x, max_y) = bounding_box
    dx = max_x - min_x
    dy = max_y - min_y

    return abs(float(dy) / dx)

def rotate(points, cnt, angle_radians):
    """
        Returns a copy of *points*, rotated around *cnt* by
        *angle_radians*
    """
    ar = scipy.array

    pts = ar(points)
    rotated = dot(pts-cnt, ar([[cos(angle_radians), sin(angle_radians)], \
              [-sin(angle_radians), cos(angle_radians)]]))+cnt
    return list(rotated)

def get_max_x(points):
    assert len(points) > 0
    return max([point[0] for point in points])

def get_max_y(points):
    assert len(points) > 0
    return max([point[1] for point in points])

def get_min_x(points):
    assert len(points) > 0
    return min([point[0] for point in points])

def get_min_y(points):
    assert len(points) > 0
    return min([point[1] for point in points])

def calculate_line_segments_thru(x, boundaries):
    """
        Renders the vertical line segment(s) that pass through the boundaries
        and the line x=*x*. If the line intersects the boundaries only at a
        single point, a line segment with length 0 is returned.
    """
    def sort_by_y(point):
        return point[1]

    def calculate_path_line_to_split(x):
        """
            Returns a line segment that passes through x=*x*, and
            which has y values between the min_y, and max_y of the 
            search area boundaries
        """
        min_y = get_min_y(boundaries)
        max_y = get_max_y(boundaries)
        return (x, min_y), (x, max_y)
    
    line = calculate_path_line_to_split(x)
    intersections = calculate_intersections(line, boundaries)

    if len(intersections) == 1:
        # If there is only one intersection, then return a line segment
        # with length zero at the intersection point. This ensures 
        # that this point will be visited by the plane
        intersection = intersections[0]
        return [(intersection, intersection)]
    else:
        # Segment this line segment such that parts where the path is not
        # over the search area are removed.
        ordered_intersections = sorted(intersections, key = sort_by_y) 
        segments = to_line_segments(ordered_intersections)[:-1] 
        return segments[::2]

def calculate_intersections(line_segment, boundaries):
    """
        Calculates the intersections between a line segment and a
        polygon. Returns a list of points representing the intersections
    """
    s_line = shapely.geometry.LineString(line_segment)
    s_boundaries = shapely.geometry.LineString(boundaries + [boundaries[0]])
    intersection = s_line.intersection(s_boundaries)

    if ( isinstance(intersection, shapely.geometry.Point) or
         isinstance(intersection, shapely.geometry.LineString) ):
        return list(intersection.coords)

    intersect_points = [list(geometry.coords) for geometry in intersection]

    return [point for points in intersect_points for point in points]


def dist(point1, point2):
    """
        Returns the euclidian distance between two points.
    """
    return sqrt( (point2[1] - point1[1]) ** 2 + (point2[0] - point1[0]) ** 2 )

def to_line_segments(points):
    """
        Returns an list of line_segments generated from an list of points
    """
    if len(points) < 2:
        return []
    else:
        return zip(points, points[1:]) + [(points[-1], points[0])]

def calculate_center(polygon):
    """
        Returns the point that is in the center of a polygon
    """

    assert len(polygon) > 0
    sum_x = sum(point[0] for point in polygon)
    sum_y = sum(point[1] for point in polygon)
    return float(sum_x) / len(polygon), float(sum_y) / len(polygon)

def find_closest_line_segment(point, line_segments):
    """
        Returns the line segment that contains the point that is nearest
        to *point*
    """

    assert len(line_segments) > 0
    def distance_to_line_segment(line_segment):
        start_point, end_point = line_segment
        return min(dist(point, start_point), dist(point, end_point))
    
    return sorted(line_segments, key = distance_to_line_segment)[0]

def pad_vertical(line_segment, padding):
    """
        Returns a copy of *line_segment* with *padding* added to the y-value
        of the top point and *padding* subtracted from the y-value of the bottom
        points
    """

    if not is_vertical(line_segment):
        raise AssertionError("pad_vertical should only be used on vertical line_segments")

    (start_x, start_y) , (stop_x, stop_y) = line_segment

    if start_y > stop_y:
        return (start_x, start_y + padding), (stop_x, stop_y - padding)
    else:
        return (start_x, start_y - padding), (stop_x, stop_y + padding)

def is_vertical(line_segment):
    (start_x, start_y), (stop_x, stop_y) = line_segment
    return start_x == stop_x

def partition_line_segment_if_vertical(line_segment, distance):
    """
        Splits up a vertical line segment into multiple line segments
        with maximum length *distance*. 
        If the line segment is not vertical, it returns the original 
        line segment
    """
    assert distance > 0
    if not is_vertical(line_segment):
        # Don't add intermediate waypoints in this case
        return line_segment
    else:
        start, stop = line_segment
        (start_x, start_y), (stop_x, stop_y) = line_segment
        if start_y > stop_y:
            distance = -distance
        result = [(start_x, y) for y in numpy.arange(start_y, stop_y,
            distance)] + [stop]
        return result

def calculate_line_segments(boundaries, dx, overshoot_distance):
    """
        Returns the line_segments that the plane must traverse to search
        *boundaries*
    """

    def pad(line_segment):
        return pad_vertical(line_segment, overshoot_distance)

    start_x = get_min_x(boundaries)
    stop_x = get_max_x(boundaries)
    line_segments_list = [calculate_line_segments_thru(x, boundaries)\
                          for x in numpy.arange(start_x,stop_x,dx)]

    # Flatten
    return [pad(line_segment) for line_segments in line_segments_list \
            for line_segment in line_segments]
