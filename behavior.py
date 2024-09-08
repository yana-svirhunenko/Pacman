
import pygame
from pygame.locals import *
from nodes import *
from search_algorithms import *
import numpy as np


def between_ghosts(pacman, ghosts, ghost):

    for g in ghosts:
        if g == ghost:
            continue

        if abs(ghost.position.x - g.position.x) <= 0.01 and abs(ghost.position.x - pacman.position.x) <= 0.01:
            if ghost.position.y <= pacman.position.y <= g.position.y or ghost.position.y >= pacman.position.y >= g.position.y:
                return True
        elif abs(ghost.position.y - g.position.y) <= 0.01 and abs(ghost.position.y - pacman.position.y) <= 0.01:
            if ghost.position.x <= pacman.position.x <= g.position.x or ghost.position.x >= pacman.position.x >= g.position.x:
                return True
    return False


def only_one_on_line(ghosts, ghost):

    for g in ghosts:
        if g == ghost:
            continue
        if abs(g.position.x - ghost.position.x) <= 0.01 or abs(g.position.y - ghost.position.y) <= 0.01:
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


def euristic1(ghost, ghosts, pacman):

    ghost.goal = pacman.position
    if ghost.target is None:
        return

    if between_ghosts(pacman, ghosts, ghost):
        ghost.path = None
        ghost.goal = pacman.position
        return

    if abs(ghost.position.x - pacman.position.x) <= 0.01 or abs(ghost.position.y - pacman.position.y) <= 0.01:
        if only_one_on_line(ghosts, ghost):
            ghost.path = None
            ghost.goal = pacman.position
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


def euristic2(ghost, ghosts, pacman):

    if ghost.target is None:
        return

    if between_ghosts(pacman, ghosts, ghost):
        ghost.path = None
        ghost.goal = pacman.position
        return

    if abs(ghost.position.x - pacman.position.x) <= 0.01 or abs(ghost.position.y - pacman.position.y) <= 0.01:
        if only_one_on_line(ghosts, ghost):
            ghost.path = None
            ghost.goal = pacman.position
            return

    if ghost.algorithm == 'handling_cut' and ghost.path is not None:
        return

    ghost_target = get_entity_target(ghost)

    for g in ghosts:
        if g == ghost:
            continue
        others_target = get_entity_target(g)

        if others_target == ghost_target and g.direction == ghost.direction:
            ghost.path = None
            ghost.algorithm = 'cut'
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
        return

    if distance(pacman.position, ghost.position) <= 20:
        ghost.path = None
        return

    r = dijkstra_find_path(ghost.target, pacman.node)
    ghost.path = r

