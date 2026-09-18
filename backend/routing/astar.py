"""A* search over a latitude/longitude cost grid."""

import heapq
import math


def find_route(grid, start, goal, avoid_margin: float = 0.0):
    cells = grid["cells"]
    step = grid["step"]
    # Pick nearest UNBLOCKED cell for start/goal — destination/origin cells
    # must not be inside the coast buffer and therefore unreachable.
    def nearest_unblocked_key(point):
        best = None
        best_d = float('inf')
        for k, cell in cells.items():
            if isinstance(cell, dict) and cell.get("blocked"):
                continue
            if isinstance(k, (list, tuple)) and len(k) == 2:
                d = distance(k, point)
            elif isinstance(k, dict):
                d = distance((k.get("lat", 0), k.get("lon", 0)), point)
            else:
                d = distance((float(k[0]), float(k[1])) if hasattr(k, '__len__') and len(k) >= 2 else (0, 0), point)
            if d < best_d:
                best_d = d
                best = k
        return best
    start_node = nearest_unblocked_key(start)
    goal_node = nearest_unblocked_key(goal)
    if start_node is None or goal_node is None:
        return []
    frontier = [(0.0, start_node)]
    came_from = {start_node: None}
    cost_so_far = {start_node: 0.0}
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal_node:
            break
        for neighbor in neighbors(current, step):
            cell = cells.get(neighbor)
            if cell is None or cell["blocked"] or cell["risk"]["overall_navigation_risk"] > 0.92 - avoid_margin * 0.01:
                continue
            next_cost = cost_so_far[current] + distance(current, neighbor) * (1.0 + cell["cost"])
            if neighbor not in cost_so_far or next_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = next_cost
                priority = next_cost + distance(neighbor, goal_node)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current
    if goal_node not in came_from:
        return []
    path = []
    current = goal_node
    while current is not None:
        path.append([current[0], current[1]])
        current = came_from[current]
    path.reverse()
    path[0] = list(start)
    path[-1] = list(goal)
    return simplify(path)


def neighbors(node, step):
    latitude, longitude = node
    for delta_latitude, delta_longitude in ((step, 0), (-step, 0), (0, step), (0, -step), (step, step), (step, -step), (-step, step), (-step, -step)):
        yield round(latitude + delta_latitude, 4), round(longitude + delta_longitude, 4)


def distance(first, second):
    return math.hypot((second[0] - first[0]) * 111.0, (second[1] - first[1]) * 111.0 * math.cos(math.radians((first[0] + second[0]) / 2.0)))


def simplify(path):
    if len(path) <= 3:
        return path
    result = [path[0]]
    for index in range(1, len(path) - 1):
        previous = result[-1]
        current = path[index]
        following = path[index + 1]
        if (current[0] - previous[0]) * (following[1] - current[1]) != (current[1] - previous[1]) * (following[0] - current[0]):
            result.append(current)
    result.append(path[-1])
    return result
