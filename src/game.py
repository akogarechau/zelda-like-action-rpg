import pygame
from src.settings import WIDTH, HEIGHT, FPS
from src.entities import Player, Projectile
from src.world import WorldManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Action-RPG Engine: Modular Architecture")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "STATE_MENU"

        self.full_heart_img = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.full_heart_img, (255, 50, 50), (0, 0, 20, 20)) 
        self.half_heart_img = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.half_heart_img, (255, 50, 50), (0, 0, 10, 20)) 
        
        self.font_title = pygame.font.Font(None, 100)
        self.font_options = pygame.font.Font(None, 60)
        
        self.menu_options = ["Start", "Exit"]
        self.menu_index = 0
        self.game_over_options = ["Restart", "Exit"]
        self.game_over_index = 0
        self.death_timer = 0
        
        self.world = None
        self.player = None
        self.active_keys = []
        self.movement_map = {
            pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0)
        }
        
        self.trans_prog = 0.0
        self.trans_speed = 0.03
        self.trans_dir, self.next_room = (0, 0), (0, 0)
        self.trans_start_pos, self.trans_target_pos = (0, 0), (0, 0)

    def hard_reset(self):
        self.world = WorldManager()
        self.player = Player(400, 300)
        self.active_keys.clear()
        self.state = "STATE_PLAYING"

    def start_transition(self, dx, dy, target_x, target_y):
        self.state = "STATE_TRANSITION"
        self.trans_prog = 0.0
        self.trans_dir = (dx, dy)
        self.next_room = (self.world.current_room[0] + dx, self.world.current_room[1] + dy)
        self.trans_start_pos = (self.player.rect.x, self.player.rect.y)
        self.trans_target_pos = (target_x, target_y)

    def draw_text_centered(self, text, font, color, y_pos):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(WIDTH // 2, y_pos))
        self.screen.blit(surface, rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYUP:
                if event.key in self.active_keys:
                    self.active_keys.remove(event.key)
            elif event.type == pygame.KEYDOWN and event.key in self.movement_map:
                if event.key in self.active_keys: 
                    self.active_keys.remove(event.key)
                self.active_keys.append(event.key)

            if self.state == "STATE_MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.menu_index == 0: self.hard_reset()
                        else: self.running = False
                            
            elif self.state == "STATE_GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.game_over_index = (self.game_over_index - 1) % len(self.game_over_options)
                    elif event.key == pygame.K_DOWN:
                        self.game_over_index = (self.game_over_index + 1) % len(self.game_over_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.game_over_index == 0: self.hard_reset()
                        else: self.running = False

            elif self.state == "STATE_PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.player.state == "IDLE":
                        self.player.state = "ATTACKING"
                        self.player.attack_timer = 15
                        self.player.sword_rect = pygame.Rect(0, 0, 40, 40)
                        self.player.sword_rect.center = (
                            self.player.rect.centerx + self.player.facing[0]*40, 
                            self.player.rect.centery + self.player.facing[1]*40
                        )
                        if self.player.current_hp == self.player.max_hp:
                            beam = Projectile(self.player.rect.centerx, self.player.rect.centery, 
                                              self.player.facing[0], self.player.facing[1], is_enemy=False)
                            self.world.room_projectiles[self.world.current_room].append(beam)

    def update(self):
        if self.state == "STATE_DEATH_ANIMATION":
            self.death_timer -= 1
            self.player.death_angle += 15
            self.player.death_alpha = max(0, self.player.death_alpha - 2)
            if self.death_timer <= 0:
                self.state = "STATE_GAME_OVER"
                
        elif self.state == "STATE_PLAYING":
            if self.player.invul_timer > 0: self.player.invul_timer -= 1

            if self.player.current_hp <= 0:
                self.state = "STATE_DEATH_ANIMATION"
                self.death_timer = 120
                self.active_keys.clear()
                return

            if self.player.state == "STUNNED":
                self.player.rect.x += self.player.knockback_dir[0] * 8
                self.player.rect.y += self.player.knockback_dir[1] * 8
                self.player.stun_timer -= 1
                if self.player.stun_timer <= 0: self.player.state = "IDLE"
            elif self.player.state == "ATTACKING":
                self.player.attack_timer -= 1
                if self.player.attack_timer <= 0:
                    self.player.state = "IDLE"
                    self.player.sword_rect = None
            elif self.player.state == "IDLE":
                if self.active_keys:
                    last_key = self.active_keys[-1]
                    dx, dy = self.movement_map[last_key]
                    self.player.facing = (dx, dy)
                    cancel_movement = False
                    for key in self.active_keys:
                        kx, ky = self.movement_map[key]
                        if dx == -kx and dy == -ky: cancel_movement = True; break
                    if not cancel_movement:
                        self.player.rect.x += dx * self.player.speed
                        self.player.rect.y += dy * self.player.speed

            offset = 10
            cur_r = self.world.current_room
            if self.player.rect.left < 0 and cur_r[0] > 0:
                self.start_transition(-1, 0, WIDTH - self.player.rect.width - offset, self.player.rect.y)
            elif self.player.rect.right > WIDTH and cur_r[0] < 1:
                self.start_transition(1, 0, offset, self.player.rect.y)
            elif self.player.rect.top < 0 and cur_r[1] > 0:
                self.start_transition(0, -1, self.player.rect.x, HEIGHT - self.player.rect.height - offset)
            elif self.player.rect.bottom > HEIGHT and cur_r[1] < 1:
                self.start_transition(0, 1, self.player.rect.x, offset)
                
            self.player.rect.left = max(0 if cur_r[0] == 0 else -100, self.player.rect.left)
            self.player.rect.right = min(WIDTH if cur_r[0] == 1 else WIDTH + 100, self.player.rect.right)
            self.player.rect.top = max(0 if cur_r[1] == 0 else -100, self.player.rect.top)
            self.player.rect.bottom = min(HEIGHT if cur_r[1] == 1 else HEIGHT + 100, self.player.rect.bottom)

            enemies = self.world.room_enemies.get(cur_r, [])
            projectiles = self.world.room_projectiles.get(cur_r, [])

            for enemy in enemies[:]:
                enemy.update()
                if enemy.rect.colliderect(self.player.rect):
                    self.player.take_damage(1, enemy.rect.centerx, enemy.rect.centery)
                if self.player.sword_rect and enemy.rect.colliderect(self.player.sword_rect) and enemy.state != "STUNNED":
                    enemy.hp -= 1
                    enemy.state = "STUNNED"
                    enemy.stun_timer, enemy.knockback_dir = 10, self.player.facing
                    enemy.flash_timer = 6
                    if enemy.hp <= 0: enemies.remove(enemy)
                if enemy.state == "ATTACKING" and enemy.attack_timer == 30:
                    projectiles.append(Projectile(enemy.rect.centerx, enemy.rect.centery, enemy.facing[0], enemy.facing[1], True))

            for proj in projectiles[:]:
                proj.update()
                if not self.screen.get_rect().collidepoint(proj.rect.center):
                    projectiles.remove(proj)
                    continue
                if proj.is_enemy:
                    if proj.rect.colliderect(self.player.rect):
                        if self.player.state == "IDLE" and proj.dx == -self.player.facing[0] and proj.dy == -self.player.facing[1]:
                            pass 
                        else:
                            self.player.take_damage(1, proj.rect.centerx, proj.rect.centery)
                        projectiles.remove(proj)
                else:
                    for enemy in enemies:
                        if proj.rect.colliderect(enemy.rect):
                            enemy.hp -= 1
                            enemy.state, enemy.stun_timer, enemy.knockback_dir = "STUNNED", 10, (proj.dx, proj.dy)
                            enemy.flash_timer = 6
                            if enemy.hp <= 0: enemies.remove(enemy)
                            if proj in projectiles: projectiles.remove(proj)

        elif self.state == "STATE_TRANSITION":
            self.trans_prog += self.trans_speed
            if self.trans_prog >= 1.0:
                self.trans_prog = 1.0
                self.world.current_room = self.next_room
                self.state = "STATE_PLAYING"
                self.world.room_projectiles[self.next_room].clear() 
            self.player.rect.x = self.trans_start_pos[0] + (self.trans_target_pos[0] - self.trans_start_pos[0]) * self.trans_prog
            self.player.rect.y = self.trans_start_pos[1] + (self.trans_target_pos[1] - self.trans_start_pos[1]) * self.trans_prog

    def draw(self):
        if self.state == "STATE_MENU":
            self.screen.fill((20, 20, 30))
            self.draw_text_centered("Game", self.font_title, (255, 255, 255), HEIGHT // 3)
            for i, option in enumerate(self.menu_options):
                text = f"> {option}" if i == self.menu_index else f"  {option}"
                color = (255, 200, 50) if i == self.menu_index else (150, 150, 150)
                self.draw_text_centered(text, self.font_options, color, HEIGHT // 2 + i * 70)

        elif self.state == "STATE_GAME_OVER":
            self.screen.fill((0, 0, 0))
            self.draw_text_centered("GAME OVER", self.font_title, (255, 50, 50), HEIGHT // 3)
            for i, option in enumerate(self.game_over_options):
                text = f"> {option}" if i == self.game_over_index else f"  {option}"
                color = (255, 255, 255) if i == self.game_over_index else (100, 100, 100)
                self.draw_text_centered(text, self.font_options, color, HEIGHT // 2 + i * 70)

        elif self.state in ("STATE_PLAYING", "STATE_DEATH_ANIMATION"):
            self.screen.fill(self.world.rooms_bg[self.world.current_room])
            
            for enemy in self.world.room_enemies.get(self.world.current_room, []): 
                color = (255, 255, 255) if enemy.flash_timer > 0 else (200, 50, 50)
                pygame.draw.rect(self.screen, color, enemy.rect)
                
            for proj in self.world.room_projectiles.get(self.world.current_room, []): 
                pygame.draw.rect(self.screen, (255, 255, 0), proj.rect)
            
            if self.state == "STATE_PLAYING":
                if self.player.state == "ATTACKING" and self.player.sword_rect: 
                    pygame.draw.rect(self.screen, (200, 200, 200), self.player.sword_rect)
                    
                if self.player.invul_timer == 0 or (self.player.invul_timer // 4) % 2 == 0:
                    color = (100, 100, 255) if self.player.state != "STUNNED" else (255, 255, 255)
                    pygame.draw.rect(self.screen, color, self.player.rect)
                    
                    if self.player.state == "IDLE":
                        shield_rect = pygame.Rect(0, 0, 10, 10)
                        if self.player.facing[0] != 0:
                            shield_rect.size = (4, self.player.rect.height)
                            shield_rect.center = (self.player.rect.right if self.player.facing[0] == 1 else self.player.rect.left, self.player.rect.centery)
                        else:
                            shield_rect.size = (self.player.rect.width, 4)
                            shield_rect.center = (self.player.rect.centerx, self.player.rect.bottom if self.player.facing[1] == 1 else self.player.rect.top)
                        pygame.draw.rect(self.screen, (50, 255, 50), shield_rect)
            
            elif self.state == "STATE_DEATH_ANIMATION":
                death_surf = pygame.Surface((self.player.rect.width, self.player.rect.height), pygame.SRCALPHA)
                death_surf.fill((100, 100, 255))
                rotated = pygame.transform.rotate(death_surf, self.player.death_angle)
                rotated.set_alpha(self.player.death_alpha)
                self.screen.blit(rotated, rotated.get_rect(center=self.player.rect.center))

            if self.state == "STATE_PLAYING":
                full_hearts = self.player.current_hp // 2
                has_half = self.player.current_hp % 2 != 0
                hud_x, hud_y, heart_width = 16, 16, 20
                heart_spacing = heart_width + 4
                for i in range(full_hearts):
                    self.screen.blit(self.full_heart_img, (hud_x + i * heart_spacing, hud_y))
                if has_half:
                    self.screen.blit(self.half_heart_img, (hud_x + full_hearts * heart_spacing, hud_y))

        elif self.state == "STATE_TRANSITION":
            dx, dy = self.trans_dir
            old_x, old_y = -dx * WIDTH * self.trans_prog, -dy * HEIGHT * self.trans_prog
            new_x, new_y = dx * WIDTH * (1.0 - self.trans_prog), dy * HEIGHT * (1.0 - self.trans_prog)
            self.screen.fill((0, 0, 0))
            
            old_room = pygame.Surface((WIDTH, HEIGHT)); old_room.fill(self.world.rooms_bg[self.world.current_room])
            self.screen.blit(old_room, (old_x, old_y))
            
            new_room = pygame.Surface((WIDTH, HEIGHT)); new_room.fill(self.world.rooms_bg[self.next_room])
            self.screen.blit(new_room, (new_x, new_y))
            
            pygame.draw.rect(self.screen, (100, 100, 255), self.player.rect)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
