import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zelda-like Action RPG")
clock = pygame.time.Clock()

rooms = {
    (0, 0): (40, 40, 50),
    (1, 0): (70, 40, 40),
    (0, 1): (40, 70, 40),
    (1, 1): (70, 70, 40)
}

current_room = (0, 0)

STATE_PLAYING = 0
STATE_TRANSITION = 1
game_state = STATE_PLAYING

transition_progress = 0.0
transition_speed = 0.03
transition_dir = (0, 0)
next_room = (0, 0)

player_rect = pygame.Rect(400, 300, 40, 40)
player_speed = 5
active_keys = []
trans_start_pos = (0, 0)
trans_target_pos = (0, 0)

movement_map = {
    pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0),
    pygame.K_w: (0, -1), pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0), pygame.K_d: (1, 0)
}

def start_transition(dx, dy, target_x, target_y):
    global game_state, transition_progress, transition_dir
    global next_room, trans_start_pos, trans_target_pos

    game_state = STATE_TRANSITION
    transition_progress = 0.0
    transition_dir = (dx, dy)
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
                if event.key in active_keys:
                    active_keys.remove(event.key)
                active_keys.append(event.key)
        elif event.type == pygame.KEYUP:
            if event.key in active_keys:
                active_keys.remove(event.key)

    if game_state == STATE_PLAYING:
        if active_keys:
            last_key = active_keys[-1]
            dx, dy = movement_map[last_key]
            
            cancel_movement = False
            for key in active_keys:
                kx, ky = movement_map[key]
                if dx == -kx and dy == -ky:
                    cancel_movement = True
                    break
            
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


    elif game_state == STATE_TRANSITION:
        transition_progress += transition_speed
        
        if transition_progress >= 1.0:
            transition_progress = 1.0
            current_room = next_room
            game_state = STATE_PLAYING
            
        player_rect.x = trans_start_pos[0] + (trans_target_pos[0] - trans_start_pos[0]) * transition_progress
        player_rect.y = trans_start_pos[1] + (trans_target_pos[1] - trans_start_pos[1]) * transition_progress


    if game_state == STATE_PLAYING:
        screen.fill(rooms[current_room])
        pygame.draw.rect(screen, (0, 150, 255), player_rect)

    elif game_state == STATE_TRANSITION:
        dx, dy = transition_dir
        
        old_x = -dx * WIDTH * transition_progress
        old_y = -dy * HEIGHT * transition_progress
        
        new_x = dx * WIDTH * (1.0 - transition_progress)
        new_y = dy * HEIGHT * (1.0 - transition_progress)
        
        screen.fill((0, 0, 0))
        
        old_room_surface = pygame.Surface((WIDTH, HEIGHT))
        old_room_surface.fill(rooms[current_room])
        screen.blit(old_room_surface, (old_x, old_y))
        
        new_room_surface = pygame.Surface((WIDTH, HEIGHT))
        new_room_surface.fill(rooms[next_room])
        screen.blit(new_room_surface, (new_x, new_y))
        
        pygame.draw.rect(screen, (0, 150, 255), player_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
