import math
import numpy as np


class PathPlanner:
    def __init__(self, polygon_file, axis, bg_colour, gap_in_metres=2):
        # Attributes
        self.polygon_file = polygon_file  # polygon files
        self.axis = axis  # Axis to draw onto
        self.bg_colour = bg_colour  # Plot background colour
        self.gap_in_metres = gap_in_metres  # gap between nodes
        # Import the polygon as np array
        self._get_polygon()
        # Generate grid
        self._generate_grid()

    def _get_polygon(self):
        with open(self.polygon_file, 'r') as f:
            lines = f.readlines()[1:]
        n = len(lines)
        self.polygon = np.zeros((n, 2))
        for i in range(n):
            line = lines[i].strip().split(" ")
            # Swap rows to convert (lat, lon) to (x, y) where x=lon, y=lat
            self.polygon[i][0] = float(line[1])
            self.polygon[i][1] = float(line[0])
        return self.polygon

    def _generate_grid(self):
        """
        Generate an equally-spaced grid of points inside a rectangle
        formed by two points: top_left and bottom_right
        """
        # Get top left and bottom right coordinates
        x_left, y_bottom = np.amin(self.polygon, 0)
        x_right, y_top = np.amax(self.polygon, 0)
        x_avg = (x_left + x_right) / 2
        y_avg = (y_top + y_bottom) / 2
        # Convert 2 m gap to decimal degrees using conversion factor
        gap_x = self.gap_in_metres*abs(x_left - x_right) / \
            _get_distance_metres(x_left, y_avg, x_right, y_avg)
        gap_y = self.gap_in_metres*abs(y_top - y_bottom) / \
            _get_distance_metres(x_avg, y_top, x_avg, y_bottom)
        grid_shape = (int(abs(y_top - y_bottom) / gap_y)+1,
                      int(abs(x_right - x_left) / gap_x)+1, 2)
        self.grid = np.zeros(grid_shape)
        for i in range(grid_shape[1]):
            for j in range(grid_shape[0]):
                self.grid[j][i][0] = x_left + gap_x*i
                self.grid[j][i][1] = y_top - gap_y*j
        return self.grid

    def plot_path(self):
        """
        Plot grid of nodes with polygon overlaid on top. Nodes inside
        polygon are highlighted in red.

        Call signature
        >>> backend = PathPlanner(polygon_file, axis, bg_colour)
        >>> backend.plot_path()

        Plots the highlighted nodes to the given axis and make axis
        background colour bg_colour.
        """
        for row in self.grid:
            for point in row:
                if _is_inside_polygon(self.polygon, point):
                    self.axis.plot(point[0], point[1], 'rx')
                else:
                    self.axis.plot(point[0], point[1], 'kx')
        self.axis.plot(self.polygon[:, 0], self.polygon[:, 1], 'x-')
        self.axis.set_title("Path")
        self.axis.set_xlabel("Longitude (deg)")
        self.axis.set_ylabel("Latitude (deg)")
        self.axis.set_facecolor(self.bg_colour)

    def export_path(self, export_file):
        """
        Path consists of highlighted nodes in the right order. Start
        of file has file format. No home location is set. All nodes
        are stored in waypoint file format.

        Call signature
        >>> backend = PathPlanner(polygon_file, axis, bg_colour)
        >>> backend.export_path(export_file)

        Export the path to text file at the given directory export_file.
        """
        # Format
        output = "QGC WPL 110\n"
        # Home location (need to change this dynamically)
        # Currently disabled because no need to change location, MP will figure out automatically
        # output += "0\t1\t0\t16\t0\t0\t0\t0\t50.937248\t-1.404930\t-0.060000\t1\n"
        count = 1
        for i, row in enumerate(self.grid):
            if i % 2 == 1:
                row = np.flip(row, 0)
            for point in row:
                if _is_inside_polygon(self.polygon, point):
                    output += f"{count}\t0\t3\t16\t0.0\t0.0\t0.0\t0.0\t{point[1]:.8f}\t{point[0]:.8f}\t100.0\t1\n"
                    count += 1

        with open(export_file, "w") as f:
            f.write(output)


def _get_distance_metres(lon1, lat1, lon2, lat2):
    """
    Approximate distance (m) from http://www.movable-type.co.uk/scripts/latlong.html
    """
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1
    a = math.sin(0.5*dLat)**2 + math.sin(0.5*dLon)**2 * \
        math.cos(lat1) * math.cos(lat2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    return 6378100.0 * c


def _on_segment(p, q, r):
    """
    Check if q lies on line segment pr given p, q, r are colinear.
    https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
    """
    if ((q[0] <= max(p[0], r[0])) and
        (q[0] >= min(p[0], r[0])) and
        (q[1] <= max(p[1], r[1])) and
            (q[1] >= min(p[1], r[1]))):
        return True
    return False


def _orientation(p, q, r):
    val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))
    if val == 0:
        return 0  # colinear
    if val > 0:
        return 1  # clockwise
    if val < 0:
        return 2  # couterclockwise


def _is_intersect(p1, q1, p2, q2):
    """
    Check if segment p1q1 intersects with p2q2 or not
    https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    """
    # Find the 4 orientations required for
    # the general and special cases
    o1 = _orientation(p1, q1, p2)
    o2 = _orientation(p1, q1, q2)
    o3 = _orientation(p2, q2, p1)
    o4 = _orientation(p2, q2, q1)

    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True

    # Special Cases
    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if ((o1 == 0) and _on_segment(p1, p2, q1)):
        return True
    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if ((o2 == 0) and _on_segment(p1, q2, q1)):
        return True
    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if ((o3 == 0) and _on_segment(p2, p1, q2)):
        return True
    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if ((o4 == 0) and _on_segment(p2, q1, q2)):
        return True

    # If none of the cases
    return False


def _is_inside_polygon(polygon, point):
    # Number of vertices
    n = len(polygon)
    # Extreme point that lies 1 unit outside the right-most vertex of polygon
    extreme = [polygon[:, 1].max() + 1, point[1]]
    i = 0
    intersect_cnt = 0
    while True:
        next = (i + 1) % n
        # Check if the line segment from 'point' to
        # 'extreme' intersects with the line
        # segment from 'polygon[i]' to 'polygon[next]'
        if _is_intersect(polygon[i], polygon[next], point, extreme):
            # If the point 'p' is colinear with line
            # segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if _orientation(polygon[i], point, polygon[next]) == 0:
                return _on_segment(polygon[i], point, polygon[next])
            intersect_cnt += 1
        i = next
        if (i == 0):
            break
    # Return true if count is odd, false otherwise
    return (intersect_cnt % 2 == 1)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    bg_colour = "#d9d9d9"
    fig = plt.figure(tight_layout=True, facecolor=bg_colour)
    axis = fig.add_subplot(111)
    backend = PathPlanner("rla_app_files/lawn-polygon.poly", axis, bg_colour)
    backend.plot_path()
    backend.export_path("rla_app_files/polygon-path.txt")
    plt.show()
