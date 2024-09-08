import random

import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import *
from pellets import PelletGroup
from map_generator import *
from ghosts import Ghost
from search_algorithms import *
import numpy as np

euristics = ['random', 'deterministic', 'cut']


def between_ghosts(pacman, ghosts, ghost):

    for g in ghosts:
        if g == ghost:
            continue

        if ghost.position.x == g.position.x == pacman.position.x:
            if ghost.position.y <= pacman.position.y <= g.position.y or ghost.position.y >= pacman.position.y >= g.position.y:
                return True
        elif ghost.position.y == g.position.y == pacman.position.y:
            if ghost.position.x <= pacman.position.x <= g.position.x or ghost.position.x >= pacman.position.x >= g.position.x:
                return True
    return False


def only_one_on_line(ghosts, ghost):

    for g in ghosts:
        if g == ghost:
            continue
        if g.position.x == ghost.position.x or g.position.y == ghost.position.y:
            return False

    return True


def distance(vec1, vec2):
    return math.sqrt((vec2.x - vec1.x)**2 + (vec2.y - vec1.y)**2)

class GameController(object):

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.clock = pygame.time.Clock()
        self.path_timer = 0
        self.path_interval = 3


    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):

        self.difficulty = 1
        self.map = generate_map(self.difficulty)
        self.setBackground()
        self.nodes = NodeGroup(self.map)
        self.pacman = Pacman(self.nodes.start_node)
        self.pellets = PelletGroup(self.map)
        self.t = None
        self.tar = None
        p = self.nodes.ghost_node
        self.ghost1 = Ghost(p, algorithm=euristics[0])
        self.ghost2 = Ghost(p, algorithm=euristics[0])
        self.ghost3 = Ghost(p, algorithm=euristics[0])
        self.ghosts = [self.ghost1, self.ghost2, self.ghost3]

        self.fin = None
        self.not_connected = True

    def euristic1(self, ghost):

        ghost.goal = self.pacman.position
        if ghost.target is None: return
        if ghost.path is None and distance(self.pacman.position, ghost.position) >= 200:
            fin = self.pacman.target
            r = dfs_find_path(ghost.target, fin)
            ghost.path = r
        elif distance(self.pacman.position, ghost.position) < 200:
            ghost.path = None


    def euristic2(self, ghost):

        if ghost.target is None:
            return

        if between_ghosts(self.pacman, self.ghosts, ghost):
            ghost.path = None
            ghost.goal = self.pacman.position
            return

        if ghost.position.x == self.pacman.position.x or ghost.position.y == self.pacman.position.y:
            if only_one_on_line(self.ghosts, ghost):
                print(self.path_timer)
                ghost.path = None
                ghost.goal = self.pacman.position
                return

        if ghost.algorithm == 'handling_cut' and ghost.path is not None:
            return

        self.tar = self.get_entity_target(ghost)

        for g in self.ghosts:
            if g == ghost:
                continue
            self.t = self.get_entity_target(g)

            if self.t == self.tar and g.direction == ghost.direction:
                ghost.path = None
                ghost.algorithm = 'cut'
                return

        ghost.algorithm = 'deterministic'
        fin = self.get_entity_target(self.pacman)

        if distance(self.pacman.position, ghost.position) <= 50:
            ghost.path = None
            ghost.goal = self.pacman.position
        else:
            r = bfs_find_path(ghost.target, fin)
            ghost.path = r
            ghost.goal = fin.position


    def euristic3(self, ghost):

        if ghost.target == None:
            return

        if distance(self.pacman.position, ghost.position) <= 20:
            ghost.path = None
            return

        r = dijkstra_find_path(ghost.target, self.pacman.node)
        ghost.path = r


    def get_entity_target(self, entity):

        fin = entity.target
        direction = entity.direction
        if direction != STOP and direction is not None:

            while fin.neighbors[direction] is not None:
                fin = fin.neighbors[direction]

        return fin


    def update(self):

        dt = self.clock.tick(30) / 1000.0
        self.path_timer += dt

        if self.path_timer >= self.path_interval and self.not_connected:

            self.map = np.array([['.' if cell == '=' else cell for cell in row] for row in self.map])
            self.nodes.connectVertically(self.map)
            self.not_connected = False
            for g in self.ghosts:
                g.algorithm = euristics[1]

        #self.euristic1(self.ghost1)
        self.euristic2(self.ghost2)
        self.euristic3(self.ghost3)

        #self.ghost1.update(dt)
        self.ghost2.update(dt)
        self.ghost3.update(dt)

        self.pacman.update(dt)
        self.checkPelletEvents()
        self.checkEvents()
        self.render()

    def recalculatePath(self, g):

        if g.target == None:
            return
        r = None
        fin = self.pacman.node
        if g.algorithm == 'dfs':
            self.euristic1(g)
            #fin = self.pacman.target
            #r = dfs_find_path(g.target, fin)
        elif g.algorithm == 'bfs':

            r = bfs_find_path(g.target, self.fin)
        elif g.algorithm == 'dijkstra':

            r = dijkstra_find_path(g.target, self.pacman.node)

        g.path = r

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.pellets.pelletList.remove(pellet)


    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.nodes.render(self.screen, self.ghost2.path)
        self.pellets.render(self.screen)
        self.pacman.render(self.screen)
        for g in self.ghosts:
            g.render((self.screen))
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()