#here stored data about character and enemy for battle system

# inital and max params for char
character = {
    "name": "Mage",
    "hp": 100,
    "max_hp": 100,
    "qp": 250,
    "max_qp": 250
}

# inital and max params for the enemy
enemy = {
    "name": "Archenemy",
    "hp": 100,
    "max_hp": 100
}

# linking states to actions
player_action_map = {
    "00": "idle",
    "01": "attack",
    "10": "defend",
    "11": "heal"
}

# cost per gate. NOTE: RX, RY, RZ have scalable cost from the selected angle. Herein MAX cost for the is set
player_gates_cost = {
    "I": 0,
    "X": 10,
    "H": 15,
    "S": 6,
    "Z": 6,
    "T": 6,
    "RX": 30,
    "RY": 30,
    "RZ": 30,
}

#

player_stats = {
    "normal_attack": 10,
    "heal": 15,
    "qp_restore_per_turn": 10,
    "defence": 20,
    "last_phase_attack": 20,
}

enemy_stats = {
    "base_attack": {
        1: 10,  # phase 1
        2: 15,  # phase 2
        3: 20   # phase 3
    },
    "heal": 10,
    "attack_charge_per_idle": 0.2,   # +20% per idle turn
    "defence_increase": 0.1,         # +10% per defend
    "max_defence": 1.0
}