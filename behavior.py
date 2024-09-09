import pygame
from pygame.locals import *
from nodes import *

def between_ghosts(pacman, ghosts, ghost):

    for g in ghosts:
        if g == ghost:
            continue

        if abs(ghost.position.x - g.position.x) <= 1 and abs(ghost.position.x - pacman.position.x) <= 1:
            if ghost.position.y <= pacman.position.y <= g.position.y or ghost.position.y >= pacman.position.y >= g.position.y:
                return True
        elif abs(ghost.position.y - g.position.y) <= 1 and abs(ghost.position.y - pacman.position.y) <= 1:
            if ghost.position.x <= pacman.position.x <= g.position.x or ghost.position.x >= pacman.position.x >= g.position.x:
                return True
    return False


def one_on_pacman_line(pacman, ghosts, ghost):

    if abs(ghost.position.x - pacman.position.x) >= 1 and abs(ghost.position.y - pacman.position.y) >= 1:
        return False

    for g in ghosts:
        if g == ghost:
            continue
        if abs(g.position.x - ghost.position.x) <= 1 or abs(g.position.y - ghost.position.y) <= 1:
            return False

    return True


def distance(vec1, vec2):
    return math.sqrt((vec2.x - vec1.x)**2 + (vec2.y - vec1.y)**2)


def get_entity_target(entity):

        fin = entity.target
        direction = entity.direction
        if direction != STOP and direction is not None:

            while fin.neighbors[direction] is not None:
                fin = fin.neighbors[direction]

        return fin


def get_node_directions(node, directions):

    dir = []
    for d in directions:
        if d == STOP:
            continue
        if node.neighbors[d] is not None:
            dir.append(d)
    return dir


def handle_cut(ghost):

        if ghost.direction == STOP:
            return

        directions = get_node_directions(ghost.target, ghost.directions)

        if ghost.direction in directions:
            directions.remove(ghost.direction)

        opposite_dir = ghost.direction * -1
        if opposite_dir in directions:
            directions.remove(opposite_dir)

        if len(directions) == 0:
            return

        d = ghost.direction
        gd = ghost.goalDirection(directions)
        target = ghost.target.neighbors[gd]

        path = [ghost.target, target]
        ghost.path = path

        while True:
            if target.neighbors[d] is not None:
                path.append(target.neighbors[d])
                target = target.neighbors[d]
            else:
                break
            if len(path) >= 3:
                break

        ghost.path = path
        ghost.algorithm = 'deterministic'


def ghost_default_navigation(ghost, pacman):
    ghost.algorithm = 'deterministic'
    ghost.path = None
    ghost.goal = pacman.position


def euristic1(ghost, ghosts, pacman):

    ghost.goal = pacman.position
    if ghost.target is None:
        ghost_default_navigation(ghost, pacman)
        return

    if between_ghosts(pacman, ghosts, ghost):
        ghost_default_navigation(ghost, pacman)
        return

    if one_on_pacman_line(pacman, ghosts, ghost):
        ghost_default_navigation(ghost, pacman)
        return

    ghost_target = get_entity_target(ghost)
    for g in ghosts:
        if g == ghost:
            continue
        others_target = get_entity_target(g)

        if others_target == ghost_target and g.direction == ghost.direction:
            ghost.path = None
            ghost.algorithm = 'random'
            return

    ghost.algorithm = 'deterministic'
    if ghost.path is None and distance(pacman.position, ghost.position) >= 200:
        r = dfs_find_path(ghost.target, pacman.target)
        ghost.path = r
    elif distance(pacman.position, ghost.position) < 200:
        ghost.path = None
        ghost.goal = pacman.position


def euristic2(ghost, ghosts, pacman):

    if ghost.target is None:
        ghost_default_navigation(ghost, pacman)
        return

    if between_ghosts(pacman, ghosts, ghost):
        ghost_default_navigation(ghost, pacman)
        return

    if one_on_pacman_line(pacman, ghosts, ghost):
        ghost_default_navigation(ghost, pacman)
        return

    if ghost.algorithm == 'cut' and ghost.path is not None:
        return

    ghost_target = get_entity_target(ghost)
    for g in ghosts:
        if g == ghost:
            continue
        others_target = get_entity_target(g)

        if others_target == ghost_target and g.direction == ghost.direction:
            handle_cut(ghost)
            return

    ghost.algorithm = 'deterministic'
    pacman_destination = get_entity_target(pacman)

    if distance(pacman.position, ghost.position) <= 50:
        ghost.path = None
        ghost.goal = pacman.position
    else:
        r = bfs_find_path(ghost.target, pacman_destination)
        ghost.path = r
        ghost.goal = pacman_destination.position


def euristic3(ghost, pacman):

    if ghost.target == None:
        ghost_default_navigation(ghost, pacman)
        return

    if distance(pacman.position, ghost.position) <= 50:
        ghost_default_navigation(ghost, pacman)
        return

    r = dijkstra_find_path(ghost.target, pacman.node)
    ghost.path = r


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



