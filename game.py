import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zelda-like Action RPG")
clock = pygame.time.Clock()

full_heart_img = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.rect(full_heart_img, (255, 50, 50), (0, 0, 20, 20))

half_heart_img = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.rect(half_heart_img, (255, 50, 50), (0, 0, 10, 20))


rooms_bg = {
    (0, 0): (40, 40, 50), (1, 0): (70, 40, 40),
    (0, 1): (40, 70, 40), (1, 1): (70, 70, 40)
}
current_room = (0, 0)
game_state = "PLAYING"

trans_prog = 0.0
trans_speed = 0.03
trans_dir, next_room = (0, 0), (0, 0)
trans_start_pos, trans_target_pos = (0, 0), (0, 0)

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
        self.hp = 2
        self.speed = 2
        self.facing = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.state = "ROAMING"
        self.roam_timer = random.randint(30, 90)
        self.attack_timer = random.randint(120, 240)
        self.stun_timer = 0
        self.knockback_dir = (0, 0)

    def update(self):
        if self.state == "STUNNED":
            self.rect.x += self.knockback_dir[0] * 4
            self.rect.y += self.knockback_dir[1] * 4
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
            if self.roam_timer <= 0 or not screen.get_rect().contains(self.rect):
                self.rect.clamp_ip(screen.get_rect())
                dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                if self.facing in dirs: dirs.remove(self.facing)
                self.facing = random.choice(dirs)
                self.roam_timer = random.randint(30, 90)
            if self.attack_timer <= 30:
                self.state = "ATTACKING"

room_enemies = {
    (0, 0): [Enemy(300, 200)], (1, 0): [Enemy(400, 300), Enemy(200, 400)],
    (0, 1): [Enemy(500, 200)], (1, 1): [Enemy(350, 250), Enemy(600, 400)]
}
room_projectiles = {(0,0):[], (1,0):[], (0,1):[], (1,1):[]}

player_rect = pygame.Rect(400, 300, 40, 40)
player_speed = 5
active_keys = []
movement_map = {
    pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0)
}

max_hp = 6
current_hp = 5
player_state = "IDLE"
player_facing = (0, 1)
invul_timer, stun_timer, attack_timer = 0, 0, 0
knockback_dir = (0, 0)
sword_rect = None

def take_damage(damage, source_x, source_y):
    global current_hp, player_state, stun_timer, invul_timer, knockback_dir
    if invul_timer == 0 and player_state != "STUNNED":
        current_hp -= damage
        if current_hp < 0: current_hp = 0
        
        player_state = "STUNNED"
        stun_timer = 15
        invul_timer = 60
        dx = player_rect.centerx - source_x
        dy = player_rect.centery - source_y
        k_dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
        k_dy = 1 if dy > 0 else (-1 if dy < 0 else 0)
        knockback_dir = (k_dx, 0) if abs(dx) > abs(dy) else (0, k_dy)

