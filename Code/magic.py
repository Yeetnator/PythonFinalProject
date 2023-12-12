import pygame
from settings import *

class Magic:
    def __init__(self,animation_player):
        self.sounds = {
            "heal": pygame.mixer.Sound("Documents/Zelda-main/1-level/audio/heal.wav"),
            "flame": pygame.mixer.Sound("Documents/Zelda-main/1-level/audio/flame.wav"),
            "afterimage": pygame.mixer.Sound("Documents/Zelda-main/1-level/audio/afterimage.wav"),
            "time_stop": pygame.mixer.Sound("Documents/Zelda-main/1-level/audio/timestop.wav")
        }
        self.display = pygame.display.get_surface()
        self.animation_player = animation_player
    def heal(self, player, strength, cost, groups):
        self.sounds["heal"].set_volume (0.4)
        self.sounds["heal"].play()
        if player.energy >= cost:
            player.health += strength 
            player.energy -= cost
            if player.health >= player.stats["health"]:
                player.health = player.stats["health"]
            self.animation_player.create_particles( "heal", player.rect.center + pygame.math.Vector2(0,-60), groups)
            self.animation_player.create_particles ("aura", player.rect.center, groups)

    def flame (self, player, cost, groups):
        self.sounds["flame"].set_volume (0.4)
        self.sounds["flame"].play()
        if player.energy >= cost:
            player.energy -= cost
            if "up" in player.status:
                direction = pygame.math.Vector2(0,1)
            elif "down" in player.status:
                direction = pygame.math.Vector2(0,-1)
            elif "left" in player.status:
                direction = pygame.math.Vector2(-1,0)
            else:
                direction = pygame.math.Vector2(1,0)
            for t in range (3):
                for i in range (1,4):
                    if direction.x:
                        offset_x = direction.x * i * TILESIZE
                        x = player.rect.centerx + offset_x
                        y = player.rect.centery - (TILESIZE * (1-t))
                        self.animation_player.create_particles("flame",(x,y),groups )
                    else:
                        offset_y = direction.y * i * TILESIZE
                        x = player.rect.centerx + - (TILESIZE * (1-t))
                        y = player.rect.centery - offset_y
                        self.animation_player.create_particles("flame",(x,y),groups )

    
    def afterimage (self, player,strength, cost, groups):
        self.sounds["afterimage"].set_volume (0.4)
        self.sounds["afterimage"].play()
        self.animation_player.create_particles ("afterimage", player.rect.center, groups)
        if player.energy >= cost:
            player.energy -= cost
            player.vulnerable = False
            player.invulnerability_duration = strength * 400
            player.hurt_time = pygame.time.get_ticks()
    def time (self, player):
        self.sounds["time_stop"].set_volume (0.8)
        self.sounds["time_stop"].play()
        if player.energy >= 60:
            player.energy -= 60
            
        
        
            



