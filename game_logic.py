import random
import math
from numpy import pi
import pygame

import constants
from game_constants import character, enemy, player_action_map, player_gates_cost, player_stats, enemy_stats
from ui import FloatingText


# retireve player's qubit part of the evaluation |xx??>
def get_player_string():
    player_string = constants.last_measurement[:2]
    return player_string

# retireve enemy's qubit part of the evaluation |??yy>
def get_enemy_string():
    enemy_string = constants.last_measurement[-2:]
    return enemy_string

#######################
###PLAYER ACTION TRIGGERED ONLY AFTER MEASURING CURRENT SUPERPOSITION AND FOLLOWING COLLAPSING
#######################
def player_action():
    #getting player's part of observation
    outcome = get_player_string()

    #selecting action based on the measurement
    action = player_action_map.get(outcome, "idle")

    # IDLE - player does nothing
    if action == "idle":
        constants.player_floating_texts.append(FloatingText("Idle", (constants.SCREEN_WIDTH / 4 + 20, 630)))
        pass
        
        #character["qp"] += 10
        #current_animator = hero_idle_animator

    # ATTACK - deals attack according to modifiers, sets necessary animation
    elif action == "attack":
        
        
        constants.current_animator = constants.hero_attack_animator
        constants.attack_effect_pos[0] = constants.SCREEN_WIDTH // 4  # reset to starting x pos
        constants.attack_effect_animator.pos = tuple(constants.attack_effect_pos)

        constants.show_attack_effect = True
        constants.attack_effect_timer = pygame.time.get_ticks()
        constants.attack_start_time = pygame.time.get_ticks()

        damage = player_stats["normal_attack"]

        #player's attack doubled during the last phase
        if constants.boss_phase == 3:
            damage = player_stats["last_phase_attack"]

        if constants.enemy_defence_bonus > 0:
            damage *= max(0, 1 - constants.enemy_defence_bonus)
            constants.enemy_defence_bonus = 0.0  # reset enemy defence bonuses after taking damage
        enemy["hp"] -= damage

        #helper message for player to see what actually was done. Appears roughly under the sprite of the char
        constants.player_floating_texts.append(FloatingText("Attack", (constants.SCREEN_WIDTH / 4 + 20, 630)))
    
    # DEFEND - deals stacks defence for the player, sets necessary animation
    elif action == "defend":
        
        #stacking defence
        if constants.player_defence_bonus != 1.0:
            constants.player_defence_bonus += player_stats["defence"] / 100

        constants.current_animator = constants.hero_defend_animator
        constants.defend_start_time = pygame.time.get_ticks()
        constants.player_floating_texts.append(FloatingText("Defend", (constants.SCREEN_WIDTH / 4 + 20, 630)))

    
     # HEAL - heals set number of HP (cannot go over cap), sets necessary animation
    elif action == "heal":

        constants.current_animator = constants.hero_heal_animator
        constants.heal_start_time = pygame.time.get_ticks()

        character["hp"] = min(character["hp"] + 10, character["max_hp"])
       
        constants.player_floating_texts.append(FloatingText("Heal", (constants.SCREEN_WIDTH / 4 + 20, 630)))

