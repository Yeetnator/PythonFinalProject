from csv import reader
from os import walk
import pygame
def import_csv_layout(path):
    terrain_map = []
    with open (path) as level_map:
        layout = reader(level_map, delimiter= ",")
        for row in layout: 
            terrain_map.append(list(row))
    return terrain_map
def import_folder(path):
    surface_list = []
    for _,__,img_files in walk(path):
       for image in img_files:
        full_path = path + '/' + image
        image_surf = pygame.image.load(full_path).convert_alpha()
        surface_list.append(image_surf)
    return surface_list 
def import_check(path):
   surface1_list = []
   for _,__,img_files in walk(path):
    img_files = sorted(img_files, key = lambda x: int (x.split(".")[0]))
    for image in img_files:
        full_path = path + '/' + image
        image_surf = pygame.image.load(full_path).convert_alpha()
        surface1_list.append(image_surf)
    return surface1_list 
def import_r(path):
    for _,__,img_files in walk(path):
       print (img_files)

