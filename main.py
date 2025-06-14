#######################
###IMPORTS
#######################

# general imports
import pygame

from importlib.metadata import version
print(version('qiskit'))

from pygame.locals import (
    K_ESCAPE,
    K_SPACE,
    K_b,
    K_v,
    K_s,
    K_m,
)

# game files
import constants #all "global variables" are stored there
from game_constants import character, enemy #data about char/enemy and thier stats
from ui import * #all visual part
from dialogs import dialog_sequences #dictionary with all dialogs
from game_logic import * #managing player's actions and AI responses


#######################
###GAME INIT
#######################
pygame.init()
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Quantum faceoff: superposition tactics")
clock = pygame.time.Clock()


#######################
###PATHS AND ASSETS LOADING
#######################

from assets import load_assets
assets = load_assets()

# getting all to constants, and all will be called from there
# hero animators
constants.hero_idle_animator = assets["hero_idle_animator"]
constants.hero_attack_animator = assets["hero_attack_animator"]
constants.hero_defend_animator = assets["hero_defend_animator"]
constants.hero_heal_animator = assets["hero_heal_animator"]
constants.hero_death_animator = assets["hero_death_animator"]
# hero attack effect
constants.attack_effect_animator = assets["attack_effect_animator"]

# enemy animators
constants.enemy_idle_animator = assets["enemy_idle_animator"]
constants.enemy_attack_animator = assets["enemy_attack_animator"]
constants.enemy_defend_animator = assets["enemy_defend_animator"]
constants.enemy_heal_animator = assets["enemy_heal_animator"]
constants.enemy_charge_animator = assets["enemy_charge_animator"]
constants.enemy_death_animator = assets["enemy_death_animator"]

# portraits for status bar
constants.portrait = assets["portrait"]
constants.enemy_portrait = assets["enemy_portrait"]

# backgrounds
constants.background = assets["background"] #default
constants.background_2 = assets["background_2"] # good ending

# icons for buttons
constants.lock_icon = assets["lock_icon"]
constants.arrow_icon = assets["arrow_icon"]

#######################
###PRE-GAME INITS
#######################

# function to dynamically switch OSTs
def play_music(track, loop=-1, fade_ms=2000):
    pygame.mixer.music.fadeout(1000)
    pygame.mixer.music.load(assets[track])
    constants.current_music_track = track
    pygame.mixer.music.play(loop, fade_ms=fade_ms)
    
    #track is playing but without volume, so continues when unmuted, not pauses
    if constants.music_muted:
        pygame.mixer.music.set_volume(0.0)
    else:
        pygame.mixer.music.set_volume(1.0)


# dialog box
textbox = TextBox(
    screen=screen,
    font=pygame.font.Font(None, 28),
    name_font=constants.name_font,
    box_rect=constants.box_rect
)

current_sequence = dialog_sequences["intro"] #selects dialog sequence from dialogs.py (herein initial)
textbox.set_text(current_sequence[0]["name"], current_sequence[0]["text"]) # name - of a speaker, text - of a speaker

# currently rendered sprites for player. Initially in idle mode
constants.current_animator = constants.hero_idle_animator
constants.enemy_current_animator = constants.enemy_idle_animator

# intro OST
play_music("intro")

# creating buttons (gate buttons, qubit buttons, apply/end turn buttons, and arrow pagination)
register_gate_callback(set_gate)
create_gate_buttons()
create_qubit_buttons(set_qubit)
create_control_buttons(confirm_gate_application, start_enemy_turn)
slider = create_param_slider(set_param)

