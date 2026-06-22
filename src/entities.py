import pygame
import random
import math
from src.settings import (
    WIDTH, HEIGHT, ENEMY_SIZE, ENEMY_SPEED, ENEMY_HP,
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_MAX_HP,
    PROJECTILE_SIZE, PROJECTILE_SPEED,
    COLOR_ENEMY_DEFAULT, COLOR_ENEMY_SHOOTER, COLOR_ENEMY_DRILLER,
    SHOOTER_HP
)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, is_enemy):
        super().__init__()
        self.rect = pygame.Rect(x, y, PROJECTILE_SIZE, PROJECTILE_SIZE)
        self.exact_x = float(x)
        self.exact_y = float(y)
        self.dx = dx
        self.dy = dy
        self.speed = PROJECTILE_SPEED
        self.is_enemy = is_enemy

    def update(self):
        self.exact_x += self.dx * self.speed
        self.exact_y += self.dy * self.speed
        self.rect.x = int(self.exact_x)
        self.rect.y = int(self.exact_y)
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
        
        self.color = COLOR_ENEMY_DEFAULT
        self.is_underground = False

    def update(self, player, projectiles_group=None):
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
            self.attack(projectiles_group)

    def attack(self, projectiles_group):
        proj = Projectile(self.rect.centerx, self.rect.centery, self.facing[0], self.facing[1], True)
        projectiles_group.add(proj)

class Shooter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = SHOOTER_HP
        self.color = COLOR_ENEMY_SHOOTER

    def attack(self, projectiles_group):
        for angle_deg in range(0, 360, 45):
            angle_rad = math.radians(angle_deg)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)
            proj = Projectile(self.rect.centerx, self.rect.centery, dx, dy, True)
            projectiles_group.add(proj)

class Driller(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = COLOR_ENEMY_DRILLER
        self.speed = ENEMY_SPEED + 2
        self.state = "SURFACE"
        self.action_timer = random.randint(60, 120)
        
    def update(self, player, projectiles_group=None):
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        if self.state == "STUNNED":
            self.rect.x += self.knockback_dir[0] * 4
            self.rect.y += self.knockback_dir[1] * 4
            self.rect.clamp_ip(self.screen_bounds)
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = "SURFACE"
                self.is_underground = False
                self.action_timer = random.randint(60, 120)
                
        elif self.state == "SURFACE":
            self.is_underground = False
            self.rect.x += self.facing[0] * self.speed
            self.rect.y += self.facing[1] * self.speed
            self.action_timer -= 1
            if self.action_timer <= 0 or not self.screen_bounds.contains(self.rect):
                self.rect.clamp_ip(self.screen_bounds)
                self.state = "DIGGING"
                self.action_timer = 30
                
        elif self.state == "DIGGING":
            self.action_timer -= 1
            if self.action_timer <= 0:
                self.state = "HIDDEN"
                self.is_underground = True
                self.action_timer = 60
                
        elif self.state == "HIDDEN":
            self.action_timer -= 1
            if self.action_timer <= 0:
                dist = 150
                is_horizontal = random.choice([True, False])
                
                if is_horizontal:
                    self.rect.centerx = player.rect.centerx
                    self.rect.centery = player.rect.centery + random.choice([-dist, dist])
                else:
                    self.rect.centerx = player.rect.centerx + random.choice([-dist, dist])
                    self.rect.centery = player.rect.centery
                    
                self.rect.clamp_ip(self.screen_bounds)
                
                self.state = "EMERGING"
                self.action_timer = 30
                
        elif self.state == "EMERGING":
            self.action_timer -= 1
            if self.action_timer <= 0:
                self.state = "SURFACE"
                self.is_underground = False
                self.action_timer = random.randint(60, 120)
                
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                
                if abs(dx) > abs(dy):
                    self.facing = (1 if dx > 0 else -1, 0)
                else:
                    self.facing = (0, 1 if dy > 0 else -1)

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
        self.attack_cooldown = 0
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
