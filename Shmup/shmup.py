#with help of KidsCanCode

import pygame
import random
import os

height = 600
width = 480
fps = 60
inf = 10**9
power_time = 5000

#COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0 , 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#set up assets folder
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "images")
snd_folder = os.path.join(game_folder, "sounds")

#initialize
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')
def draw_text(surf, x, y, text, size):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_shield(surf, x, y, prc):
    if prc < 0:
        prc = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 15
    fill = (prc / 100) * BAR_LENGTH
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = 30*i + x
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_shield_timer(surf, x, y, time_picked, gun_on_top, shield_on_top):
    time_left = power_time - pygame.time.get_ticks() + time_picked
    if time_left > 0:
        BAR_LENGTH = 50
        BAR_HEIGHT = 15
        if gun_on_top:
            y = y + BAR_HEIGHT + 5
            shield_on_top = False
        else:
            shield_on_top = True
        fill = (time_left / power_time) * BAR_LENGTH
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        pygame.draw.rect(surf, YELLOW, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)
        shield_img = pygame.transform.scale(power_images["shield"], (17, 17))
        shield_img.set_colorkey(BLACK)
        shield_rect = shield_img.get_rect()
        shield_rect.centerx = width - 180
        shield_rect.y = y
        screen.blit(shield_img, shield_rect)
    else:
        if shield_on_top:
            shield_on_top = False
    return gun_on_top, shield_on_top

def draw_gun_timer(surf, x, y, time_picked, gun_on_top, shield_on_top):
    time_left = power_time - pygame.time.get_ticks() + time_picked
    if time_left > 0:
        BAR_LENGTH = 50
        BAR_HEIGHT = 15
        if shield_on_top:
            y = y + BAR_HEIGHT + 5
            gun_on_top = False
        else:
            gun_on_top = True
        fill = (time_left / power_time) * BAR_LENGTH
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        pygame.draw.rect(surf, YELLOW, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)
        gun_img = pygame.transform.scale(power_images["gun"], (11, 17))
        gun_img.set_colorkey(BLACK)
        gun_rect = gun_img.get_rect()
        gun_rect.centerx = width - 180
        gun_rect.y = y
        screen.blit(gun_img, gun_rect)
    else:
        if gun_on_top:
            gun_on_top = False
    return gun_on_top, shield_on_top

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, width / 2, height / 4, "Shmup!", 64)
    draw_text(screen, width / 2, height / 2, "Arrows to move, Space to fire", 24)
    draw_text(screen, width / 2, height * 3 / 4, "Press key to begin", 24)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        #self.image.fill(GREEN)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*0.8/2)
        self.rect.centerx = width/2
        self.rect.bottom = height - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shoot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.timer_hidden = pygame.time.get_ticks()
        self.unvalnerable = True
        self.time_shield_picked = pygame.time.get_ticks() - 3000 #-inf
        self.num_bullets = 1
        self.time_gun_picked = -inf

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if self.hidden and pygame.time.get_ticks() - self.timer_hidden > 1000:
            self.hidden = False
            self.rect.centerx = width/2
            self.rect.bottom = height - 10
            self.unvalnerable = True
            self.time_shield_picked = pygame.time.get_ticks() - 3000
        if self.num_bullets >= 2 and pygame.time.get_ticks() - self.time_gun_picked > power_time:
            self.num_bullets -= 1
        if pygame.time.get_ticks() - self.time_shield_picked > power_time:
            self.unvalnerable = False
        if (keystate[pygame.K_d]) or (keystate[pygame.K_RIGHT]):
            self.speedx = 8
        if (keystate[pygame.K_a]) or (keystate[pygame.K_LEFT]):
            self.speedx = -8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > width:
            self.rect.right = width

    def shoot(self):
        now = pygame.time.get_ticks()
        if (now - self.last_shoot > self.shoot_delay) and (not self.hidden):
            if self.num_bullets == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
                self.last_shoot = now
            if self.num_bullets >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
                self.last_shoot = now

    def hide(self):
        self.hidden = True
        self.timer_hidden = pygame.time.get_ticks()
        self.rect.center = (width / 2, height + 200)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*0.9/2)
        self.rect.x = random.randrange(self.rect.width,
         width - self.rect.width - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedx = random.randrange(-2, 2)
        self.speedy = random.randrange(3, 8)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if (self.rect.top > height) or (self.rect.left < -20) or (self.rect.right > width + 20):
            self.rect.x = random.randrange(self.rect.width,
             width - self.rect.width - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedx = random.randrange(-2, 2)
            self.speedy = random.randrange(3, 8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bulllet_img
        #self.image.fill(YELLOW)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y +=self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.frame_rate = 50
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame +=1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun", "heal"])
        self.image = power_images[self.type]
        #self.image.fill(YELLOW)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y +=self.speedy
        if self.rect.top > height:
            self.kill()

#Load sounds
shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, "Laser_1.wav"))
expl_sounds = []
for i in ["Explosion1.wav", "Explosion2.wav"]:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_folder, i)))
player_die_sound = pygame.mixer.Sound(os.path.join(snd_folder, "die_sound.wav"))
pygame.mixer.music.load(os.path.join(snd_folder, "Error Management.wav"))
pygame.mixer.music.set_volume(0.3)

