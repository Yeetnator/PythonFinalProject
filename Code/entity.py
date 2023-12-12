import pygame 
from math import sin  
class Enitity (pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animations_speed = 0.15
        self.direction = pygame.math.Vector2()
    def move (self,speed):
       if self.direction.magnitude() != 0:
           self.direction = self.direction.normalize()
       self.hitbox.x += self.direction.x * speed
       self.collision("horizontal")
       self.hitbox.y += self.direction.y * speed
       self.collision("vertical")
       self.rect.center = self.hitbox.center
    def collision (self, direction):
        if direction == "horizontal":
            for sprite in self.obstacle_sprite:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: #moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: #moving left
                        self.hitbox.left = sprite.hitbox.right
        if direction == "vertical":
            for sprite in self.obstacle_sprite:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: #moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: #moving up
                        self.hitbox.top = sprite.hitbox.bottom
    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()
        return (distance, direction)
    def wave_value (self):
        value = sin (pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0

