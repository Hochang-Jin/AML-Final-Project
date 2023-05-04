import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()

font = pygame.font.SysFont('arial', 25)

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 80
SPEED = 40

# default map
MAP  = [[1,0,0,0,0],
        [0,0,0,0,2],
        [0,0,0,0,0]] # 0: nothing, 1: player, 2: goal, 3: wall

# array to map setting
def getPoint(x, y):
    return Point(x*BLOCK_SIZE, y*BLOCK_SIZE)

class GameAI:
    def __init__(self, map=MAP):
        self.map=map
        self.w = BLOCK_SIZE * len(self.map[0])
        self.h = BLOCK_SIZE * len(self.map)
        self.walls=[]
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # map reading
        for i in self.map:
            for j in i:
                if j == 1:
                    x = i.index(j)
                    y = self.map.index(i)
                    self.player = getPoint(x, y)
                elif j == 2:
                    x = i.index(j)
                    y = self.map.index(i)
                    self.goal = getPoint(x,y)
                elif j == 3:
                    x = i.index(j)
                    y = self.map.index(i)
                    self.walls.append(getPoint(x,y))

        self.score = 300
        self.frame_iteration = 0

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self._move(action)  # update the head

        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 1800:
            game_over = True
            reward = -10
            self.score = -300
            return reward, game_over, self.score

        # 4. player reaches goal or not
        if self.player == self.goal:
            reward = 10
            game_over = True
            return reward, game_over, self.score
        else:
            self.score -= 1

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.player
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits wall
        if pt in self.walls:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        # player: Blue
        pygame.draw.rect(self.display, BLUE1, pygame.Rect(self.player.x, self.player.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, BLUE2, pygame.Rect(self.player.x + 4, self.player.y + 4, 72, 72))
        # goal : Red
        pygame.draw.rect(self.display, RED, pygame.Rect(self.goal.x, self.goal.y, BLOCK_SIZE, BLOCK_SIZE))
        # wall : White
        for wall in self.walls:
            pygame.draw.rect(self.display, WHITE, pygame.Rect(wall[0],wall[1], BLOCK_SIZE, BLOCK_SIZE))
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):

       x = self.player.x
       y = self.player.y
       # [up, right, down left]
       if np.array_equal(action, [1, 0, 0, 0]):
           y -= BLOCK_SIZE
       elif np.array_equal(action, [0, 1, 0, 0]):
           x += BLOCK_SIZE
       elif np.array_equal(action, [0, 0, 1, 0]):
           y += BLOCK_SIZE
       else:
           x -= BLOCK_SIZE

       self.player = Point(x, y)