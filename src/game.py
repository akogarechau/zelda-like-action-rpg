import pygame
from src.utils import SpriteSheet
from src.settings import (
    WIDTH, HEIGHT, FPS,
    COLOR_BG_MENU, COLOR_TEXT_MAIN, COLOR_TEXT_SELECT, COLOR_TEXT_MUTED,
    COLOR_TEXT_GAMEOVER, COLOR_TEXT_GAMEOVER_MUTED, COLOR_BLACK,
    PLAYER_SIZE, ENEMY_SIZE, WALL_SIZE, SWORD_SIZE, PROJECTILE_SIZE,
    PLAYER_ATTACK_COOLDOWN
)
from src.entities import Player, Projectile
from src.world import WorldManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zelda")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self._load_assets()

        self.state = "STATE_MENU"
        self.font_title = pygame.font.Font(None, 100)
        self.font_options = pygame.font.Font(None, 60)
        self.font_story = pygame.font.Font(None, 40) 
        
        self.menu_options = ["Начать игру", "Выход"]
        self.menu_index = 0
        self.game_over_options = ["Заново", "Выход"]
        self.game_over_index = 0
        self.death_timer = 0
        self.victory_timer = 0
        
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

    def _load_assets(self):
        self.assets = {}
        
        try:
            link_sheet = SpriteSheet('assets/link.bmp')
            
            c_key_link = link_sheet.sheet.get_at((1, 11))
            self.assets['player_down'] = [
                link_sheet.get_image(1, 11, 16, 16, PLAYER_SIZE, c_key_link),
                link_sheet.get_image(18, 11, 16, 16, PLAYER_SIZE, c_key_link)
            ]
            self.assets['player_right'] = [
                link_sheet.get_image(35, 11, 16, 16, PLAYER_SIZE, c_key_link),
                link_sheet.get_image(52, 11, 16, 16, PLAYER_SIZE, c_key_link)
            ]
            self.assets['player_up'] = [
                link_sheet.get_image(69, 11, 16, 16, PLAYER_SIZE, c_key_link),
                link_sheet.get_image(86, 11, 16, 16, PLAYER_SIZE, c_key_link)
            ]
            self.assets['player_left'] = [
                pygame.transform.flip(self.assets['player_right'][0], True, False),
                pygame.transform.flip(self.assets['player_right'][1], True, False)
            ]

            self.assets['player_attack_down'] = link_sheet.get_image(1, 47, 16, 16, PLAYER_SIZE, c_key_link)
            self.assets['player_attack_right'] = link_sheet.get_image(1, 77, 16, 16, PLAYER_SIZE, c_key_link)
            self.assets['player_attack_up'] = link_sheet.get_image(1, 109, 16, 16, PLAYER_SIZE, c_key_link)
            self.assets['player_attack_left'] = pygame.transform.flip(self.assets['player_attack_right'], True, False)
            
            c_key_sword = link_sheet.sheet.get_at((1, 154))
            self.assets['sword_up'] = link_sheet.get_image(1, 154, 7, 16, SWORD_SIZE, c_key_sword)
            self.assets['sword_right'] = pygame.transform.rotate(self.assets['sword_up'], -90)
            self.assets['sword_down'] = pygame.transform.rotate(self.assets['sword_up'], 180)
            self.assets['sword_left'] = pygame.transform.rotate(self.assets['sword_up'], 90)
        except Exception:
            surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            surf.fill((100, 100, 255))
            for k in ['player_down', 'player_up', 'player_left', 'player_right']: 
                self.assets[k] = [surf, surf]
            for k in ['player_attack_down', 'player_attack_up', 'player_attack_left', 'player_attack_right']:
                self.assets[k] = surf

            surf_s_vert = pygame.Surface((17, SWORD_SIZE))
            surf_s_vert.fill((200, 200, 200))
            surf_s_horiz = pygame.Surface((SWORD_SIZE, 17))
            surf_s_horiz.fill((200, 200, 200))
            self.assets['sword_down'] = surf_s_vert
            self.assets['sword_up'] = surf_s_vert
            self.assets['sword_left'] = surf_s_horiz
            self.assets['sword_right'] = surf_s_horiz

        try:
            enemy_sheet = SpriteSheet('assets/enemies.bmp')
            
            c_key_enemy = enemy_sheet.sheet.get_at((1, 18))
            self.assets['enemy_down'] = enemy_sheet.get_image(1, 11, 16, 16, ENEMY_SIZE, c_key_enemy)
            self.assets['enemy_left'] = enemy_sheet.get_image(35, 11, 16, 16, ENEMY_SIZE, c_key_enemy)
            self.assets['enemy_up'] = pygame.transform.flip(self.assets['enemy_down'], False, True)
            self.assets['enemy_right'] = pygame.transform.flip(self.assets['enemy_left'], True, False)
            
            c_key_shooter = enemy_sheet.sheet.get_at((82, 11))
            self.assets['shooter_down'] = enemy_sheet.get_image(82, 11, 16, 16, ENEMY_SIZE, c_key_shooter)
            self.assets['shooter_right'] = enemy_sheet.get_image(116, 11, 16, 16, ENEMY_SIZE, c_key_shooter)
            self.assets['shooter_up'] = enemy_sheet.get_image(99, 11, 16, 16, ENEMY_SIZE, c_key_shooter)
            self.assets['shooter_left'] = pygame.transform.flip(self.assets['shooter_right'], True, False)
            
            c_key_driller = enemy_sheet.sheet.get_at((69, 59))
            self.assets['driller'] = enemy_sheet.get_image(69, 59, 16, 16, ENEMY_SIZE, c_key_driller)
            self.assets['driller_dig'] = enemy_sheet.get_image(35, 59, 16, 16, ENEMY_SIZE, c_key_driller)
            
        except Exception:
            surf = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
            surf.fill((255, 0, 0))
            for k in ['enemy_down', 'enemy_right', 'enemy_up', 'enemy_left', 'shooter_down', 'shooter_right', 'shooter_up', 'shooter_left', 'driller', 'driller_dig']: 
                self.assets[k] = surf

        surf_p = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
        surf_p.fill((255, 255, 0))
        self.assets['proj_enemy'] = surf_p
        self.assets['proj_player'] = surf_p

        try:
            tiles_sheet = SpriteSheet('assets/tiles.bmp')
            self.assets['wall'] = tiles_sheet.get_image(1, 1, 16, 16, WALL_SIZE, None)
        except Exception:
            surf = pygame.Surface((WALL_SIZE, WALL_SIZE))
            surf.fill((100, 100, 100))
            self.assets['wall'] = surf

        try:
            hud_sheet = SpriteSheet('assets/hud.bmp')
            c_key_hud = hud_sheet.sheet.get_at((645, 117))
            
            self.full_heart_img = hud_sheet.get_image(645, 117, 8, 8, 43, c_key_hud)
            self.half_heart_img = hud_sheet.get_image(636, 117, 8, 8, 43, c_key_hud)
        except Exception:
            self.full_heart_img = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.full_heart_img, (255, 50, 50), (0, 0, 20, 20)) 
            self.half_heart_img = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.half_heart_img, (255, 50, 50), (0, 0, 10, 20))

    def hard_reset(self):
        self.world = WorldManager(self.assets)
        self.player = Player(400, 300, self.assets)
        self.active_keys.clear()
        self.victory_timer = 0
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
            elif event.type == pygame.KEYUP:
                if event.key in self.active_keys:
                    self.active_keys.remove(event.key)
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

    def _handle_keydown(self, event):
        if event.key in self.movement_map:
            if event.key in self.active_keys: 
                self.active_keys.remove(event.key)
            self.active_keys.append(event.key)

        if self.state == "STATE_MENU":
            if event.key == pygame.K_UP:
                self.menu_index = (self.menu_index - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.menu_index = (self.menu_index + 1) % len(self.menu_options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.menu_index == 0:
                    self.hard_reset()
                else:
                    self.running = False
                        
        elif self.state in ("STATE_GAME_OVER", "STATE_VICTORY"):
            if event.key == pygame.K_UP:
                self.game_over_index = (self.game_over_index - 1) % len(self.game_over_options)
            elif event.key == pygame.K_DOWN:
                self.game_over_index = (self.game_over_index + 1) % len(self.game_over_options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.game_over_index == 0:
                    self.hard_reset()
                else:
                    self.running = False

        elif self.state == "STATE_PLAYING":
            if event.key == pygame.K_SPACE and self.player.state == "IDLE" and self.player.attack_cooldown <= 0:
                self.player.state = "ATTACKING"
                self.player.attack_timer = 15
                self.player.attack_cooldown = PLAYER_ATTACK_COOLDOWN
                
                if self.player.facing[0] != 0:
                    hitbox_w, hitbox_h = SWORD_SIZE, 17
                else:
                    hitbox_w, hitbox_h = 17, SWORD_SIZE
                
                self.player.sword_rect = pygame.Rect(0, 0, hitbox_w, hitbox_h)
                self.player.sword_rect.center = (
                    self.player.rect.centerx + self.player.facing[0]*30, 
                    self.player.rect.centery + self.player.facing[1]*30
                )
                
                if self.player.current_hp == self.player.max_hp:
                    beam = Projectile(self.player.rect.centerx, self.player.rect.centery, 
                                      self.player.facing[0], self.player.facing[1], False, self.assets['proj_player'])
                    self.world.room_projectiles[self.world.current_room].add(beam)

    def update(self):
        if self.state == "STATE_DEATH_ANIMATION":
            self._update_death()
        elif self.state == "STATE_PLAYING":
            self._update_playing()
        elif self.state == "STATE_TRANSITION":
            self._update_transition()
        elif self.state == "STATE_VICTORY":
            self.victory_timer += 1

    def _update_death(self):
        self.death_timer -= 1
        self.player.death_angle += 15
        self.player.death_alpha = max(0, self.player.death_alpha - 2)
        if self.death_timer <= 0:
            self.state = "STATE_GAME_OVER"

    def _update_playing(self):
        if self.player.invul_timer > 0:
            self.player.invul_timer -= 1
        if self.player.attack_cooldown > 0:
            self.player.attack_cooldown -= 1

        if self.player.current_hp <= 0:
            self.state = "STATE_DEATH_ANIMATION"
            self.death_timer = 120
            self.active_keys.clear()
            return

        if not self.world.secret_door_opened and self.world.is_cleared():
            self.world.secret_door_opened = True
            self.world.room_walls[(1, 1)] = self.world._generate_walls((1, 1), secret_door=True)

        cur_r = self.world.current_room
        walls = self.world.room_walls.get(cur_r)
        
        self.player.is_moving = False

        if self.player.state == "STUNNED":
            self.player.rect.x += self.player.knockback_dir[0] * 8
            for wall in walls:
                if self.player.rect.colliderect(wall.rect):
                    if self.player.knockback_dir[0] > 0:
                        self.player.rect.right = wall.rect.left
                    elif self.player.knockback_dir[0] < 0:
                        self.player.rect.left = wall.rect.right
                    
            self.player.rect.y += self.player.knockback_dir[1] * 8
            for wall in walls:
                if self.player.rect.colliderect(wall.rect):
                    if self.player.knockback_dir[1] > 0:
                        self.player.rect.bottom = wall.rect.top
                    elif self.player.knockback_dir[1] < 0:
                        self.player.rect.top = wall.rect.bottom
                    
            self.player.stun_timer -= 1
            if self.player.stun_timer <= 0:
                self.player.state = "IDLE"
                
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
                    if dx == -kx and dy == -ky:
                        cancel_movement = True
                        break
                        
                if not cancel_movement:
                    self.player.is_moving = True
                    self.player.rect.x += dx * self.player.speed
                    for wall in walls:
                        if self.player.rect.colliderect(wall.rect):
                            if dx > 0:
                                self.player.rect.right = wall.rect.left
                            elif dx < 0:
                                self.player.rect.left = wall.rect.right
                            
                    self.player.rect.y += dy * self.player.speed
                    for wall in walls:
                        if self.player.rect.colliderect(wall.rect):
                            if dy > 0:
                                self.player.rect.bottom = wall.rect.top
                            elif dy < 0:
                                self.player.rect.top = wall.rect.bottom

        self.player.update_image()
        self._handle_room_bounds()

        enemies = self.world.room_enemies.get(cur_r)
        projectiles = self.world.room_projectiles.get(cur_r)

        enemies.update(self.player, projectiles, walls)
        projectiles.update()

        self._handle_collisions(enemies, projectiles, walls)

    def _handle_room_bounds(self):
        offset = WALL_SIZE + 10 
        cur_r = self.world.current_room
        
        if self.player.rect.left > WIDTH and cur_r == (1, 1) and self.world.secret_door_opened:
            self.state = "STATE_VICTORY"
            self.active_keys.clear()
            return

        if self.player.rect.left < 0 and cur_r[0] > 0:
            self.start_transition(-1, 0, WIDTH - self.player.rect.width - offset, self.player.rect.y)
        elif self.player.rect.right > WIDTH and cur_r[0] < 1:
            self.start_transition(1, 0, offset, self.player.rect.y)
        elif self.player.rect.top < 0 and cur_r[1] > 0:
            self.start_transition(0, -1, self.player.rect.x, HEIGHT - self.player.rect.height - offset)
        elif self.player.rect.bottom > HEIGHT and cur_r[1] < 1:
            self.start_transition(0, 1, self.player.rect.x, offset)

    def _handle_collisions(self, enemies, projectiles, walls):
        for enemy in enemies:
            if getattr(enemy, 'is_underground', False):
                continue
            if enemy.rect.colliderect(self.player.rect):
                self.player.take_damage(1, enemy.rect.centerx, enemy.rect.centery)
            if self.player.sword_rect and enemy.rect.colliderect(self.player.sword_rect) and enemy.state != "STUNNED":
                enemy.hp -= 1
                enemy.state = "STUNNED"
                enemy.stun_timer, enemy.knockback_dir = 10, self.player.facing
                enemy.flash_timer = 6
                if enemy.hp <= 0:
                    enemy.kill()

        for proj in projectiles:
            if pygame.sprite.spritecollideany(proj, walls):
                proj.kill()
                continue
            if proj.is_enemy:
                if proj.rect.colliderect(self.player.rect):
                    dot_product = proj.dx * self.player.facing[0] + proj.dy * self.player.facing[1]
                    if self.player.state == "IDLE" and dot_product < -0.5:
                        pass 
                    else:
                        self.player.take_damage(1, proj.rect.centerx, proj.rect.centery)
                    proj.kill()
            else:
                for enemy in enemies:
                    if getattr(enemy, 'is_underground', False):
                        continue
                    if proj.rect.colliderect(enemy.rect):
                        enemy.hp -= 1
                        enemy.state, enemy.stun_timer, enemy.knockback_dir = "STUNNED", 10, (proj.dx, proj.dy)
                        enemy.flash_timer = 6
                        if enemy.hp <= 0:
                            enemy.kill()
                        proj.kill()

    def _update_transition(self):
        self.trans_prog += self.trans_speed
        if self.trans_prog >= 1.0:
            self.trans_prog = 1.0
            self.world.current_room = self.next_room
            self.state = "STATE_PLAYING"
            self.world.room_projectiles[self.next_room].empty() 
        self.player.rect.x = self.trans_start_pos[0] + (self.trans_target_pos[0] - self.trans_start_pos[0]) * self.trans_prog
        self.player.rect.y = self.trans_start_pos[1] + (self.trans_target_pos[1] - self.trans_start_pos[1]) * self.trans_prog

    def draw(self):
        if self.state == "STATE_MENU":
            self._draw_menu()
        elif self.state == "STATE_GAME_OVER":
            self._draw_game_over()
        elif self.state == "STATE_VICTORY":
            self._draw_victory()
        elif self.state in ("STATE_PLAYING", "STATE_DEATH_ANIMATION"):
            self._draw_gameplay()
        elif self.state == "STATE_TRANSITION":
            self._draw_transition()

    def _draw_menu(self):
        self.screen.fill(COLOR_BG_MENU)
        self.draw_text_centered("Just another Monday", self.font_title, COLOR_TEXT_MAIN, HEIGHT // 3)
        for i, option in enumerate(self.menu_options):
            text = f"> {option}" if i == self.menu_index else f"  {option}"
            color = COLOR_TEXT_SELECT if i == self.menu_index else COLOR_TEXT_MUTED
            self.draw_text_centered(text, self.font_options, color, HEIGHT // 2 + i * 70)

    def _draw_game_over(self):
        self.screen.fill(COLOR_BLACK)
        self.draw_text_centered("Поражение", self.font_title, COLOR_TEXT_GAMEOVER, HEIGHT // 3)
        for i, option in enumerate(self.game_over_options):
            text = f"> {option}" if i == self.game_over_index else f"  {option}"
            color = COLOR_TEXT_MAIN if i == self.game_over_index else COLOR_TEXT_GAMEOVER_MUTED
            self.draw_text_centered(text, self.font_options, color, HEIGHT // 2 + i * 70)

    def _draw_victory(self):
        self.screen.fill(COLOR_BLACK)
        if self.victory_timer > 30:
            self.draw_text_centered("Ты спас принцессу Зельду!", self.font_story, (255, 200, 255), HEIGHT // 3 - 30)
        if self.victory_timer > 90:
            self.draw_text_centered("Мир снова спасен!", self.font_story, COLOR_TEXT_MAIN, HEIGHT // 3 + 20)
        if self.victory_timer > 150:
            self.draw_text_centered("Победа", self.font_title, COLOR_TEXT_SELECT, HEIGHT // 2 + 30)
        if self.victory_timer > 210:
            for i, option in enumerate(self.game_over_options):
                text = f"> {option}" if i == self.game_over_index else f"  {option}"
                color = COLOR_TEXT_MAIN if i == self.game_over_index else COLOR_TEXT_GAMEOVER_MUTED
                self.draw_text_centered(text, self.font_options, color, HEIGHT // 2 + 130 + i * 50)

    def _draw_gameplay(self):
        self.screen.fill(self.world.rooms_bg[self.world.current_room])
        cur_r = self.world.current_room
        
        for wall in self.world.room_walls.get(cur_r):
            self.screen.blit(wall.image, wall.rect)
            
        for enemy in self.world.room_enemies.get(cur_r): 
            if getattr(enemy, 'is_underground', False) and enemy.state == "HIDDEN":
                continue 
            
            if enemy.flash_timer > 0:
                flash_surf = enemy.image.copy()
                flash_surf.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(flash_surf, enemy.rect)
            else:
                self.screen.blit(enemy.image, enemy.rect)
            
        for proj in self.world.room_projectiles.get(cur_r): 
            self.screen.blit(proj.image, proj.rect)
        
        if self.state == "STATE_PLAYING":
            if self.player.state == "ATTACKING" and self.player.sword_rect:
                if self.player.facing == (0, 1):
                    sword_img = self.assets['sword_down']
                elif self.player.facing == (0, -1):
                    sword_img = self.assets['sword_up']
                elif self.player.facing == (-1, 0):
                    sword_img = self.assets['sword_left']
                elif self.player.facing == (1, 0):
                    sword_img = self.assets['sword_right']
                
                img_rect = sword_img.get_rect(center=self.player.sword_rect.center)
                self.screen.blit(sword_img, img_rect)
                
            if self.player.invul_timer == 0 or (self.player.invul_timer // 4) % 2 == 0:
                self.screen.blit(self.player.image, self.player.rect)
        
        elif self.state == "STATE_DEATH_ANIMATION":
            rotated = pygame.transform.rotate(self.player.image, self.player.death_angle)
            rotated.set_alpha(self.player.death_alpha)
            self.screen.blit(rotated, rotated.get_rect(center=self.player.rect.center))

        if self.state == "STATE_PLAYING":
            self._draw_hud()

    def _draw_hud(self):
        full_hearts = self.player.current_hp // 2
        has_half = self.player.current_hp % 2 != 0
        
        hud_x, hud_y, heart_width = 18, 10, 43
        heart_spacing = heart_width + 3
        
        max_hearts = self.player.max_hp // 2
        bar_width = (max_hearts * heart_spacing) - 4
        
        pygame.draw.rect(self.screen, COLOR_BLACK, (8, 4, bar_width, 30))
        pygame.draw.rect(self.screen, (0, 64, 255), (6, 2, bar_width + 4, 34), 2)

        for i in range(full_hearts):
            self.screen.blit(self.full_heart_img, (hud_x + i * heart_spacing, hud_y))
        if has_half:
            self.screen.blit(self.half_heart_img, (hud_x + full_hearts * heart_spacing, hud_y))

    def _draw_transition(self):
        dx, dy = self.trans_dir
        old_x, old_y = -dx * WIDTH * self.trans_prog, -dy * HEIGHT * self.trans_prog
        new_x, new_y = dx * WIDTH * (1.0 - self.trans_prog), dy * HEIGHT * (1.0 - self.trans_prog)
        self.screen.fill(COLOR_BLACK)
        
        old_room = pygame.Surface((WIDTH, HEIGHT))
        old_room.fill(self.world.rooms_bg[self.world.current_room])
        for wall in self.world.room_walls[self.world.current_room]:
            old_room.blit(wall.image, wall.rect)
        self.screen.blit(old_room, (old_x, old_y))
        
        new_room = pygame.Surface((WIDTH, HEIGHT))
        new_room.fill(self.world.rooms_bg[self.next_room])
        for wall in self.world.room_walls[self.next_room]:
            new_room.blit(wall.image, wall.rect)
        self.screen.blit(new_room, (new_x, new_y))
        
        self.screen.blit(self.player.image, self.player.rect)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
