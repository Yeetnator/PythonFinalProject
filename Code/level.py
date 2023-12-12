import pygame
from random import choice
from random import randint 
from settings import *
from tile import *
from player import Player
from support import *
from debug import *
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import Magic
from upgrade import Upgrade
class Level:
    def __init__ (self):
        #get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False
        #sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacles_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        #attack
        self.current_attack = None
        #map
        self.create_map()
        #UI
        self.ui = UI()
        self.upgrade = Upgrade(self.player)
        #particles
        self.animation_player = AnimationPlayer()
        self.Magic = Magic(self.animation_player)
        #special
        self.time = True
    def create_map (self):

        layouts = {
            'boundary': import_csv_layout("Documents/Zelda-main/1-level/map/map_FloorBlocks.csv"),
            'grass': import_csv_layout("Documents/Zelda-main/1-level/map/map_Grass.csv"),
            'object': import_csv_layout("Documents/Zelda-main/1-level/map/map_Objects.csv"),
            'entities': import_csv_layout ("Documents/Zelda-main/1-level/map/map_Entities.csv")
                  }
        graphics = {
            'grass': import_folder("Documents/Zelda-main/1-level/graphics/grass"),
            'objects': import_check("Documents/Zelda-main/1-level/graphics/objects")
        }
        for style,layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != "-1":
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == "boundary":
                            Tile ((x,y),[self.obstacles_sprites],'invisible')
                        if style == "grass":
                            random_grass_image = choice(graphics['grass'])
                            Tile((x,y),[self.attackable_sprites, self.visible_sprites,self.obstacles_sprites],'grass',random_grass_image)
                        if style == "object":
                            surf = graphics["objects"][int(col)]
                            Tile ((x,y), [self.visible_sprites,self.obstacles_sprites],'object',surf)
                        if style == "entities":
                            if col == "394":
                                self.player = Player((x,y), [self.visible_sprites],self.obstacles_sprites,self.create_attack,self.destroy_weapon, self.create_magic)
                            else:
                                if col == "390":
                                    monster_name = "bamboo"
                                elif col == "391":
                                    monster_name = "spirit"
                                elif col == "392":
                                    monster_name = "raccoon"
                                else:
                                    monster_name = "squid" 
                                self.enemy = Enemy (monster_name, (x,y), [self.visible_sprites, self.attackable_sprites], self.obstacles_sprites, self.damage_player, self.trigger_death_particles, self.add_xp) 
    def create_attack(self):
        self.current_attack = Weapon (self.player, [self.visible_sprites,self.attack_sprites])
    def create_magic (self, style, strength, cost):
        if style == "heal":
            self.Magic.heal(self.player, strength, cost, [self.visible_sprites])
        if style == "flame":
            self.Magic.flame (self.player, cost, [self.visible_sprites, self.attack_sprites])
        if style == "dash":
            self.Magic.afterimage(self.player, strength, cost, [self.visible_sprites])
        if style == "time_stop":
            if self.time == True and self.player.energy >= 60:
                self.time = not self.time
                self.Magic.time (self.player)
            elif self.time == False:
                self.time = not self.time
    
    def player_attack_logic (self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprites in collision_sprites:
                        if target_sprites.sprite_type == "grass":
                            pos = target_sprites.rect.center
                            offset = pygame.math.Vector2(0,75)
                            for i in range (randint(3,6)):
                                self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
                            target_sprites.kill()
                        else:
                            target_sprites.get_damage(self.player, attack_sprite.sprite_type)
    def trigger_death_particles (self, pos, particle_type):
        self.animation_player.create_particles(particle_type,pos,[self.visible_sprites])
    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.direction  = - (self.enemy.get_player_distance_direction(self.player)[1])  
            self.player.move(self.player.speed + 15)
            self.player.hurt_time = pygame.time.get_ticks() 
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites]) 

    def destroy_weapon (self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None
    def add_xp (self, amount):
        self.player.exp += amount
    def toggle_menu (self):
        self.game_paused = not self.game_paused
        self.ui.display(self.player)
    def run (self):
        self.visible_sprites.custom_draw(self.player, self.time)
        self.ui.display(self.player)
        if self.game_paused:
            self.upgrade.display()
        elif not self.time:
            self.player.update()
            self.player_attack_logic()
            self.enemy.hit_reaction()
        else:
            self.player_attack_logic()
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.halfwidth = self.display_surface.get_size()[0]//2
        self.halflength = self.display_surface.get_size()[1]//2
        self.floor_surf = pygame.image.load("Documents/Zelda-main/1-level/graphics/tilemap/ground.png").convert()
        self.floor_surf1 = pygame.image.load("Documents/Zelda-main/1-level/graphics/tilemap/grayscaleground.png").convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))
    def custom_draw (self,player, time):
        self.offset.x = player.rect.centerx - self.halfwidth
        self.offset.y = player.rect.centery - self.halflength
        if not time:
            self.display_surface.blit (self.floor_surf1, self.floor_rect.topleft  - self.offset)
        else:
            self.display_surface.blit (self.floor_surf, self.floor_rect.topleft  - self.offset)
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit (sprite.image, offset_pos)
    def enemy_update (self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr (sprite, "sprite_type") and sprite.sprite_type == "enemy"]
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
            