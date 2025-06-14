
#here assets from the assets folder parsed and loaded
import pygame
import os
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, INFO_PANEL_HEIGHT, button_width, button_height
from ui import SpriteAnimator

#######################
###IS CALLED ONCE ON MAIN.PY INIT STAGE
###LATER ALL REFERENCES TO ANIMATORS, ETC. ARE STORED IN CONSTANTS.PY AND CALLED FROM THERE
#######################

def load_assets():

    pygame.mixer.init() #for in-game OST

    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(current_dir, "assets") #relative path to assets folder

    assets = {} # storing all assets as named dictionary

    # all music
    battle_music_path_3 = os.path.join(assets_dir, "battle_3.mp3")
    #pygame.mixer.music.load(battle_music_path_3)
    assets["battle_3"] = battle_music_path_3

    battle_music_path_1 = os.path.join(assets_dir, "battle_1.mp3")
    assets["battle_1"] = battle_music_path_1
    battle_music_path_2 = os.path.join(assets_dir, "battle_2.mp3")
    assets["battle_2"] = battle_music_path_2
    intro_music_path = os.path.join(assets_dir, "intro.mp3")
    assets["intro"] = intro_music_path
    outro_music_path = os.path.join(assets_dir, "outro.mp3")
    assets["outro"] = outro_music_path
    lost_music_path = os.path.join(assets_dir, "lost.mp3")
    assets["lost"] = lost_music_path

    # icons for buttons
    lock_icon = pygame.image.load(os.path.join(assets_dir, "lock.png"))
    assets["lock_icon"] = pygame.transform.scale(lock_icon, (button_width - 20, button_height - 10))

    arrow_icon = pygame.image.load(os.path.join(assets_dir, "arrow.png"))
    assets["arrow_icon"] = pygame.transform.scale(arrow_icon, (button_width - 20, button_height - 10))

    # backgrounds & scaling
    bg1 = pygame.image.load(os.path.join(assets_dir, "background.png")) 
    bg2 = pygame.image.load(os.path.join(assets_dir, "background_2.png")) # background for good ending
    assets["background"] = pygame.transform.scale(bg1, (SCREEN_WIDTH, SCREEN_HEIGHT - INFO_PANEL_HEIGHT))
    assets["background_2"] = pygame.transform.scale(bg2, (SCREEN_WIDTH, SCREEN_HEIGHT - INFO_PANEL_HEIGHT))

    # char & enemy portraits for status bar (during the battle)
    mage = pygame.image.load(os.path.join(assets_dir, "mage.png"))
    mage_2 = pygame.image.load(os.path.join(assets_dir, "mage_2.png"))
    assets["portrait"] = pygame.transform.scale(mage, (64, 64))
    assets["enemy_portrait"] = pygame.transform.scale(mage_2, (64, 64))

    # all sprites used for animation
    def load(path):
        #return pygame.transform.flip(pygame.image.load(os.path.join(assets_dir, path)).convert_alpha(), True, False)
        return pygame.image.load(os.path.join(assets_dir, path)).convert_alpha()
    
    # all hero sprites
    assets["hero_idle"] = load("Idle.png")
    assets["hero_attack"] = load("Attack_1.png")
    assets["hero_defend"] = load("Attack_2.png")
    assets["hero_heal"] = load("Magic_sphere.png")
    assets["hero_death"] = load("Dead.png")
    assets["attack_effect"] = load("Charge_1.png")

    # all enemy sprites
    assets["enemy_idle"] = load("Idle_enemy.png")
    assets["enemy_attack"] = load("Attack_1_enemy.png")
    assets["enemy_defend"] = load("Hurt_enemy.png")
    assets["enemy_heal"] = load("Light_ball_enemy.png")
    assets["enemy_charge"] = load("Attack_2_enemy.png")
    assets["enemy_death"] = load("Dead_enemy.png")

    # hero positioning
    char_pose = (SCREEN_WIDTH / 5, SCREEN_HEIGHT - INFO_PANEL_HEIGHT * 1.6 - int(assets["hero_idle"].get_height() * 1.5) - 10)
    
    # enemy positioning
    enemy_pos = (SCREEN_WIDTH / 1.5, SCREEN_HEIGHT - INFO_PANEL_HEIGHT*1.6 - int(assets["hero_idle"].get_height() * 1.5) - 10)

    # hero animators
    assets["hero_idle_animator"] = SpriteAnimator(assets["hero_idle"], 8, char_pose, scale=1.5)
    assets["hero_attack_animator"] = SpriteAnimator(assets["hero_attack"], 7, char_pose, scale=1.5)
    assets["hero_defend_animator"] = SpriteAnimator(assets["hero_defend"], 9, char_pose, scale=1.5)
    assets["hero_heal_animator"] = SpriteAnimator(assets["hero_heal"], 16, char_pose, scale=1.5)
    assets["hero_death_animator"] = SpriteAnimator(assets["hero_death"], 4, char_pose, frame_delay=400, scale=1.5, loop=False) #death animation should not be looped

    # hero attack effect animator
    assets["attack_effect_animator"] = SpriteAnimator(assets["attack_effect"], 9, pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - INFO_PANEL_HEIGHT * 2), scale=1.5)

    # enemy animators
    assets["enemy_idle_animator"] = SpriteAnimator(assets["enemy_idle"], 7, enemy_pos, scale=1.5, flip=True)
    #only animator with different positioning
    assets["enemy_attack_animator"] = SpriteAnimator(assets["enemy_attack"], 10, (SCREEN_WIDTH / 5 + 50, 
                                                                                  SCREEN_HEIGHT - INFO_PANEL_HEIGHT*1.6 - int(assets["hero_attack"].get_height() * 1.5) - 10), 
                                                                                  scale=1.5, flip=True)
    assets["enemy_heal_animator"] = SpriteAnimator(assets["enemy_heal"], 7, enemy_pos, scale=1.5, flip=True)
    assets["enemy_defend_animator"] = SpriteAnimator(assets["enemy_defend"], 3, enemy_pos, frame_delay=400, scale=1.5, flip=True)
    assets["enemy_charge_animator"] = SpriteAnimator(assets["enemy_charge"], 4, enemy_pos, frame_delay=200, scale=1.5, flip=True)
    assets["enemy_death_animator"] = SpriteAnimator(assets["enemy_death"], 5, enemy_pos, frame_delay=400, scale=1.5, loop=False, flip=True)

    return assets
