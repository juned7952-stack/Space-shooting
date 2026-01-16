import pygame
import random

class Star:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.w)
        self.y = random.randint(0, self.h)
        self.speed = random.randint(2, 7)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > self.h:
            self.reset()
            self.y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, (120, 200, 255),
                           (self.x, self.y), self.size)


class Starfield:
    def __init__(self, w, h, count=120):
        self.stars = [Star(w, h) for _ in range(count)]

    def update(self):
        for s in self.stars:
            s.update()

    def draw(self, screen):
        screen.fill((5, 5, 20))
        for s in self.stars:
            s.draw(screen)