#######################
###PLAYER ACTION EFFECT IS TRIGGERED ONLY AFTER MEASURING CURRENT SUPERPOSITION AND FOLLOWING COLLAPSING
#######################
def enemy_action_effect():
    
    #getting enemy's part of observation
    outcome = get_enemy_string()
    #I use the same linking for results as it is the same for the enemy as for player, yet effects can be different
    action = player_action_map.get(outcome, "idle")

    # ATTACK - deals attack according to modifiers, sets necessary animation
    if action == "attack": 
        constants.enemy_current_animator = constants.enemy_attack_animator
        constants.enemy_attack_start_time = pygame.time.get_ticks()

        # base attack of the enemy depends on the phase
        damage = enemy_stats["base_attack"].get(constants.boss_phase, 10)
        damage *= constants.enemy_attack_multiplier

        #  player defence modifiers
        if constants.player_defence_bonus > 0:
            damage *= max(0, 1 - constants.player_defence_bonus)
            constants.player_defence_bonus = 0

        character["hp"] -= round(damage)

        # reset attack multiplier for the enemy after the attack
        constants.enemy_attack_multiplier = 1.0

        # if attack killed player, sets HP for 0 and game state as player_death, leading to game over event sequence
        if character["hp"] <= 0:
            character["hp"] = 0
            constants.player_dead = True
            constants.game_state = "player_death"
        
        constants.enemy_floating_texts.append(FloatingText("Attack", (constants.SCREEN_WIDTH / 1.5 + 50, 630)))
    
    # IDLE - unlike player, the enemy chages up the attack when idle. Can stack.
    elif action == "idle":
        constants.enemy_current_animator = constants.enemy_charge_animator
        constants.enemy_charge_start_time = pygame.time.get_ticks()
        
        constants.enemy_attack_multiplier += enemy_stats["attack_charge_per_idle"]
        constants.enemy_floating_texts.append(FloatingText("Charging up", (constants.SCREEN_WIDTH / 1.5 + 50, 630)))

    # HEAL - heals set number of HP (cannot go over cap), sets necessary animation
    elif action == "heal":
        constants.enemy_current_animator = constants.enemy_heal_animator
        constants.enemy_heal_start_time = pygame.time.get_ticks()
        enemy["hp"] = min(enemy["hp"] + enemy_stats["heal"], enemy["max_hp"])
        constants.enemy_floating_texts.append(FloatingText("Heal", (constants.SCREEN_WIDTH / 1.5 + 50, 630)))

    # DEFEND - deals stacks defence for the player, sets necessary animation
    elif action == "defend":
        constants.enemy_current_animator = constants.enemy_defend_animator
        constants.enemy_defend_start_time = pygame.time.get_ticks()

        constants.enemy_defence_bonus = min(constants.enemy_defence_bonus + enemy_stats["defence_increase"], enemy_stats["max_defence"])
        constants.enemy_floating_texts.append(FloatingText("Defend", (constants.SCREEN_WIDTH / 1.5 + 50, 630)))

