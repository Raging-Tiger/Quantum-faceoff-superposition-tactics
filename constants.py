import pygame
from quantum import *

#######################
###DESPITE NAME, HERE STORED NOT ONLY GAME CONSTANTS 
###BUT ALL GLOBAL VARS THAT ARE CHANGED DURING GAME PROCESS
#######################


#######################
###SCREEN AND DIALOG BOX, BUTTONS, ETC. DIMENSIONS
#######################
INFO_PANEL_HEIGHT = 160
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720 + INFO_PANEL_HEIGHT

TEXT_BOX_WIDTH = 700
TEXT_BOX_HEIGHT = 180

# dialog text box screen position
dialog_box_x = (SCREEN_WIDTH - TEXT_BOX_WIDTH) // 2
dialog_box_y = SCREEN_HEIGHT - TEXT_BOX_HEIGHT - 20  # 20px margin from bottom
box_rect = pygame.Rect(dialog_box_x, dialog_box_y, TEXT_BOX_WIDTH, TEXT_BOX_HEIGHT)


# gate buttons
button_width = 60
button_height = 40
button_spacing = 20

num_buttons = 4  # gate or qubit row
total_row_width = num_buttons * button_width + (num_buttons - 1) * button_spacing
buttons_start_x = 20

# buttons positioning
start_y_gate = SCREEN_HEIGHT - INFO_PANEL_HEIGHT + 10
start_y_qubit = start_y_gate + button_height + 10

# control buttons positioning
apply_y = start_y_qubit + button_height + 15
end_x = SCREEN_WIDTH // 2 + 10

#######################
###COLORS
#######################
GRAY = (50, 50, 50)
DARK_GRAY = (30, 30, 30)
DARK_GRAY_2 = (60, 60, 60)
DIM_GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
LIGHT_GREEN = (0, 180, 0)
LIGHT_BLUE = (100, 200, 255)
YELLOWISH = (200, 200, 50)


#######################
###FONTS
#######################
pygame.font.init()
font = pygame.font.SysFont(None, 28)
font_bold = pygame.font.SysFont(None, 28, bold=True)
name_font = pygame.font.SysFont('arial', 28, bold=True)


#######################
###VARIOUS CONTROL FLAGS / VARIABLES
#######################

dialog_flag = True #is dialog active
boss_phase = 1  # start at phase 1
post_dialog_state = None #to what state transition after the dialog

#backgrounds smooth changing
has_transitioned = False #screen transition
fade_steps = 30

#measurement and collapse counters
measurement_turns_count = 1 #initial setup
turns_remaining_until_measurement = 1

# opening dialog sequence init
# game_state is defining actions based on the game state. 
# available states: dialog_intro (opening dialog), battle (including 3 stages), dialog_outro (used for dialog IN battle and after a battle), done (the end screen)
game_state = "dialog_intro" #initial state
dialog_index = 0 # starting with the first dialog entry
dialog_flag = True 
#battle_over = False #TECH - to check battle end without battle
final_dialog_shown = False
player_dead = False

#for used action (gates, qubit, angle)
selected_gate = None
selected_qubit = None
selected_gate_button = None
selected_qubit_button = None
selected_param = 0
buttons = []
buttons = []
gate_set_callback = None

# create gate buttons UI for player
gates = ["I", "X", "H", "Z"]
all_gates = ["I", "X", "H", "Z", "RX", "RY", "RZ", "S", "T"]
gate_page = 0  # page index for rotating gate sets

# set quantum state for battle
quatum_state = QuantumState()
last_measurement = "0000"


#for printing out enemy action
#ENEMY_ACTION_STATE = "enemy_action"
enemy_action_log = []



player_action_log = [] #for errors display
show_player_log = False

#player/enemy action display
player_floating_texts = []
enemy_floating_texts = []

#for defence/attack stacking (modifyers)
player_defence_bonus = 0.0

enemy_attack_multiplier = 1.0  # accumulates with idle
enemy_defence_bonus = 0.0      



#######################
###ANIMATORS AND IMAGE ASSETS STORING
#######################

# char's
hero_idle_animator = None
hero_attack_animator = None
hero_defend_animator = None
hero_heal_animator = None
hero_death_animator = None
# char's attack effect
attack_effect_animator = None

# enemy
enemy_idle_animator = None
enemy_attack_animator = None
enemy_defend_animator = None
enemy_heal_animator = None
enemy_charge_animator = None
enemy_death_animator = None

# portraits for stats boxes
portrait = None
enemy_portrait = None

# backgrounds
background = None #default and bad ending
background_2 = None #good ending only

# icons for buttons
lock_icon = None
arrow_icon = None

#MAJOR PART OF ANIMATION
current_animator = None #current sprite for the char
enemy_current_animator = None #current sprite for the enemy

#######################
###ANIMATION'S PLAYTIME SETTING (IF NOT LOOPED)
#######################

attack_start_time = None
defend_start_time = None
heal_start_time = None
enemy_attack_start_time = None
enemy_defend_start_time = None
enemy_heal_start_time = None
enemy_charge_start_time = None

show_attack_effect = False
attack_effect_timer = None
attack_effect_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT - INFO_PANEL_HEIGHT * 2 - 100]  

#######################
###OST MUTE/UNMUTE
#######################
music_muted = False
current_music_track = None  #for debug mostly