# the main loop itself, driver of the game
running = True
while running:
    for event in pygame.event.get():
        mouse_pos = pygame.mouse.get_pos()
        
        #buttons/slider are available only in battle, so checking them there
        if constants.game_state == "battle":
            for btn in constants.buttons:
                btn.handle_event(event, mouse_pos)
            slider.handle_event(event)

        # game end event
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            #SPACE is used to iterate through the dialogs, and close in-battle notifications
            if event.key == pygame.K_SPACE:
                if constants.dialog_flag:
                    current_sequence, constants.dialog_index, textbox, constants.dialog_flag = handle_dialogue_advance(
                        current_sequence, constants.dialog_index, textbox, constants.dialog_flag
                    )
                elif constants.game_state == "show_enemy_log":
                    complete_enemy_turn()
                elif constants.show_player_log:
                    constants.player_action_log.clear()
                    constants.show_player_log = False


                        ####TECHNICAL BUTTON, CONSOLE PRINTS ALL MAIN VARIABLES FOR DEBUGGING
            elif event.key == pygame.K_s:
                #print(constants.current_animator)
                print("Game state flag:", constants.game_state)
                print("Game phase flag:", constants.boss_phase)
                print("Player dead flag:", constants.player_dead)
                print("Currently selected gate:", constants.selected_gate)
                print("Currently selected qubit:", constants.selected_qubit)

                print("Player defence bonus:", constants.player_defence_bonus)
                print("Enemy attack multiplier:", constants.enemy_attack_multiplier)
                print("Enemy defence bonus:", constants.enemy_defence_bonus)
                print("<---CHAR STATS--->")
                print(character)
                print("<---ENEMY STATS--->")
                print(enemy)

            ####MUTE/UNMUTE OST
            elif event.key == pygame.K_m:
                constants.music_muted = not constants.music_muted
                
                if constants.music_muted:
                    pygame.mixer.music.set_volume(0.0)
                else:
                    pygame.mixer.music.set_volume(1.0)

            #exiting the game on win/lose via ESCAPE button
            elif event.key == pygame.K_ESCAPE and (constants.game_state == "done" or constants.game_state == "lost"):
                running = False
            ####TECHNICAL BUTTON, REDUCES ENEMY'S HP BY 10
            ####IF NEED TO SEE GOOD ENDING WITHOUT BEATING THE GAME - UNCOMMENT AND USE IT
            
            ''' 
            elif event.key == pygame.K_b and constants.game_state == "battle":
                print(get_player_string())
                enemy["hp"] -= 10
                #print(f"Enemy HP: {enemy['hp']}")
            '''
            ####TECHNICAL BUTTON, REDUCES PLAYER'S HP BY 10
            ''' 
            elif event.key == pygame.K_v and constants.game_state == "battle":
                print(get_player_string())
                if(character["hp"] - 10 > 0):
                    character["hp"] -= 10
                    print(f"Charecter HP: {character['hp']}")
            ''' 

            
    #gray background for the infopanel at the bottom of the screen. Always rendered in any game state.
    pygame.draw.rect(screen, constants.GRAY, (0, constants.SCREEN_HEIGHT - constants.INFO_PANEL_HEIGHT, constants.SCREEN_WIDTH, constants.INFO_PANEL_HEIGHT))

    # draw background for the whole game and bad ending
    if constants.post_dialog_state != "done":
        screen.blit(constants.background, (0, 0))
    
    else:
        #when game is won (good ending), change the background by nicely fading the old
        if not constants.has_transitioned:
            for i in range(constants.fade_steps + 1):
                alpha = int(255 * i / constants.fade_steps)
                constants.background_2.set_alpha(alpha)
                screen.blit(constants.background, (0, 0))
                screen.blit(constants.background_2, (0, 0))

                #char/enemy are presented both still
                draw_hero(screen, clock)
                draw_enemy(screen, clock)
                               
                pygame.display.flip()
                pygame.time.delay(30) #making the transition bit longer
            constants.has_transitioned = True #protector from looping the transition between backgrounds
        else:
            screen.blit(constants.background_2, (0, 0))

    # update textbox animation (only relevant in dialog phases)
    if constants.game_state in ["dialog_intro", "dialog_outro"]:
        textbox.update()


    #######################
    ###MAIN GAME STATES HANDLING
    ### dialog_intro - opening scene for a game
    ### battle - main gameplay part
    ### dialog_outro - used to trigger dialog boxes during boss phase transition, during the game, and for the final dialogs
    ### done - game over for good ending
    ### lost - game over for bad ending
    #######################

    # opening scene for a game
    if constants.game_state == "dialog_intro":
        
        #char/enemy are presented both
        draw_hero(screen, clock)
        draw_enemy(screen,clock)

        #showing the dialog box itself
        textbox.draw()

        if not constants.dialog_flag:
            constants.game_state = "battle"  # transition to battle
            play_music("battle_1")   # turning on battle OST

    # battle stage. starts by default in phase 1
    elif constants.game_state == "battle":

        #char/enemy are presented both
        draw_hero(screen, clock)
        draw_enemy(screen,clock)

        # draw attack effect if it is triggered
        if constants.show_attack_effect:

            # moving sprite of attack effect towards the enemy
            constants.attack_effect_pos[0] += 10  # speed in pixels per frame
            constants.attack_effect_animator.pos = tuple(constants.attack_effect_pos)

            constants.attack_effect_animator.update(clock.get_time())
            constants.attack_effect_animator.draw(screen)

            # after reaching the enemy/time - dissapearing
            if constants.attack_effect_pos[0] >= constants.SCREEN_WIDTH * 0.75 or pygame.time.get_ticks() - constants.attack_effect_timer > 900:
                constants.show_attack_effect = False

        #char/enemy stats are drawn in the info panel
        draw_info_box(screen, *char_box_pos, character, constants.portrait, show_qp=True)
        draw_info_box(screen, *enemy_box_pos, enemy, constants.enemy_portrait, show_qp=False) #boss does not have QP at all, it is considered infinite
        
        #draw current superposition
        draw_statevector_box(screen, constants.quatum_state, 20, 20, constants.turns_remaining_until_measurement)

        #draw all buttons and sliders
        for btn in constants.buttons:
            btn.draw(screen)
        slider.draw(screen)

        #draw box with user error if QP is not enough to apply the gate
        if constants.show_player_log and constants.player_action_log:
            draw_enemy_action_log(screen, constants.player_action_log) #just the same function adapted to the user's error messages

        # texts shown after the superposition collaplsed - with applied action
        constants.player_floating_texts = [t for t in constants.player_floating_texts if t.draw(screen)]
        constants.enemy_floating_texts = [t for t in constants.enemy_floating_texts if t.draw(screen)]


        #starting phase 2 on 70% of boss health and below
        if constants.boss_phase == 1 and enemy["hp"] <= enemy["max_hp"] * 0.7:
            
            
            constants.boss_phase = 2

            #phase 2 OST
            play_music("battle_2")

            #new time intervals for measurements
            constants.measurement_turns_count = 2
            constants.turns_remaining_until_measurement = 2

            #re-drawing gates, as there going to be changes depending on the phase of the boss
            create_gate_buttons()
            
            # setting dialog to be played before the phase 2
            current_sequence = dialog_sequences["phase2"]
            constants.dialog_index = 0
            textbox.set_text(current_sequence[0]["name"], current_sequence[0]["text"])
            constants.dialog_flag = True
            constants.post_dialog_state = "battle" #after dialog back to the battle
            constants.game_state = "dialog_outro" #trigger in-battle dialog

        #starting phase 3 on 40% of boss health and below
        elif constants.boss_phase == 2 and enemy["hp"] <= enemy["max_hp"] * 0.4:

        
            constants.boss_phase = 3

            #phase 3 OST
            play_music("battle_3")

            #re-drawing gates, as there going to be changes depending on the phase of the boss
            create_gate_buttons()

            #new time intervals for measurements
            constants.measurement_turns_count = 3
            constants.turns_remaining_until_measurement = 3

            # setting dialog to be played before the phase 2
            current_sequence = dialog_sequences["phase3"]
            constants.dialog_index = 0
            textbox.set_text(current_sequence[0]["name"], current_sequence[0]["text"])
            constants.dialog_flag = True
            constants.post_dialog_state = "battle" #after dialog back to the battle
            constants.game_state = "dialog_outro" #trigger in-battle dialog

        # enemy defeated (actually boss_phase check is not necessary)
        elif constants.boss_phase == 3 and enemy["hp"] <= 0 and not constants.final_dialog_shown:

            # setting the endgame dialog
            current_sequence = dialog_sequences["final"]
            constants.dialog_index = 0
            textbox.set_text(current_sequence[0]["name"], current_sequence[0]["text"])
            constants.dialog_flag = True

            constants.post_dialog_state = "done" #after to good ending finish

            #ending OST
            play_music("outro") 

            enemy["hp"] = 0 # was used for status bar not to go into minus, but can be removed. Has potential application for enemy "revival" and another phase
            
            #playing death animation
            constants.enemy_current_animator = constants.enemy_death_animator
            constants.final_dialog_shown = True
            
            constants.game_state = "enemy_death" #switches for the last dialog and corresponding sprites

    #in-battle dialogue handling
    elif constants.game_state == "dialog_outro":

        #char/enemy are presented both
        draw_hero(screen, clock)
        draw_enemy(screen,clock)

        #showing the dialog box itself
        textbox.draw()
        if not constants.dialog_flag:
            constants.game_state = constants.post_dialog_state

    #the end-game screen for a good ending
    elif constants.game_state == "done":
        end_text = constants.font_bold.render("The End. Press ESC to quit.", True, constants.WHITE)
        screen.blit(end_text, (constants.SCREEN_WIDTH // 2 - end_text.get_width() // 2, constants.SCREEN_HEIGHT // 2))

    # display in-battle messages
    elif constants.game_state == "show_enemy_log":
        
        #full screen re-draw with all in-battle elements + draw_enemy_action_log()
        screen.blit(constants.background, (0, 0))
        draw_hero(screen, clock)
        draw_enemy(screen,clock)
        draw_info_box(screen, *char_box_pos, character, constants.portrait, show_qp=True)
        draw_info_box(screen, *enemy_box_pos, enemy, constants.enemy_portrait, show_qp=False)
        draw_enemy_action_log(screen, constants.enemy_action_log)
        draw_statevector_box(screen, constants.quatum_state, 20, 20, constants.turns_remaining_until_measurement)

    #player is killed
    elif constants.game_state == "player_death":
        play_music("lost")
        #play char death animation
        if constants.current_animator != constants.hero_death_animator:
            constants.current_animator = constants.hero_death_animator

        if constants.current_animator.frame_index < len(constants.current_animator.frames) - 1:
            constants.current_animator.update(clock.get_time())
        #freeze on last frame

        screen.blit(constants.background, (0, 0))

        # render animation
        constants.current_animator.draw(screen)
        
        constants.enemy_charge_start_time = draw_enemy(screen,clock)

        draw_info_box(screen, *char_box_pos, character, constants.portrait, show_qp=True)
        draw_info_box(screen, *enemy_box_pos, enemy, constants.enemy_portrait, show_qp=False)
        draw_statevector_box(screen, constants.quatum_state, 20, 20, constants.turns_remaining_until_measurement)

        # after animation show last dialog
        if constants.current_animator.frame_index == len(constants.current_animator.frames) - 1:
            constants.dialog_index = 0
            current_sequence = dialog_sequences["game_lost"]
            textbox.set_text(current_sequence[0]["name"], current_sequence[0]["text"])
            constants.dialog_flag = True
            constants.post_dialog_state = "lost"
            constants.game_state = "dialog_outro"

    #the end-game screen for a bad ending
    elif constants.game_state == "lost":
        screen.fill(constants.BLACK)

        end_text = constants.font_bold.render("Game Over. Press ESC to quit.", True, constants.WHITE)
        screen.blit(end_text, (constants.SCREEN_WIDTH // 2 - end_text.get_width() // 2, constants.SCREEN_HEIGHT // 2))


    elif constants.game_state == "enemy_death":

        constants.enemy_current_animator = constants.enemy_death_animator
        if constants.enemy_current_animator.frame_index < len(constants.enemy_current_animator.frames) - 1:
            constants.enemy_current_animator.update(clock.get_time())
        # else: do nothing — freeze on last frame

        screen.blit(constants.background_2, (0, 0))  # final phase background assumed

        #idle for char
        constants.current_animator.draw(screen)

        #death animation for the enemy
        constants.enemy_current_animator.draw(screen)

        # (screen, *char_box_pos, character, portrait, show_qp=True)
        #draw_info_box(screen, *enemy_box_pos, enemy, enemy_portrait, show_qp=False)
        #draw_statevector_box(screen, constants.quatum_state, 20, 20, constants.turns_remaining_until_measurement)

        #set last dialog for good ending
        if constants.enemy_current_animator.frame_index == len(constants.enemy_current_animator.frames) - 1:
            current_sequence = dialog_sequences["final"]
            constants.dialog_index = 0
            textbox.set_text(current_sequence[0]["name"], current_sequence[0]["text"])
            constants.dialog_flag = True
            constants.post_dialog_state = "done"
            constants.game_state = "dialog_outro"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()