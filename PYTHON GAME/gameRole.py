import pygame, random

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, speed, direction=1, color=(255,255,255)):
        super().__init__()
        self.image = pygame.Surface((6,14), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0,0,6,14))
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed * direction

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, img, rects, pos):
        super().__init__()
        self.images = [img.subsurface(r).convert_alpha() for r in rects]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 8

        self.bullets = pygame.sprite.Group()
        self.frame = 0

        self.max_hp = 100
        self.hp = 100

        self.rapid = 0
        self.multi = 0
        self.shield = 0

    def shoot(self):
        count = 3 if self.multi > 0 else 1
        spread = 22
        for i in range(count):
            offset = (i - (count-1)/2) * spread
            self.bullets.add(
                Bullet((self.rect.centerx + offset, self.rect.top),
                       14, 1, (80,255,255))
            )

    def update(self):
        self.frame = (self.frame + 1) % len(self.images)
        self.image = self.images[self.frame]

        self.rapid = max(0, self.rapid-1)
        self.multi = max(0, self.multi-1)
        self.shield = max(0, self.shield-1)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, elite=False):
        super().__init__()
        self.image = pygame.Surface((40,30))
        self.image.fill((255,80,80) if elite else (255,160,80))
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 3 if not elite else 5
        self.hp = 2 if elite else 1
        self.cooldown = random.randint(50,90)

    def update(self, bullets):
        self.rect.y += self.speed
        self.cooldown -= 1

        if self.cooldown <= 0:
            bullets.add(
                Bullet(self.rect.midbottom, 6, -1, (255,80,80))
            )
            self.cooldown = random.randint(60,100)

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((200,120))
        self.image.fill((180,60,60))
        self.rect = self.image.get_rect(center=(240,-150))
        self.hp = 4000
        self.timer = 0

    def update(self, bullets):
        if self.rect.y < 80:
            self.rect.y += 2
            return

        self.timer += 1
        if self.timer % 25 == 0:
            for _ in range(6):
                bullets.add(
                    Bullet(self.rect.center, 6, -1, (255,120,120))
                )


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, ptype, pos):
        super().__init__()
        self.type = ptype  # rapid, multi, shield, heal
        self.image = pygame.Surface((32,32), pygame.SRCALPHA)
        colors = [(255,80,80),(80,80,255),(80,255,120),(120,255,120)]
        pygame.draw.circle(self.image, colors[ptype], (16,16), 16)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

