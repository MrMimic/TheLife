from typing import List
from math import hypot


def point_is_in_map(map_coords: List[List[int]], point_coordinates: List[int]) -> bool:
    """
        Check if a point is in the map.

        Args:
            map_size (int): The size of the map.
            point_coordinates (List[int]): The coordinates of the point.
        """
    # Map size should be a square centered around zero

    x1, y1 = map_coords[0]
    x2, y2 = map_coords[1]
    x, y = point_coordinates
    if (x1 < x and x < x2) and (y1 < y and y < y2):
        return True
    else:
        return False

def compute_distance(x: List[int], y: List[int]) -> float:
    """
    Compute the distance between two points.

    Args:
        x (List[int]): The first point.
        y (List[int]): The second point.

    Returns:
        float: The distance between the two points.
    """
    return round(hypot(x[0] - y[0], x[1] - y[1]), 3)
