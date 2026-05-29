import pygame
import random
from src.settings import WIDTH, HEIGHT

class Projectile:
    def __init__(self, x, y, dx, dy, is_enemy):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.dx, self.dy = dx, dy
        self.speed = 7
        self.is_enemy = is_enemy

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.hp = 100
        self.speed = 2
        self.facing = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.state = "ROAMING"
        self.roam_timer = random.randint(30, 90)
        self.attack_timer = random.randint(120, 240)
        self.stun_timer = 0
        self.knockback_dir = (0, 0)
        self.flash_timer = 0
        self.screen_bounds = pygame.Rect(0, 0, WIDTH, HEIGHT) # Границы для коллизий

    def update(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        if self.state == "STUNNED":
            self.rect.x += self.knockback_dir[0] * 4
            self.rect.y += self.knockback_dir[1] * 4
            self.rect.clamp_ip(self.screen_bounds) # Фикс вылета за границы при стане
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
                if self.facing in dirs: dirs.remove(self.facing)
                self.facing = random.choice(dirs)
                self.roam_timer = random.randint(30, 90)
                
            if self.attack_timer <= 30:
                self.state = "ATTACKING"

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 5
        self.max_hp = 5
        self.current_hp = 5
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
            if self.current_hp < 0: self.current_hp = 0
            
            if self.current_hp > 0:
                self.state = "STUNNED"
                self.stun_timer = 15
                self.invul_timer = 60
                dx = self.rect.centerx - source_x
                dy = self.rect.centery - source_y
                k_dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
                k_dy = 1 if dy > 0 else (-1 if dy < 0 else 0)
                self.knockback_dir = (k_dx, 0) if abs(dx) > abs(dy) else (0, k_dy)
