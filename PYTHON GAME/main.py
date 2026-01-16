import pygame, random, os, asyncio
from sys import exit
from gameRole import *
from background import Starfield

pygame.init()
screen = pygame.display.set_mode((480,800))
pygame.display.set_caption("HARDCORE ARCADE SHOOTER")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 64)

# ---------- HIGH SCORE ----------
HS_FILE = "highscore.txt"
if not os.path.exists(HS_FILE):
    with open(HS_FILE, "w") as f:
        f.write("0")

def load_hs():
    with open(HS_FILE, "r") as f:
        return int(f.read())

def save_hs(score):
    hs = load_hs()
    if score > hs:
        with open(HS_FILE, "w") as f:
            f.write(str(score))

high_score = load_hs()

# ---------- ASSETS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sheet = pygame.image.load(
    os.path.join(BASE_DIR, "resources", "image", "shoot.png")
).convert_alpha()

player_rects = [
    pygame.Rect(0,99,102,126),
    pygame.Rect(165,360,102,126)
]

# ---------- RESET ----------
def reset_game():
    return (
        Player(sheet, player_rects, (190,600)),
        pygame.sprite.Group(),
        pygame.sprite.Group(),
        pygame.sprite.Group(),
        pygame.sprite.Group(),
        0, 0, 0, False
    )

# ---------- TOUCH ZONES ----------
LEFT = pygame.Rect(0, 600, 160, 200)
RIGHT = pygame.Rect(320, 600, 160, 200)
UP = pygame.Rect(0, 500, 160, 100)
DOWN = pygame.Rect(0, 700, 160, 100)
FIRE = pygame.Rect(160, 650, 160, 150)
PAUSE_BTN = pygame.Rect(420, 10, 50, 40)

GAME_PLAYING = 0
GAME_PAUSED = 1
GAME_OVER = 2

# ---------- ASYNC MAIN LOOP ----------
async def main():
    global high_score

    player, enemies, enemy_bullets, powerups, boss_group, score, spawn_timer, shoot_timer, boss_spawned = reset_game()
    stars = Starfield(480,800)
    game_state = GAME_PLAYING

    while True:
        clock.tick(60)
        dx = dy = 0
        firing = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_hs(score)
                pygame.quit()
                exit()

            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                game_state = GAME_PAUSED if game_state == GAME_PLAYING else GAME_PLAYING

            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if PAUSE_BTN.collidepoint(pos) and game_state == GAME_PLAYING:
                    game_state = GAME_PAUSED

                if game_state == GAME_OVER:
                    save_hs(score)
                    high_score = load_hs()
                    player, enemies, enemy_bullets, powerups, boss_group, score, spawn_timer, shoot_timer, boss_spawned = reset_game()
                    game_state = GAME_PLAYING

        keys = pygame.key.get_pressed()
        dx += (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy += (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

        mouse = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        if mouse[0]:
            if LEFT.collidepoint(pos): dx -= 1
            if RIGHT.collidepoint(pos): dx += 1
            if UP.collidepoint(pos): dy -= 1
            if DOWN.collidepoint(pos): dy += 1
            if FIRE.collidepoint(pos): firing = True

        # ---------- GAMEPLAY ----------
        if game_state == GAME_PLAYING:
            player.rect.x += dx * player.speed
            player.rect.y += dy * player.speed
            player.rect.clamp_ip(screen.get_rect())

            shoot_timer += 1
            fire_rate = 5 if player.rapid > 0 else 10
            if firing or shoot_timer >= fire_rate:
                shoot_timer = 0
                player.shoot()

            spawn_timer += 1
            if spawn_timer > max(20, 60 - score//2000):
                spawn_timer = 0
                enemies.add(Enemy((random.randint(0,440), -40), random.random() < 0.25))

            if score >= 100000 and not boss_spawned:
                boss_group.add(Boss())
                boss_spawned = True

            stars.update()
            enemies.update(enemy_bullets)
            enemy_bullets.update()
            powerups.update()
            boss_group.update(enemy_bullets)
            player.update()
            player.bullets.update()

            for e in enemies:
                if pygame.sprite.spritecollide(e, player.bullets, True):
                    e.hp -= 1
                    if e.hp <= 0:
                        e.kill()
                        score += 200
                        if random.random() < 0.3:
                            powerups.add(PowerUp(random.randint(0,3), e.rect.center))

            if pygame.sprite.spritecollideany(player, enemy_bullets) and player.shield <= 0:
                player.hp -= 10

            for p in pygame.sprite.spritecollide(player, powerups, True):
                if p.type == 0: player.rapid = 600
                elif p.type == 1: player.multi = 600
                elif p.type == 2: player.shield = 600
                elif p.type == 3: player.hp = min(100, player.hp + 30)

            if player.hp <= 0:
                save_hs(score)
                high_score = load_hs()
                game_state = GAME_OVER

        # ---------- DRAW ----------
        stars.draw(screen)
        enemies.draw(screen)
        enemy_bullets.draw(screen)
        powerups.draw(screen)
        boss_group.draw(screen)
        player.bullets.draw(screen)
        screen.blit(player.image, player.rect)

        pygame.draw.rect(screen, (255,60,60), (10,10,200,12))
        pygame.draw.rect(screen, (60,255,120),
                         (10,10,200*(player.hp/player.max_hp),12))

        screen.blit(font.render(f"SCORE: {score}", True, (255,255,255)), (10,30))
        screen.blit(font.render(f"HS: {high_score}", True, (255,215,0)), (10,55))

        pygame.draw.rect(screen, (80,80,80), PAUSE_BTN)
        screen.blit(font.render("II", True, (255,255,255)), (435,15))

        if game_state == GAME_PAUSED:
            overlay = pygame.Surface((480,800))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            screen.blit(overlay,(0,0))
            screen.blit(big_font.render("PAUSED", True, (255,255,255)), (150,320))

        if game_state == GAME_OVER:
            overlay = pygame.Surface((480,800))
            overlay.set_alpha(200)
            overlay.fill((0,0,0))
            screen.blit(overlay,(0,0))
            screen.blit(big_font.render("GAME OVER", True, (255,80,80)), (90,320))
            screen.blit(font.render("Tap to Restart", True, (255,255,255)), (150,390))

        pygame.display.flip()

        # 🔥 IMPORTANT FOR BROWSER
        await asyncio.sleep(0)

# ---------- RUN ----------
asyncio.run(main())
