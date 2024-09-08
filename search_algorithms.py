import math
from collections import deque


def distance(vec1, vec2):
    return math.sqrt((vec2.x - vec1.x)**2 + (vec2.y - vec1.y)**2)

def dfs_find_path(current_node, finish_node, visited=None, path=None):

    if visited is None:
        visited = set()
    if path is None:
        path = []

    visited.add(current_node)
    path.append(current_node)

    if current_node == finish_node:
        return path

    for direction, neighbor in current_node.neighbors.items():
        if neighbor is not None and neighbor not in visited:
            result = dfs_find_path(neighbor, finish_node, visited, path)
            if result:
                return result

    path.pop()
    return None


def bfs_find_path(start_node, finish_node):

    queue = deque([(start_node, [start_node])])
    visited = set()

    while queue:
        current_node, path = queue.popleft()

        if current_node == finish_node:
            return path

        visited.add(current_node)

        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return None


def dijkstra_find_path(start_node, finish_node):

    node_queue = [(0, start_node, [start_node])]
    distances = {start_node: 0}

    visited = set()

    while node_queue:

        node_queue.sort(key=lambda x: x[0])
        current_distance, current_node, path = node_queue.pop(0)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == finish_node:
            return path

        for direction, neighbor in current_node.neighbors.items():
            if neighbor is None:
                continue
            if neighbor not in visited:
                distance_to_neighbor = distance(current_node.position, neighbor.position)
                new_distance = current_distance + distance_to_neighbor

                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    node_queue.append((new_distance, neighbor, path + [neighbor]))

    return None