#######################
###AFTER EACH TURN THE ENEMY IS USING SOME QUANTUM GATES, DEPENDING ON THE PHASE OF THE BALLTE
#######################
def enemy_action():
    
    #print("ENEMY turn ends here")

    #keep qubits in such way that they were used in direct order
    reverse_list = [3, 2, 1, 0]

    # if PHASE 1, the enemy can use only 1 gate per turn
    # Eligible gates are X, H, I only
    if constants.boss_phase == 1:
    
        # with 60% chance, the enemy will apply gates to own qubits
        if random.random() < 0.6:
            constants.selected_qubit = random.choice([2, 3])
            
            constants.gate_choice = random.random()
            
            #uses only X or I on own qubits, with set probabilities
            constants.selected_gate = "X" if constants.gate_choice < 0.75 else "I"

        # with 40% chance, the enemy will apply gates to player's qubits
        else:
            constants.selected_qubit = random.choice([0, 1])
            constants.gate_choice = random.random()

            # uses only H or X on player's qubits, with set probabilities
            constants.selected_gate = "H" if constants.gate_choice < 0.8 else "X"

        #applying used selection to globally stored quantum_state
        q = reverse_list[constants.selected_qubit]
        if constants.selected_gate == "X":
            constants.quatum_state.circuit.x(q)
        elif constants.selected_gate == "H":
            constants.quatum_state.circuit.h(q)
        elif constants.selected_gate == "I":
            pass 

        #setting message for player to know what the enemy has used
        constants.enemy_action_log.append(f"Enemy has applied gate {constants.selected_gate} to qubit Q{constants.selected_qubit}")

    # if PHASE 2, the enemy will use 2 gate per turn
    # Eligible gates are X, H, Z, CNOT only; only one CNOT per turn is eligible
    elif constants.boss_phase == 2:

        cnot_used = False

        #always apply 2 gates
        for _ in range(2):

            # 25% chance for CNOT
            use_cnot = random.random() < 0.25  

            if use_cnot and cnot_used == False:
                control_from_enemy = random.choice([True, False])
                
                #always having control and target on the opposite sides (if control for enemy - target for player and vice versa)
                if control_from_enemy:
                    control_q = random.choice([2, 3])
                    target_q = random.choice([0, 1])
                else:
                    control_q = random.choice([0, 1])
                    target_q = random.choice([2, 3])

                ctrl_idx = reverse_list[control_q]
                tgt_idx = reverse_list[target_q]
                constants.quatum_state.circuit.cx(ctrl_idx, tgt_idx)

                constants.enemy_action_log.append(f"Enemy used CNOT with control Q{control_q} to target Q{target_q}")
                cnot_used = True
            
            # if not CNOT, then 50/50 to targer any qubits, selecting from X, H, Z with set probability
            else:
                if random.random() < 0.5:
                    constants.selected_qubit = random.choice([2, 3])
                else:
                    constants.selected_qubit = random.choice([0, 1])

                gate = random.choices(["X", "H", "Z"], weights=[0.4, 0.4, 0.2])[0]
                q_idx = reverse_list[constants.selected_qubit]
                
                #applying selected gates
                if gate == "X":
                    constants.quatum_state.circuit.x(q_idx)
                elif gate == "H":
                    constants.quatum_state.circuit.h(q_idx)
                elif gate == "Z":
                    constants.quatum_state.circuit.z(q_idx)
    
                constants.enemy_action_log.append(f"Enemy applied {gate} to Q{constants.selected_qubit}")

    # if PHASE 3, the enemy will use 3 gate per turn
    # Eligible gates are X, Z, T, RX, RY, RZ and CCNOT only; only one CCNOT per turn is eligible
    elif constants.boss_phase == 3:

        ccnot_used = False

        # apply 3 gates per turn
        for _ in range(3):

            # 30% chance for CCNOT
            use_ccnot = random.random() < 0.3  

            if use_ccnot and ccnot_used == False:
                
                #uses own qubits as control and player's random as target
                control_qs = [2, 3]
                target_q = random.choice([0, 1])

                ctrl_1 = [3, 2, 1, 0][control_qs[0]]
                ctrl_2 = [3, 2, 1, 0][control_qs[1]]
                tgt = [3, 2, 1, 0][target_q]

                constants.quatum_state.circuit.ccx(ctrl_1, ctrl_2, tgt)


                constants.enemy_action_log.append(f"Enemy used CCNOT with controls Q{control_qs[0]}, Q{control_qs[1]} to target Q{target_q}")

                ccnot_used = True
            
            #for the rest - purely random qubit choice
            else:
                constants.selected_qubit = random.choice([0, 1, 2, 3])
                q_idx = [3, 2, 1, 0][constants.selected_qubit]

                gate = random.choice(["H", "Z", "T", "RX", "RY", "RZ"])

                if gate == "H":
                    constants.quatum_state.circuit.h(q_idx)
                    constants.enemy_action_log.append(f"Enemy applied H to Q{constants.selected_qubit}")
                elif gate == "Z":
                    constants.quatum_state.circuit.z(q_idx)
                    constants.enemy_action_log.append(f"Enemy applied Z to Q{constants.selected_qubit}")
                elif gate == "T":
                    constants.quatum_state.circuit.t(q_idx)
                    constants.enemy_action_log.append(f"Enemy applied T to Q{constants.selected_qubit}")
                
                elif gate in ["RX", "RY", "RZ"]:

                    #randomly picks angle from pi/8 to pi (to ensure enemy does not a 0-degree rotation)
                    angle = random.uniform(pi / 8, pi)
                    if gate == "RX":
                        constants.quatum_state.circuit.rx(angle, q_idx)
                    elif gate == "RY":
                        constants.quatum_state.circuit.ry(angle, q_idx)
                    elif gate == "RZ":
                        constants.quatum_state.circuit.rz(angle, q_idx)
                    
                    angle_deg = round(angle * 180 / pi, 1)
                    
                    constants.enemy_action_log.append(f"Enemy applied {gate}({angle_deg}°) to Q{constants.selected_qubit}")
    constants.selected_gate = "I"
    constants.selected_qubit = None
#######################
###START ENEMY TURN ACTS AS A BRIDGE TO TRIGGER GATE SELECTION FOR THE ENEMY TURN
#######################
def start_enemy_turn():
    #print("player ended turn.")
    #print(f"Selected param for parm gate: {constants.selected_param}")
    #player_turn = False

    # enemy applies gates (always)
    enemy_action()

    # show enemy log after applying gates
    constants.game_state = "show_enemy_log"

    # decrease turn counter until the measurement
    constants.turns_remaining_until_measurement -= 1
    print(f"Turns remaining until measurement: {constants.turns_remaining_until_measurement}")

    #unselect all buttons for player
    if constants.selected_gate_button:
        constants.selected_gate_button.selected = False
        constants.selected_gate_button = None
    if constants.selected_qubit_button:
        constants.selected_qubit_button.selected = False
        constants.selected_qubit_button = None



