import random
from pause import Pause
import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import *
from pellets import PelletGroup
from map_generator import *
from ghosts import Ghost
from behavior import *
import numpy as np


class GameController(object):

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.clock = pygame.time.Clock()
        self.path_timer = 0
        self.path_interval = 5
        self.pause = Pause(True)
        self.level = 1
        self.lives = 5

    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)


    def restartGame(self):
        self.lives = 5
        self.level = 1
        self.pause.paused = True
        self.startGame()

    def resetLevel(self):
        self.pause.paused = True
        self.pacman.reset(self.nodes.start_node)
        for g in self.ghosts:
            g.reset(self.nodes.ghost_node)
        self.showEntities()


    def nextLevel(self):
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()


    def startGame(self):

        self.map = generate_map(self.level)
        self.setBackground()
        self.nodes = NodeGroup(self.map)
        self.pacman = Pacman(node=self.nodes.start_node, speed=100)
        self.pellets = PelletGroup(self.map)

        self.ghost1 = Ghost(self.nodes.ghost_node, TEAL, speed=90, algorithm='random')
        self.ghost2 = Ghost(self.nodes.ghost_node, ORANGE, speed=90, algorithm='random')
        self.ghost3 = Ghost(self.nodes.ghost_node, PINK, speed=90, algorithm='random')
        self.ghosts = [self.ghost1, self.ghost2, self.ghost3]
        self.not_connected = True


    def update(self):

        dt = self.clock.tick(30) / 1000.0
        self.path_timer += dt

        if not self.pause.paused:

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
            self.checkGhostEvents()

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()

        self.checkEvents()
        self.render()


    def showEntities(self):
        self.pacman.visible = True
        for g in self.ghosts:
            g.visible = True

    def hideEntities(self):
        self.pacman.visible = False
        for g in self.ghosts:
            g.visible = False


    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.pacman.alive:
                    self.pause.setPause(playerPaused=True)


    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.pellets.pelletList.remove(pellet)

        if self.pellets.isEmpty():
            self.hideEntities()
            self.pause.setPause(pauseTime=3)
            self.nextLevel()


    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideCheck(ghost):
                    return
                    if self.pacman.alive:
                        self.lives -= 1
                        self.pacman.die()
                        self.pacman.direction = STOP
                        self.hideEntities()
                        if self.lives <= 0:
                            self.pause.setPause(pauseTime=3)
                            self.restartGame()
                        else:
                            self.pause.setPause(pauseTime=3)
                            self.resetLevel()


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