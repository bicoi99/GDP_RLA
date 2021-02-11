"""
Lon - x-axis
Lat - y-axis
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import math
from dronekit import connect, Command
from pymavlink import mavutil


def get_polygon(file: str) -> np.ndarray:
    with open(file, 'r') as f:
        # First line is comment
        lines = f.readlines()[1:]
        f.close()
    n = len(lines)
    polygon = np.zeros((n, 2))
    for i in range(n):
        line = lines[i].strip().split(" ")
        # Swap rows to convert (lat, lon) to (x, y) where x=lon, y=lat
        polygon[i][0] = float(line[1])
        polygon[i][1] = float(line[0])
    return polygon


def generate_grid(polygon, gap_in_metres):
    """
    Generate an equally-spaced grid of points inside a rectangle
    formed by two points: top_left and bottom_right
    """
    # Get top left and bottom right coordinates
    x_left, y_bottom = np.amin(polygon, 0)
    x_right, y_top = np.amax(polygon, 0)
    x_avg = (x_left + x_right) / 2
    y_avg = (y_top + y_bottom) / 2
    # Convert 2 m gap to decimal degrees using conversion factor
    gap_x = gap_in_metres*abs(x_left - x_right) / \
        get_distance_metres(x_left, y_avg, x_right, y_avg)
    gap_y = gap_in_metres*abs(y_top - y_bottom) / \
        get_distance_metres(x_avg, y_top, x_avg, y_bottom)
    grid_shape = (int(abs(y_top - y_bottom) / gap_y)+1,
                  int(abs(x_right - x_left) / gap_x)+1, 2)
    grid = np.zeros(grid_shape)
    for i in range(grid_shape[1]):
        for j in range(grid_shape[0]):
            grid[j][i][0] = x_left + gap_x*i
            grid[j][i][1] = y_top - gap_y*j
    return grid


def get_distance_metres(lon1, lat1, lon2, lat2):
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


def on_segment(p, q, r):
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


def orientation(p, q, r):
    val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))
    if val == 0:
        return 0  # colinear
    if val > 0:
        return 1  # clockwise
    if val < 0:
        return 2  # couterclockwise


def is_intersect(p1, q1, p2, q2):
    """
    Check if segment p1q1 intersects with p2q2 or not
    https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    """
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True

    # Special Cases
    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if ((o1 == 0) and on_segment(p1, p2, q1)):
        return True
    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if ((o2 == 0) and on_segment(p1, q2, q1)):
        return True
    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if ((o3 == 0) and on_segment(p2, p1, q2)):
        return True
    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if ((o4 == 0) and on_segment(p2, q1, q2)):
        return True

    # If none of the cases
    return False


def is_inside_polygon(polygon, point):
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
        if is_intersect(polygon[i], polygon[next], point, extreme):
            # If the point 'p' is colinear with line
            # segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if orientation(polygon[i], point, polygon[next]) == 0:
                return on_segment(polygon[i], point, polygon[next])
            intersect_cnt += 1
        i = next
        if (i == 0):
            break
    # Return true if count is odd, false otherwise
    return (intersect_cnt % 2 == 1)


def draw_polygon(polygon):
    plt.plot(polygon[:, 0], polygon[:, 1], 'x-')
    plt.title("Polygon")
    plt.xlabel("Longitude (deg)")
    plt.ylabel("Latitude (deg)")
    plt.tight_layout()
    plt.show()


def draw_grid(grid, polygon):
    for row in grid:
        for point in row:
            plt.plot(point[0], point[1], 'kx')
    plt.plot(polygon[:, 0], polygon[:, 1], 'x-')
    plt.title("Grid of nodes")
    plt.xlabel("Longitude (deg)")
    plt.ylabel("Latitude (deg)")
    plt.tight_layout()
    plt.show()


def draw_highlighted_node(grid, polygon):
    for row in grid:
        for point in row:
            if is_inside_polygon(polygon, point):
                plt.plot(point[0], point[1], 'rx')
            else:
                plt.plot(point[0], point[1], 'kx')
    plt.plot(polygon[:, 0], polygon[:, 1], 'x-')
    plt.title("Nodes inside polygon")
    plt.xlabel("Longitude (deg)")
    plt.ylabel("Latitude (deg)")
    plt.tight_layout()
    plt.show()


def save_mission_to_file(file, grid, polygon):
    """
    Mission consists of highlighted nodes in the right order
    """
    # Format
    output = "QGC WPL 110\n"
    # Home location (need to change this dynamically)
    output += "0\t1\t0\t16\t0\t0\t0\t0\t50.937248\t-1.404930\t-0.060000\t1\n"
    count = 1
    for i, row in enumerate(grid):
        if i % 2 == 1:
            row = np.flip(row, 0)
        for point in row:
            if is_inside_polygon(polygon, point):
                output += f"{count}\t0\t3\t16\t0.0\t0.0\t0.0\t0.0\t{point[1]:.8f}\t{point[0]:.8f}\t100.0\t1\n"
                count += 1

    with open(file, "w") as f:
        f.write(output)
        f.close()


def write_mission(cmds, grid, polygon):
    print("Clear previous mission")
    cmds.download()
    cmds.wait_ready()
    cmds.clear()
    # Make highlighted nodes waypoints
    print("Adding new missions")
    for i, row in enumerate(grid):
        if i % 2 == 1:
            row = np.flip(row, 0)
        for point in row:
            if is_inside_polygon(polygon, point):
                cmds.add(Command(
                    0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,
                    point[1], point[0], 100
                ))
    # RTL
    cmds.add(Command(
        0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ))
    print("Uploading mission")
    cmds.upload()


def draw_highlighted_node(polygon_file_path, ax, bg_colour):
    polygon = get_polygon(polygon_file_path)
    grid = generate_grid(polygon, 2)
    # Use matplotlib.figure Figure rather than pyplot Figure
    # to avoid Tk not closing
    for row in grid:
        for point in row:
            if is_inside_polygon(polygon, point):
                ax.plot(point[0], point[1], 'rx')
            else:
                ax.plot(point[0], point[1], 'kx')
    ax.plot(polygon[:, 0], polygon[:, 1], 'x-')
    ax.set_title("Path")
    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_facecolor(bg_colour)
    # temp solution before OOP implemented
    return polygon, grid


if __name__ == "__main__":
    # Get polygon
    polygon = get_polygon("rla_app_files/lawn-polygon.poly")
    # Generate node grid
    grid = generate_grid(polygon, 2)
    # draw_polygon(polygon)
    # draw_grid(grid, polygon)
    # draw_highlighted_node(grid, polygon)
    save_mission_to_file(
        "dronekit_scripts/generated_path_inside_polygon.txt", grid, polygon)
    print("Connecting to vehicle")
    vehicle = connect("127.0.0.1:14550", wait_ready=True)
    write_mission(vehicle.commands, grid, polygon)
