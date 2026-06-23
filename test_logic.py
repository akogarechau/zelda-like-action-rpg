import unittest
import pygame
from src.entities import Player, Enemy
from src.world import WorldManager
from src.settings import PLAYER_MAX_HP

class TestGameLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.HIDDEN)

        surf = pygame.Surface((10, 10))
        cls.dummy_assets = {
            'player_down': [surf, surf],
            'player_up': [surf, surf],
            'player_left': [surf, surf],
            'player_right': [surf, surf],
            'player_attack_down': surf,
            'player_attack_up': surf,
            'player_attack_left': surf,
            'player_attack_right': surf,
            'enemy_down': surf, 'enemy_up': surf,
            'enemy_left': surf, 'enemy_right': surf,
            'shooter_down': surf, 'shooter_up': surf,
            'shooter_left': surf, 'shooter_right': surf,
            'driller': surf, 'driller_dig': surf,
            'proj_enemy': surf, 'proj_player': surf,
            'wall': surf
        }

    def setUp(self):
        self.player = Player(100, 100, self.dummy_assets)

    def test_player_initial_hp(self):
        self.assertEqual(self.player.current_hp, PLAYER_MAX_HP)
        self.assertEqual(self.player.state, "IDLE")

    def test_player_take_damage(self):
        initial_hp = self.player.current_hp
        
        self.player.take_damage(1, 150, 100)
        
        self.assertEqual(self.player.current_hp, initial_hp - 1)
        self.assertEqual(self.player.state, "STUNNED")
        self.assertTrue(self.player.invul_timer > 0)
        self.assertEqual(self.player.knockback_dir, (-1, 0))

    def test_player_invulnerability(self):
        self.player.take_damage(1, 0, 0)
        hp_after_first_hit = self.player.current_hp
        
        self.player.take_damage(1, 0, 0)
        
        self.assertEqual(self.player.current_hp, hp_after_first_hit)

    def test_enemy_spawns_projectile(self):
        enemy = Enemy(100, 100, self.dummy_assets)
        projectiles = pygame.sprite.Group()
        
        enemy.state = "ATTACKING"
        enemy.attack_timer = 31 
        
        enemy.update(self.player, projectiles_group=projectiles)
        
        self.assertEqual(len(projectiles), 1)

    def test_world_cleared(self):
        world = WorldManager(self.dummy_assets)
        
        self.assertFalse(world.is_cleared())
        
        for group in world.room_enemies.values():
            group.empty()
            
        self.assertTrue(world.is_cleared())

if __name__ == '__main__':
    unittest.main()