#######################
###WHEN ENEMY TURN IS COMPLETED, CHEKING IF TIME FOR A MEASUREMENT. IF YES, BOTH ENEMY AND PLAYER PERFORM ACTIONS 
######################
def complete_enemy_turn():

    #if time to measure the state
    if constants.turns_remaining_until_measurement <= 0:
        
        constants.last_measurement = constants.quatum_state.measure_and_collapse()
        
        player_action()
        enemy_action_effect()

        if character["hp"] <= 0:
            # don't proceed if player died during enemy_action_effect
            return
        # after the measurement, reset the counter
        if constants.boss_phase == 1:
            constants.turns_remaining_until_measurement = 1
        if constants.boss_phase == 2:
            constants.turns_remaining_until_measurement = 2
        if constants.boss_phase == 3:
            constants.turns_remaining_until_measurement = 3

    constants.enemy_action_log.clear()

    #at the end of each turn char restores set amount of QP
    character["qp"] = min(character["qp"] + player_stats["qp_restore_per_turn"], character["max_qp"])

    # only reset to battle state if not dead
    if character["hp"] > 0:
        constants.game_state = "battle"

    #print(f"current defence: {constants.player_defence_bonus}")



def set_qubit(q, button):
    constants.selected_qubit = q
    if constants.selected_qubit_button:
        constants.selected_qubit_button.selected = False
    constants.selected_qubit_button = button
    button.selected = True

#######################
###PLAYER'S QUANTUM GAME APPLICATION DEPENDING ON THE PRESSED BUTTON
######################

def confirm_gate_application():
    if constants.selected_gate and constants.selected_qubit is not None:
        
        reverse_list = [3, 2, 1, 0]
        q = reverse_list[constants.selected_qubit]
        
        gate_cost = 0 #each gate cost some QP

        #any rotation gates cost is scaled by the used degree
        if constants.selected_gate in ["RX", "RY", "RZ"]:

            gate_cost = math.floor(player_gates_cost[constants.selected_gate] * (constants.selected_param / pi))
            if constants.selected_param != 0 and gate_cost == 0:
                gate_cost = 1  # minimum cost for gate is always 1 (when angle is not 0)

        #the cost for all other gates is pre-determined
        elif constants.selected_gate in player_gates_cost:
            gate_cost = player_gates_cost[constants.selected_gate]

        # check QP, to see if can use the gate
        if character["qp"] < gate_cost:

            constants.player_action_log.clear()
            constants.show_player_log = True  #will display error message if cannot use

            if constants.selected_gate in ["RX", "RY", "RZ"]:
                deg = round(constants.selected_param * 180 / pi)
                constants.player_action_log.append(
                    f"Not enough QP for {constants.selected_gate}({deg}°): need {gate_cost}, have {character['qp']}."
                )
            else:
                constants.player_action_log.append(
                    f"Not enough QP for {constants.selected_gate}: need {gate_cost}, have {character['qp']}."
                )
            return

        # if there is enough QP, then just apply selected gate
        if constants.selected_gate == "I":
            pass
        elif constants.selected_gate == "X":
            constants.quatum_state.circuit.x(q)
        elif constants.selected_gate == "H":
            constants.quatum_state.circuit.h(q)
        elif constants.selected_gate == "Z":
            constants.quatum_state.circuit.z(q)
        elif constants.selected_gate == "RX":
            constants.quatum_state.circuit.rx(constants.selected_param, q)
        elif constants.selected_gate == "RY":
            constants.quatum_state.circuit.ry(constants.selected_param, q)
        elif constants.selected_gate == "RZ":
            constants.quatum_state.circuit.rz(constants.selected_param, q)
        elif constants.selected_gate == "S":
            constants.quatum_state.circuit.s(q)
        elif constants.selected_gate == "T":
            constants.quatum_state.circuit.t(q)

        #reducing current QP by the cost of used gate
        character["qp"] -= gate_cost

        # clearing buttons selection

        constants.selected_gate = None
        constants.selected_qubit = None
        
        #selected_param = None
        if constants.selected_gate_button:
            constants.selected_gate_button.selected = False
            constants.selected_gate_button = None
        if constants.selected_qubit_button:
            constants.selected_qubit_button.selected = False
            constants.selected_qubit_button = None
