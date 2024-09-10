import pygame
import numpy as np
from utils.pause import Pause
from pygame.locals import *
from entities.pacman import Pacman
from map.pellets import PelletGroup
from map.map_generator import *
from entities.ghosts import Ghost
from entities.behavior import *
from utils.text import *
from utils.sprites import *


class GameController(object):

    def __init__(self):
        pygame.init()
        self.textgroup = TextGroup()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.clock = pygame.time.Clock()
        self.path_timer = 0
        self.path_interval = 5
        self.pause = Pause(True)
        self.level = 1
        self.lives = 5
        self.lifesprites = LifeSprites(self.lives)

    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)


    def restartGame(self):

        self.lives = 5
        self.level = 1
        self.path_timer = 0
        self.pause.paused = True
        self.textgroup.updateLevel(self.level)
        #self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.startGame()

    def resetLevel(self):

        self.pause.paused = True
        self.pacman.reset(self.nodes.start_node)
        self.pacman.counter = 0

        for g in self.ghosts:
            g.reset(self.nodes.ghost_node)
        #self.textgroup.showText(READYTXT)
        self.showEntities()


    def nextLevel(self):

        self.showEntities()
        self.level += 1
        self.path_timer = 0
        self.pause.paused = True
        self.textgroup.updateLevel(self.level)
        self.startGame()


    def startGame(self):

        self.movement = 'automatic' # automatic or manual
        self.map = generate_map(self.level)
        self.setBackground()
        self.mazesprites = MazeSprites(self.map)
        self.background = self.mazesprites.constructBackground(self.background, 16, 16)

        self.nodes = NodeGroup(self.map)
        self.pacman = Pacman(node=self.nodes.start_node, speed=100, movement=self.movement)
        self.pacman.counter = 0
        self.pellets = PelletGroup(self.map)

        self.ghost1 = Ghost(self.nodes.ghost_node, BLUE, speed=90, algorithm='random', id=0)
        self.ghost2 = Ghost(self.nodes.ghost_node, ORANGE, speed=90, algorithm='random', id=2)
        self.ghost3 = Ghost(self.nodes.ghost_node, PINK, speed=90, algorithm='random', id=4)
        self.ghosts = [self.ghost1, self.ghost2, self.ghost3]
        self.pacman.avoid = self.nodes.get_avoid_nodes()
        self.not_connected = True


    def update(self):

        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.path_timer += dt

        if not self.pause.paused:

            if self.path_timer >= self.path_interval and self.not_connected:
                self.map = np.array([['#' if cell == '=' else cell for cell in row] for row in self.map])
                self.nodes.connectVertically(self.map)
                self.not_connected = False
                self.mazesprites = MazeSprites(self.map)
                self.background = self.mazesprites.constructBackground(self.background, 16, 16)
                for g in self.ghosts:
                    g.algorithm = 'deterministic'

            euristic1(self.ghost1, self.ghosts, self.pacman)
            euristic2(self.ghost2, self.ghosts, self.pacman)
            euristic3(self.ghost3, self.pacman)

            self.ghost1.update(dt)
            self.ghost2.update(dt)
            self.ghost3.update(dt)

            self.pacman.update(dt, self.ghosts)
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
                    if not self.pause.paused:
                        self.textgroup.hideText()
                        self.showEntities()
                    else:
                        self.textgroup.showText(PAUSETXT)


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
                if not self.pacman.alive:
                    continue
                self.lives -= 1
                self.lifesprites.removeImage()
                self.pacman.die()
                self.hideEntities()
                if self.lives <= 0:
                    self.textgroup.showText(GAMEOVERTXT)
                    self.pause.setPause(pauseTime=3)
                    self.restartGame()
                else:
                    self.pause.setPause(pauseTime=3)
                    self.resetLevel()


    def render(self):

        self.screen.blit(self.background, (0, 0))
        #self.nodes.render(self.screen, poses=self.pacman.avoid)
        self.pellets.render(self.screen)
        self.pacman.render(self.screen)
        for g in self.ghosts:
            g.render((self.screen))
        self.textgroup.render(self.screen)
        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()