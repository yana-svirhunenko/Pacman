import random
from pauser import Pause
import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import *
from pellets import PelletGroup
from map_generator import *
from ghosts import Ghost
from search_algorithms import *
from behavior import *
import numpy as np


class GameController(object):

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.clock = pygame.time.Clock()
        self.path_timer = 0
        self.path_interval = 10
        self.pause = Pause(True)


    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):

        self.difficulty = 1
        self.map = generate_map(self.difficulty)
        self.setBackground()
        self.nodes = NodeGroup(self.map)
        self.pacman = Pacman(node=self.nodes.start_node, speed=100)
        self.pellets = PelletGroup(self.map)

        p = self.nodes.ghost_node
        self.ghost1 = Ghost(p, TEAL, speed=90, algorithm='random')
        self.ghost2 = Ghost(p, ORANGE, speed=90, algorithm='random')
        self.ghost3 = Ghost(p, PINK, speed=90, algorithm='random')
        self.ghosts = [self.ghost1, self.ghost2, self.ghost3]

        self.not_connected = True


    def update(self):

        dt = self.clock.tick(30) / 1000.0
        self.path_timer += dt

        if not self.pause.paused:
            self.pacman.update(dt)
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()
        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()

        if self.path_timer >= self.path_interval and self.not_connected:

            self.map = np.array([['.' if cell == '=' else cell for cell in row] for row in self.map])
            self.nodes.connectVertically(self.map)
            self.not_connected = False
            for g in self.ghosts:
                g.algorithm = 'deterministic'

        euristic1(self.ghost1, self.ghosts, self.pacman)
        euristic2(self.ghost2, self.ghosts, self.pacman)
        euristic3(self.ghost3, self.pacman)

        self.ghost1.update(dt)
        self.ghost2.update(dt)
        self.ghost3.update(dt)

        self.pacman.update(dt)
        self.checkPelletEvents()
        self.checkEvents()
        self.render()


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