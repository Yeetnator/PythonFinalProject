import pygame
from settings import *
from support import *
from entity import Enitity

class Enemy (Enitity):
    def __init__(self, monster_name,pos, groups, obstacle_sprite, parameter, trigger_death_particle, add_xp):
        super().__init__(groups)
        self.sprite_type = "enemy"
        #graphics setup
        self.import_graphics(monster_name)
        self.status = "idle"
        self.image = self.animations[self.status][self.frame_index]
        #movement 
        self.rect = self.image.get_rect (topleft = pos)
        self.hitbox = self.rect.inflate (0,-10)
        self.obstacle_sprite = obstacle_sprite
        #stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']
        #player interaction
        self.can_attack = True
        self.attacking = 0
        self.can_attack_cooldown = 400
        self.damage_player = parameter
        self.trigger_death_particles = trigger_death_particle
        self.add_xp = add_xp
        #invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 400
        #sounds
        self.attack_sound  = pygame.mixer.Sound (monster_info["attack_sound"])
        self.death_sound = pygame.mixer.Sound("Documents/Zelda-main/1-level/audio/death.wav")
        self.hit_sound = pygame.mixer.Sound("Documents/Zelda-main/1-level/audio/hit.wav")
        self.death_sound.set_volume (0.2)
        self.hit_sound.set_volume (0.2)
    def import_graphics(self,name):
        self.animations = {'idle': [], 'move': [], 'attack':[]}
        main_path = f"Documents/Zelda-main/1-level/graphics/monsters/{name}/"
        for animations in self.animations.keys():
            self.animations[animations] = import_folder (main_path + animations)
    def get_status (self, player):
        distance = self.get_player_distance_direction(player)[0]
        if distance <= self.attack_radius and self.can_attack :
            if self.status != "attack":
                self.frame_index = 0 
            self.status = "attack"
        elif distance <= self.notice_radius:
            self.status = "move"
        else:
            self.status = "idle"
    def actions(self,player):
        if self.status == "attack":
            self.attacking = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_sound.set_volume(0.2)
            self.attack_sound.play()
        elif self.status == "move":
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()
    def animate (self):
        animation = self.animations[self.status]
        self.frame_index += self.animations_speed
        if self.frame_index >= len (self.animations[self.status]):
            if self.status == "attack":
                self.can_attack = False
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect (center = self.hitbox.center)
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha (alpha)
        else:
            self.image.set_alpha (255)
        
    def get_damage (self, player, attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            if attack_type == "weapon":
                self.health -= player.get_full_weapon_damage ()
            else:
                self.health -= player.get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False
        
    def check_health (self):
        if self.health <= 0:
            offset = pygame.math.Vector2(34,34)
            self.trigger_death_particles(self.rect.topleft + offset, self.monster_name )
            self.kill()
            self.death_sound.play()
            self.add_xp(self.exp)

    def cooldown (self):
        current_time = pygame.time.get_ticks() 
        if not self.can_attack:
            if current_time - self.attacking >= self.can_attack_cooldown:
                self.can_attack = True
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True
    def hit_reaction (self):
        if not self.vulnerable:
            self.direction = -(self.direction * self.resistance)

    def update (self):
        self.hit_reaction ()
        self.move(self.speed)
        self.animate()
        self.cooldown()
        self.check_health()
    def enemy_update (self,player):
        self.get_status(player)
        self.actions (player)