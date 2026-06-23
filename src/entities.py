import pygame
import random
import math
from src.settings import (
    WIDTH, HEIGHT, ENEMY_SIZE, ENEMY_SPEED, ENEMY_HP,
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_MAX_HP,
    PROJECTILE_SIZE, PROJECTILE_SPEED, WALL_SIZE
)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        if image:
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            for i in range(0, w, WALL_SIZE):
                for j in range(0, h, WALL_SIZE):
                    self.image.blit(image, (i, j))
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill((100, 100, 100))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, is_enemy, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.exact_x = float(x)
        self.exact_y = float(y)
        self.dx = dx
        self.dy = dy
        self.speed = PROJECTILE_SPEED
        self.is_enemy = is_enemy

    def update(self):
        self.exact_x += self.dx * self.speed
        self.exact_y += self.dy * self.speed
        self.rect.centerx = int(self.exact_x)
        self.rect.centery = int(self.exact_y)
        if not pygame.display.get_surface().get_rect().colliderect(self.rect):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, assets):
        super().__init__()
        self.assets = assets
        self.image = self.assets['enemy_down']
        self.rect = self.image.get_rect(topleft=(x, y))
        
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
        self.is_underground = False

    def _update_image(self):
        if self.facing == (0, 1): self.image = self.assets['enemy_down']
        elif self.facing == (0, -1): self.image = self.assets['enemy_up']
        elif self.facing == (-1, 0): self.image = self.assets['enemy_left']
        elif self.facing == (1, 0): self.image = self.assets['enemy_right']

    def update(self, player, projectiles_group=None, walls_group=None):
        self._update_image()
        
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        if self.state == "STUNNED":
            self.rect.x += self.knockback_dir[0] * 4
            if walls_group and pygame.sprite.spritecollideany(self, walls_group):
                self.rect.x -= self.knockback_dir[0] * 4
                
            self.rect.y += self.knockback_dir[1] * 4
            if walls_group and pygame.sprite.spritecollideany(self, walls_group):
                self.rect.y -= self.knockback_dir[1] * 4
                
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = "ROAMING"
                
        elif self.state == "ATTACKING":
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.state = "ROAMING"
                self.attack_timer = random.randint(120, 240)
                
        elif self.state == "ROAMING":
            old_x, old_y = self.rect.x, self.rect.y
            self.rect.x += self.facing[0] * self.speed
            self.rect.y += self.facing[1] * self.speed
            
            collided = False
            if not self.screen_bounds.contains(self.rect): collided = True
            if walls_group and pygame.sprite.spritecollideany(self, walls_group): collided = True
                
            if collided:
                self.rect.x, self.rect.y = old_x, old_y
                dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                if self.facing in dirs: dirs.remove(self.facing)
                self.facing = random.choice(dirs)
                self.roam_timer = random.randint(30, 90)
            
            self.roam_timer -= 1
            self.attack_timer -= 1
            
            if self.roam_timer <= 0:
                dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                if self.facing in dirs: dirs.remove(self.facing)
                self.facing = random.choice(dirs)
                self.roam_timer = random.randint(30, 90)
                
            if self.attack_timer <= 30:
                self.state = "ATTACKING"

        if self.state == "ATTACKING" and self.attack_timer == 30 and projectiles_group is not None:
            self.attack(projectiles_group)

    def attack(self, projectiles_group):
        proj = Projectile(self.rect.centerx, self.rect.centery, self.facing[0], self.facing[1], True, self.assets['proj_enemy'])
        projectiles_group.add(proj)

class Shooter(Enemy):
    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)
        self.hp = ENEMY_HP - 1    

    def _update_image(self):
        if self.facing == (0, 1): self.image = self.assets['shooter_down']
        elif self.facing == (0, -1): self.image = self.assets['shooter_up']
        elif self.facing == (-1, 0): self.image = self.assets['shooter_left']
        elif self.facing == (1, 0): self.image = self.assets['shooter_right']

    def attack(self, projectiles_group):
        for angle_deg in range(0, 360, 45):
            angle_rad = math.radians(angle_deg)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)
            proj = Projectile(self.rect.centerx, self.rect.centery, dx, dy, True, self.assets['proj_enemy'])
            projectiles_group.add(proj)

class Driller(Enemy):
    def __init__(self, x, y, assets):
        super().__init__(x, y, assets)
        self.state = "SURFACE"
        self.action_timer = random.randint(60, 120)

    def _update_image(self):
        if self.state in ("DIGGING", "EMERGING"):
            self.image = self.assets['driller_dig']
        else:
            self.image = self.assets['driller']
        
    def update(self, player, projectiles_group=None, walls_group=None):
        self._update_image()
        if self.flash_timer > 0: self.flash_timer -= 1
            
        if self.state == "STUNNED":
            self.rect.x += self.knockback_dir[0] * 4
            if walls_group and pygame.sprite.spritecollideany(self, walls_group): self.rect.x -= self.knockback_dir[0] * 4
            self.rect.y += self.knockback_dir[1] * 4
            if walls_group and pygame.sprite.spritecollideany(self, walls_group): self.rect.y -= self.knockback_dir[1] * 4
                
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = "SURFACE"
                self.is_underground = False
                self.action_timer = random.randint(60, 120)
                
        elif self.state == "SURFACE":
            self.is_underground = False
            old_x, old_y = self.rect.x, self.rect.y
            self.rect.x += self.facing[0] * self.speed
            self.rect.y += self.facing[1] * self.speed
            
            if walls_group and pygame.sprite.spritecollideany(self, walls_group):
                self.rect.x, self.rect.y = old_x, old_y
                
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
                    
                safe_bounds = pygame.Rect(WALL_SIZE, WALL_SIZE, WIDTH - WALL_SIZE*2, HEIGHT - WALL_SIZE*2)
                self.rect.clamp_ip(safe_bounds)
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
                if abs(dx) > abs(dy): self.facing = (1 if dx > 0 else -1, 0)
                else: self.facing = (0, 1 if dy > 0 else -1)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, assets):
        super().__init__()
        self.assets = assets
        self.image = self.assets['player_down'][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        
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
        
        self.is_moving = False
        self.anim_timer = 0
        self.anim_frame = 0

    def update_image(self):
        if self.state == "ATTACKING":
            if self.facing == (0, 1):
                self.image = self.assets['player_attack_down']
            elif self.facing == (0, -1):
                self.image = self.assets['player_attack_up']
            elif self.facing == (-1, 0):
                self.image = self.assets['player_attack_left']
            elif self.facing == (1, 0):
                self.image = self.assets['player_attack_right']
        else:
            if self.is_moving:
                self.anim_timer += 1
                if self.anim_timer >= 10:
                    self.anim_timer = 0
                    self.anim_frame = 1 - self.anim_frame
            else:
                self.anim_frame = 0
                
            if self.facing == (0, 1):
                self.image = self.assets['player_down'][self.anim_frame]
            elif self.facing == (0, -1):
                self.image = self.assets['player_up'][self.anim_frame]
            elif self.facing == (-1, 0):
                self.image = self.assets['player_left'][self.anim_frame]
            elif self.facing == (1, 0):
                self.image = self.assets['player_right'][self.anim_frame]

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
