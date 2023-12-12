import pygame
from settings import *
from support import *
from entity import Enitity

class Player (Enitity):
    def __init__(self,pos,groups, obstacle_sprite, create_attack, destroy_attack, create_magic):
        super().__init__(groups)
        self.image = pygame.image.load("Documents/Zelda-main/1-level/graphics/test/player.png").convert_alpha()
        self.import_player_assets()
        self.rect = self.image.get_rect(topleft = pos)
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = 0
        self.obstacle_sprite = obstacle_sprite
        self.hitbox = self.rect.inflate (-10,HITBOX_OFFSET["player"])
        self.status = "down"

        #weapon
        self.create_attack = create_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.destroy_attack = destroy_attack
        self.switch_weapon = False
        self.switch_time = 0
        self.switch_cooldown = 100
        #magic 
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.switch_magic = False
        self.magic_switch_time = 0

        #stats
        self.stats = {"health": 100, "energy": 60, "attack": 5, "magic": 5, "speed":5}
        self.max_stats = {"health": 300, "energy": 140, "attack": 20, "magic": 10, "speed":10}
        self.upgrade_cost = {"health": 100, "energy": 100, "attack": 100, "magic": 100, "speed": 100}
        self.exp = 123
        self.health = self.stats["health"]
        self.energy = self.stats["energy"]
        self.attack = self.stats["attack"]
        self.speed = self.stats["speed"]

        #damage
        self.vulnerable = True
        self.hurt_time =  0
        self.invulnerability_duration = 500

        #import a sound
        self.weapon_attack_sound = pygame.mixer.Sound ("Documents/Zelda-main/1-level/audio/sword.wav")
        self.weapon_attack_sound.set_volume (0.4)

    def import_player_assets(self):
        character_path = ("Documents/Zelda-main/1-level/graphics/player/")
        self.animations = {"up": [], "down": [], "left": [], 'right': [],
                          "right_idle": [], "left_idle": [], "up_idle": [], "down_idle": [],
                          "right_attack": [], "left_attack": [], "up_attack": [], "down_attack": []}
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder (full_path)
    def input(self):
        #movement input
        keys = pygame.key.get_pressed()
        if not self.attacking:
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = "up"
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = "down"
            else:
                self.direction.y = 0
            if keys[pygame.K_a]:
                self.direction.x = -1
                self.status = "left"
            elif keys[pygame.K_d]:
                self.direction.x = 1
                self.status = "right"
            else:
                self.direction.x = 0
            #attack input
            if keys[pygame.K_j]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attack_sound.play()
            if keys[pygame.K_k]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.magic = list(magic_data.keys())[self.magic_index]
                style = self.magic
                strength = magic_data [self.magic]["strength"] + self.stats['magic']
                cost = magic_data [self.magic]["cost"]
                self.create_magic(style,strength,cost)
        if keys[pygame.K_u] and not self.switch_weapon:
            self.switch_time = pygame.time.get_ticks()
            self.switch_weapon = True
            self.weapon_index += 1
            if self.weapon_index >= len(list(weapon_data.keys())):
                self.weapon_index = 0
            self.weapon = list(weapon_data.keys())[self.weapon_index]
        if keys[pygame.K_o] and not self.switch_magic:
            self.magic_switch_time = pygame.time.get_ticks()
            self.switch_magic = True
            self.magic_index += 1
            if self.magic_index >= len(list(magic_data.keys())):
                 self.magic_index = 0
            self.magic = list(weapon_data.keys())[self.magic_index]

    def get_status(self):
        #idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not "idle" in self.status and not "attack" in self.status:
                self.status = self.status + '_idle'
        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not "attack" in self.status:
                if "idle" in self.status:
                    self.status = self.status.replace("_idle","_attack")
                else:
                    self.status = self.status + "_attack"
        else: 
            self.status = self.status.replace("_attack","")

    def cooldown (self):
        current_time = pygame.time.get_ticks() 
        if current_time - self.attack_time >= self.attack_cooldown:
            self.attacking = False
            self.destroy_attack()
        if current_time - self.switch_time >= self.switch_cooldown:
            self.switch_weapon = False
        if current_time - self.magic_switch_time >= self.switch_cooldown:
            self.switch_magic = False
        if current_time - self.hurt_time >= self.invulnerability_duration:
            self.vulnerable = True
            self.invulnerability_duration = 500
    def animate (self):
        animation = self.animations[self.status]
        #loop over the frame index
        self.frame_index += self.animations_speed
        if self.frame_index >= len (self.animations[self.status]):
            self.frame_index = 0
        #set the image 
        self.image = animation [int (self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)
        #flicker 
        if not self.vulnerable:
            alpha = self.wave_value ()    
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.attack 
        weapon_damage = weapon_data [self.weapon]["damage"]
        return weapon_damage + base_damage
    def get_full_magic_damage (self):
        base_damage = self.stats["magic"]
        spell_damage = magic_data [self.magic]['strength']
        return base_damage + spell_damage
    def get_value_by_index (self, index):
        return list(self.stats.values())[index]
    def get_cost_by_index (self,index):
        return list(self.upgrade_cost.values())[index]
    def magic_overtime (self):
        self.energy += 0.5 #0.01 * self.stats["magic"]
        if self.energy >= self.stats["energy"]:
            self.energy = self.stats["energy"]

             
    def update(self):
        self.input()
        self.cooldown()
        self.get_status()
        self.move(self.stats['speed']) 
        self.magic_overtime()
        self.animate()
    
          
