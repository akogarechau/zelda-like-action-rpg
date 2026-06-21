import pygame
import random
from src.settings import (
    WIDTH, HEIGHT, ENEMY_SIZE, ENEMY_SPEED, ENEMY_HP,
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_MAX_HP,
    PROJECTILE_SIZE, PROJECTILE_SPEED
)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, is_enemy):
        super().__init__()
        self.rect = pygame.Rect(x, y, PROJECTILE_SIZE, PROJECTILE_SIZE)
        self.dx = dx
        self.dy = dy
        self.speed = PROJECTILE_SPEED
        self.is_enemy = is_enemy

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        if not pygame.display.get_surface().get_rect().colliderect(self.rect):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.hp = ENEMY_HP
        self.speed = ENEMY_SPEED
        self.facing = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.state = "ROAMING"
        self.roam_timer = random.randint(30, 90)
        self.attack_timer = random.randint(120, 240)
        self.stun_timer = 0
        self.knockback_dir = (0, 0)
        self.flash_timer = 0
        self.screen_bounds = pygame.Rect(0, 0, WIDTH, HEIGHT)

    def update(self, projectiles_group=None):
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        if self.state == "STUNNED":
            self.rect.x += self.knockback_dir[0] * 4
            self.rect.y += self.knockback_dir[1] * 4
            self.rect.clamp_ip(self.screen_bounds)
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = "ROAMING"
                
        elif self.state == "ATTACKING":
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.state = "ROAMING"
                self.attack_timer = random.randint(120, 240)
                
        elif self.state == "ROAMING":
            self.rect.x += self.facing[0] * self.speed
            self.rect.y += self.facing[1] * self.speed
            self.roam_timer -= 1
            self.attack_timer -= 1
            
            if self.roam_timer <= 0 or not self.screen_bounds.contains(self.rect):
                self.rect.clamp_ip(self.screen_bounds)
                dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                if self.facing in dirs:
                    dirs.remove(self.facing)
                self.facing = random.choice(dirs)
                self.roam_timer = random.randint(30, 90)
                
            if self.attack_timer <= 30:
                self.state = "ATTACKING"

        if self.state == "ATTACKING" and self.attack_timer == 30 and projectiles_group is not None:
            proj = Projectile(self.rect.centerx, self.rect.centery, self.facing[0], self.facing[1], True)
            projectiles_group.add(proj)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.max_hp = PLAYER_MAX_HP
        self.current_hp = PLAYER_MAX_HP
        self.state = "IDLE"
        self.facing = (0, 1)
        self.invul_timer = 0
        self.stun_timer = 0
        self.attack_timer = 0
        self.knockback_dir = (0, 0)
        self.sword_rect = None
        self.death_angle = 0
        self.death_alpha = 255

    def take_damage(self, damage, source_x, source_y):
        if self.invul_timer == 0 and self.state != "STUNNED" and self.current_hp > 0:
            self.current_hp -= damage
            if self.current_hp < 0:
                self.current_hp = 0
            
            if self.current_hp > 0:
                self.state = "STUNNED"
                self.stun_timer = 15
                self.invul_timer = 60
                dx = self.rect.centerx - source_x
                dy = self.rect.centery - source_y
                k_dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
                k_dy = 1 if dy > 0 else (-1 if dy < 0 else 0)
                self.knockback_dir = (k_dx, 0) if abs(dx) > abs(dy) else (0, k_dy)