def start_transition(dx, dy, target_x, target_y):
    global game_state, trans_prog, trans_dir, next_room, trans_start_pos, trans_target_pos
    game_state = "TRANSITION"
    trans_prog = 0.0
    trans_dir = (dx, dy)
    next_room = (current_room[0] + dx, current_room[1] + dy)
    trans_start_pos = (player_rect.x, player_rect.y)
    trans_target_pos = (target_x, target_y)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in movement_map:
                if event.key in active_keys: active_keys.remove(event.key)
                active_keys.append(event.key)
            elif event.key == pygame.K_SPACE and player_state == "IDLE":
                player_state = "ATTACKING"
                attack_timer = 15
                sword_rect = pygame.Rect(0, 0, 40, 40)
                sword_rect.center = (player_rect.centerx + player_facing[0]*40, player_rect.centery + player_facing[1]*40)
                if current_hp == max_hp:
                    beam = Projectile(player_rect.centerx, player_rect.centery, player_facing[0], player_facing[1], is_enemy=False)
                    room_projectiles[current_room].append(beam)
        elif event.type == pygame.KEYUP:
            if event.key in active_keys: active_keys.remove(event.key)

    if game_state == "PLAYING":
        if invul_timer > 0: invul_timer -= 1
        
        if player_state == "STUNNED":
            player_rect.x += knockback_dir[0] * 8
            player_rect.y += knockback_dir[1] * 8
            stun_timer -= 1
            if stun_timer <= 0: player_state = "IDLE"
        elif player_state == "ATTACKING":
            attack_timer -= 1
            if attack_timer <= 0:
                player_state = "IDLE"
                sword_rect = None
        elif player_state == "IDLE":
            if active_keys:
                last_key = active_keys[-1]
                dx, dy = movement_map[last_key]
                player_facing = (dx, dy)
                cancel_movement = False
                for key in active_keys:
                    kx, ky = movement_map[key]
                    if dx == -kx and dy == -ky: cancel_movement = True; break
                if not cancel_movement:
                    player_rect.x += dx * player_speed
                    player_rect.y += dy * player_speed

        offset = 10
        if player_rect.left < 0 and current_room[0] > 0:
            start_transition(-1, 0, WIDTH - player_rect.width - offset, player_rect.y)
        elif player_rect.right > WIDTH and current_room[0] < 1:
            start_transition(1, 0, offset, player_rect.y)
        elif player_rect.top < 0 and current_room[1] > 0:
            start_transition(0, -1, player_rect.x, HEIGHT - player_rect.height - offset)
        elif player_rect.bottom > HEIGHT and current_room[1] < 1:
            start_transition(0, 1, player_rect.x, offset)
            
        player_rect.left = max(0 if current_room[0] == 0 else -100, player_rect.left)
        player_rect.right = min(WIDTH if current_room[0] == 1 else WIDTH + 100, player_rect.right)
        player_rect.top = max(0 if current_room[1] == 0 else -100, player_rect.top)
        player_rect.bottom = min(HEIGHT if current_room[1] == 1 else HEIGHT + 100, player_rect.bottom)

        enemies = room_enemies.get(current_room, [])
        projectiles = room_projectiles.get(current_room, [])

        for enemy in enemies[:]:
            enemy.update()
            if enemy.rect.colliderect(player_rect):
                take_damage(1, enemy.rect.centerx, enemy.rect.centery)
            if sword_rect and enemy.rect.colliderect(sword_rect) and enemy.state != "STUNNED":
                enemy.hp -= 1
                enemy.state = "STUNNED"
                enemy.stun_timer, enemy.knockback_dir = 10, player_facing
                if enemy.hp <= 0: enemies.remove(enemy)
            if enemy.state == "ATTACKING" and enemy.attack_timer == 30:
                projectiles.append(Projectile(enemy.rect.centerx, enemy.rect.centery, enemy.facing[0], enemy.facing[1], True))

        for proj in projectiles[:]:
            proj.update()
            if not screen.get_rect().collidepoint(proj.rect.center):
                projectiles.remove(proj)
                continue
            if proj.is_enemy:
                if proj.rect.colliderect(player_rect):
                    if player_state == "IDLE" and proj.dx == -player_facing[0] and proj.dy == -player_facing[1]:
                        projectiles.remove(proj)
                    else:
                        take_damage(1, proj.rect.centerx, proj.rect.centery)
                        projectiles.remove(proj)
            else:
                for enemy in enemies:
                    if proj.rect.colliderect(enemy.rect):
                        enemy.hp -= 1
                        enemy.state, enemy.stun_timer, enemy.knockback_dir = "STUNNED", 10, (proj.dx, proj.dy)
                        if enemy.hp <= 0: enemies.remove(enemy)
                        if proj in projectiles: projectiles.remove(proj)

    elif game_state == "TRANSITION":
        trans_prog += trans_speed
        if trans_prog >= 1.0:
            trans_prog, current_room, game_state = 1.0, next_room, "PLAYING"
            room_projectiles[next_room].clear() 
        player_rect.x = trans_start_pos[0] + (trans_target_pos[0] - trans_start_pos[0]) * trans_prog
        player_rect.y = trans_start_pos[1] + (trans_target_pos[1] - trans_start_pos[1]) * trans_prog

    if game_state == "PLAYING":
        screen.fill(rooms_bg[current_room])
        for enemy in room_enemies.get(current_room, []): pygame.draw.rect(screen, (200, 50, 50), enemy.rect)
        for proj in room_projectiles.get(current_room, []): pygame.draw.rect(screen, (255, 255, 0), proj.rect)
        if player_state == "ATTACKING" and sword_rect: pygame.draw.rect(screen, (200, 200, 200), sword_rect)
            
        if invul_timer == 0 or (invul_timer // 4) % 2 == 0:
            color = (100, 100, 255) if player_state != "STUNNED" else (255, 255, 255)
            pygame.draw.rect(screen, color, player_rect)
            if player_state == "IDLE":
                shield_rect = pygame.Rect(0, 0, 10, 10)
                if player_facing[0] != 0:
                    shield_rect.size = (4, player_rect.height)
                    shield_rect.center = (player_rect.right if player_facing[0] == 1 else player_rect.left, player_rect.centery)
                else:
                    shield_rect.size = (player_rect.width, 4)
                    shield_rect.center = (player_rect.centerx, player_rect.bottom if player_facing[1] == 1 else player_rect.top)
                pygame.draw.rect(screen, (50, 255, 50), shield_rect)

    elif game_state == "TRANSITION":
        dx, dy = trans_dir
        old_x, old_y = -dx * WIDTH * trans_prog, -dy * HEIGHT * trans_prog
        new_x, new_y = dx * WIDTH * (1.0 - trans_prog), dy * HEIGHT * (1.0 - trans_prog)
        screen.fill((0, 0, 0))
        old_room = pygame.Surface((WIDTH, HEIGHT)); old_room.fill(rooms_bg[current_room]); screen.blit(old_room, (old_x, old_y))
        new_room = pygame.Surface((WIDTH, HEIGHT)); new_room.fill(rooms_bg[next_room]); screen.blit(new_room, (new_x, new_y))
        pygame.draw.rect(screen, (100, 100, 255), player_rect)

    full_hearts = current_hp // 2
    has_half = current_hp % 2 != 0
    
    hud_x, hud_y = 16, 16
    heart_width = 20
    heart_spacing = heart_width + 4
    
    for i in range(full_hearts):
        screen.blit(full_heart_img, (hud_x + i * heart_spacing, hud_y))
        
    if has_half:
        screen.blit(half_heart_img, (hud_x + full_hearts * heart_spacing, hud_y))


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