#Load graphics
background = pygame.image.load(os.path.join(img_folder, "starfield.png"))
background_rect = background.get_rect()
background = pygame.transform.scale(background, (height, height))
player_img = pygame.image.load(os.path.join(img_folder, "ship.png")).convert()
player_img_mini = pygame.transform.scale(player_img, (25, 19))
player_img_mini.set_colorkey(BLACK)
bulllet_img = pygame.image.load(os.path.join(img_folder, "laser.png")).convert()
power_images = {}
power_images["shield"] = pygame.image.load(os.path.join(img_folder, "shield.png")).convert()
power_images["gun"] = pygame.image.load(os.path.join(img_folder, "bolt.png")).convert()
heal_img = pygame.image.load(os.path.join(img_folder, "heal.png"))
power_images["heal"] = pygame.transform.scale(heal_img, (30, 30))
meteor_images = []
meteor_list = ["meteorBrown_big1.png", "meteorBrown_big2.png", "meteorBrown_big4.png",
               "meteorBrown_med1.png", "meteorBrown_med3.png", "meteorBrown_small1.png",
               "meteorBrown_small2.png", "meteorBrown_tiny1.png"]
for i in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_folder, i)).convert())
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = "sonicExplosion0{}.png".format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

#Game loop
pygame.mixer.music.play(loops = -1)
running = True
game_over = True

while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range (8):
            newmob()
        score = 0
        gun_on_top = False
        shield_on_top = False

    #controls speed
    clock.tick(fps)
    #input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #update
    all_sprites.update()

    #check if any mob hit the Player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        if not player.unvalnerable:
            player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            player.hide()
            player.lives -= 1
            if player.lives != 0:
                player.shield = 100

    if player.lives == 0 and not death_expl.alive():
        game_over = True

    #check if any bullet hit the mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 75 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.85:
            pow = PowerUp(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    #check if the player hits a PowerUp
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == "shield":
            player.unvalnerable = True
            player.time_shield_picked = pygame.time.get_ticks()
        if hit.type == "heal":
            player.shield += 20
            if player.shield >=100:
                player.shield = 100
        if hit.type == "gun":
            player.time_gun_picked = pygame.time.get_ticks()
            player.num_bullets += 1
    #draw
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    draw_text(screen, width/2, 10, str(score), 20)
    draw_shield(screen, 5, 5, player.shield)
    draw_lives(screen, width - 100, 5, player.lives, player_img_mini)
    gun_on_top, shield_on_top = draw_shield_timer(screen, width - 160, 5,
            player.time_shield_picked, gun_on_top, shield_on_top)
    gun_on_top, shield_on_top = draw_gun_timer(screen, width - 160, 5,
            player.time_gun_picked, gun_on_top, shield_on_top)
    all_sprites.draw(screen)

    #at the very end
    pygame.display.flip()

pygame.quit()
