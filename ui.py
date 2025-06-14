import constants
from quantum import QuantumState
#from constants import boss_phase
import pygame
from numpy import pi


#######################
###Here is defined functionality to draw a text box for narration, displaying char/enemy stats during the battle, and animate sprites, etc.
#######################

#######################
###STATS FOR BATTLE DISPLAYING
#######################

box_spacing = 100
total_width = 2 * 350 + box_spacing
start_x = (constants.SCREEN_WIDTH - total_width) // 2
#char_box_pos = (start_x, constants.SCREEN_HEIGHT - constants.INFO_PANEL_HEIGHT + 20)
#enemy_box_pos = (start_x + 350 + box_spacing, constants.SCREEN_HEIGHT - constants.INFO_PANEL_HEIGHT + 20)

box_spacing = 20 
box_width = 400 

enemy_box_pos = (constants.SCREEN_WIDTH - box_width -10, constants.SCREEN_HEIGHT - constants.INFO_PANEL_HEIGHT + 20)
char_box_pos = (constants.SCREEN_WIDTH - 2 * box_width - box_spacing - 10, constants.SCREEN_HEIGHT - constants.INFO_PANEL_HEIGHT + 20)

def draw_info_box(surface, x, y, data, portrait_img, show_qp=True):
    box_width = 400
    box_height = 100
    pygame.draw.rect(surface, constants.BLACK, (x, y, box_width, box_height), border_radius=6)
    pygame.draw.rect(surface, constants.WHITE, (x, y, box_width, box_height), 2, border_radius=6)

    # draw char/enemy portrait in the box
    surface.blit(portrait_img, (x + 10, y + 18))

    # char/enemy name in the box
    name_text = constants.font_bold.render(data["name"], True, constants.WHITE)
    surface.blit(name_text, (x + 84, y + 10))

    # HP bar

    hp_ratio = data["hp"] / data["max_hp"]
    pygame.draw.rect(surface, constants.RED, (x + 84, y + 38, 200, 20))
    pygame.draw.rect(surface, constants.GREEN, (x + 84, y + 38, 200 * hp_ratio, 20))
    
    hp_text = constants.font.render(f"{data['hp']}/{data['max_hp']} HP", True, constants.WHITE)
    surface.blit(hp_text, (x + 290, y + 38))

    # QP bar (if applicable; enemy does not have a limitation on QP)
    if show_qp:
        mp_ratio = data["qp"] / data["max_qp"]
        pygame.draw.rect(surface, constants.BLUE, (x + 84, y + 66, 200, 20))
        pygame.draw.rect(surface, constants.LIGHT_BLUE, (x + 84, y + 66, 200 * mp_ratio, 20))
        mp_text = constants.font.render(f"{data['qp']}/{data['max_qp']} QP", True, constants.WHITE)
        surface.blit(mp_text, (x + 290, y + 66))

#######################
###NARRATION TEXTBOX AND ITS FORWARDING
###OUTPUTS SPEAKING CHAR NAME AND MULTILINE TEXT. SUPPORTS LINE BREAKING
#######################

class TextBox:
    def __init__(self, screen, font, name_font, box_rect, text_color=constants.WHITE, name_color=constants.YELLOWISH,
                 box_color=constants.DARK_GRAY, padding=10, line_spacing=5, char_delay=30):
        
        self.screen = screen
        self.font = font
        self.name_font = name_font
        self.box_rect = box_rect
        self.text_color = text_color
        self.name_color = name_color
        self.box_color = box_color
        self.padding = padding
        self.line_spacing = line_spacing
        self.char_delay = char_delay
    

        self.text = ""
        self.char_name = ""
        self.full_text = ""
        self.displayed_text = ""
        self.last_char_time = pygame.time.get_ticks()
        self.text_pos = 0
        self.done = True

    def set_text(self, char_name, text):
        self.char_name = char_name
        self.full_text = text
        self.displayed_text = ""
        self.text_pos = 0
        self.last_char_time = pygame.time.get_ticks()
        self.done = False

    def update(self):
        if not self.done:
            now = pygame.time.get_ticks()
            if now - self.last_char_time >= self.char_delay:
                if self.text_pos < len(self.full_text):
                    self.text_pos += 1
                    self.displayed_text = self.full_text[:self.text_pos]
                    self.last_char_time = now
                else:
                    self.done = True

    def draw(self):
        pygame.draw.rect(self.screen, self.box_color, self.box_rect)

        # render character name
        name_surf = self.name_font.render(self.char_name, True, self.name_color)
        name_y = self.box_rect.y + self.padding
        text_start_x = self.box_rect.x + self.padding

        self.screen.blit(name_surf, (text_start_x, name_y))

        #word wrapping
        max_width = self.box_rect.width - (text_start_x - self.box_rect.x) - self.padding
        words = self.displayed_text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            test_surf = self.font.render(test_line, True, self.text_color)
            if test_surf.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        y = name_y + name_surf.get_height() + self.line_spacing
        for line in lines:
            line_surf = self.font.render(line, True, self.text_color)
            self.screen.blit(line_surf, (text_start_x, y))
            y += line_surf.get_height() + self.line_spacing

    def is_done(self):
        return self.done

    def skip(self):
        self.text_pos = len(self.full_text)
        self.displayed_text = self.full_text
        self.done = True

def handle_dialogue_advance(current_sequence, dialog_index, textbox, dialog_flag):
    #global current_sequence, dialog_index, textbox
    #print(dialog_index)
    
    if not current_sequence:
        return

    if textbox.is_done():
        dialog_index += 1
        if dialog_index < len(current_sequence):
            entry = current_sequence[dialog_index]
            textbox.set_text(entry["name"], entry["text"])
        else:
            current_sequence = None  # End the dialogue
            dialog_flag = False
    else:
        textbox.skip()
    
    return current_sequence, dialog_index, textbox, dialog_flag

#######################
###ANY SPRITE ANIMATION
#######################

class SpriteAnimator:
    def __init__(self, sprite_sheet, frame_count, pos, frame_delay=100, scale=1.0, loop=True, flip = False):
        self.scale = scale
        self.frames = self._slice_frames(sprite_sheet, frame_count, flip=flip)
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = frame_delay
        self.pos = pos
        self.last_update = pygame.time.get_ticks()
        self.loop = loop
        self.done = False  # new flag to track completion
        self.flip = flip

    #changing individual frame to needed scale + flip if needed
    def _slice_frames(self, sprite_sheet, frame_count, flip=False):
        
        frame_width = sprite_sheet.get_width() // frame_count
        
        frame_height = sprite_sheet.get_height()
        
        frames = []
        
        for i in range(frame_count):
            frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            if self.scale != 1.0:
                scaled_width = int(frame_width * self.scale)
                scaled_height = int(frame_height * self.scale)
                frame = pygame.transform.scale(frame, (scaled_width, scaled_height))
            if flip:
                frame = pygame.transform.flip(frame, True, False)
                #print("HERE, flips separate frames")
            frames.append(frame)
        
        return frames


    def update(self, dt):
        if self.done:
            return

        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_delay:
            self.last_update = now
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.frames) - 1  # stay on last
                    self.done = True

    def draw(self, surface):
        surface.blit(self.frames[self.frame_index], self.pos)

#######################
###RENDERING CURRENT STATE VECTOR FOR PLAYER
#######################
def draw_statevector_box(surface, quantum_state, x, y, turns_left, width=290, height=160):

    sv = quantum_state.get_statevector()

    # filter and format amplitudes
    lines = ["Current state:"]
    for i, amp in enumerate(sv.data):
        probability = abs(amp) ** 2
        if probability < 1e-4:
            continue  # approximate rounding

        binary = format(i, f"0{sv.num_qubits}b")
        prob_percent = f"{probability * 100:.1f}%"

        if abs(probability - 1.0) < 1e-6:
            #100% state (basis)
            line = f"|{binary}>  ({prob_percent})"
        else:
            # superposition: show amplitude, state, and probability
            real_part = f"{amp.real:.3f}" if abs(amp.real) >= 1e-6 else ""
            imag_part = f"{'+' if amp.imag >= 0 else '-'}{abs(amp.imag):.3f}j" if abs(amp.imag) >= 1e-6 else ""
            amp_str = real_part + imag_part
            line = f"{amp_str} |{binary}>  ({prob_percent})"

        lines.append(line)

    lines.append(f"Turns until measurement: {turns_left}")

    # dynamic height for the whole text box depending on number of lines (max expected 18 lines: 16 for superposition, 1 turn counter and 1 just header; min 3 lines)
    line_height = constants.font.get_height() + 4
    height = 10 + len(lines) * line_height + 10  # padding

    # draw box
    pygame.draw.rect(surface, constants.BLACK, (x, y, width, height), border_radius=6)
    pygame.draw.rect(surface, constants.WHITE, (x, y, width, height), 2, border_radius=6)

    # render text lines
    line_y = y + 10
    for line in lines:
        txt_surface = constants.font.render(line, True, constants.WHITE)
        surface.blit(txt_surface, (x + 10, line_y))
        line_y += line_height

#######################
###BUTTONS FOR SELECTING GATES RENDERING
#######################

class UIButton:
    def __init__(self, rect, text, action=None, font=constants.font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action  # function to call on click
        self.font = font
        self.color = constants.DIM_GRAY
        self.hover_color = constants.LIGHT_GRAY
        self.active = False
        self.selected = False  
        self.icon = None


    def draw(self, surface):
    
        color = self.hover_color if self.active else self.color

        if self.selected:
            color = constants.LIGHT_GREEN
        else:
            color = self.hover_color if self.active else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, constants.WHITE, self.rect, 2)

        if self.icon:
            icon_rect = self.icon.get_rect(center=self.rect.center)
            surface.blit(self.icon, icon_rect)
        else:
            text_surface = self.font.render(self.text, True, constants.WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def handle_event(self, event, mouse_pos):
        self.active = self.rect.collidepoint(mouse_pos) 

        if self.active and event.type == pygame.MOUSEBUTTONDOWN:
            if self.action:
                self.action()

def update_gate_buttons():
    gate_buttons = [btn for btn in constants.buttons if btn.text in constants.all_gates]
    for btn in gate_buttons:
        constants.buttons.remove(btn)

    start_index = constants.gate_page * 4
    visible_gates = constants.all_gates[start_index:start_index + 4]

    for i, gate in enumerate(visible_gates):
        x = constants.buttons_start_x + i * (constants.button_width + constants.button_spacing)
        btn = UIButton((x, constants.start_y_gate, constants.button_width, constants.button_height), gate)
        #btn.action = lambda g=gate, b=btn: gate_set_callback(g, b) if gate_set_callback else None

        if gate == "X" and constants.boss_phase >= 2:
            btn.icon = constants.lock_icon
            btn.action = None
            btn.color = constants.DARK_GRAY_2
        elif gate == "H" and constants.boss_phase >= 3:
            btn.action = None
            btn.icon = constants.lock_icon
            btn.color = constants.DARK_GRAY_2
        else:
            btn.action = lambda g=gate, b=btn: constants.gate_set_callback(g, b) if constants.gate_set_callback else None

        constants.buttons.append(btn)
        
#######################
###PAGINATION FOR BUTTONS
#######################
def next_gate_page():
    max_page = (len(constants.all_gates) - 1) // 4
    constants.gate_page = (constants.gate_page + 1) % (max_page + 1)
    update_gate_buttons()


def register_gate_callback(callback):
    constants.gate_set_callback = callback

#######################
###DRAWING SPRITES
#######################
def draw_hero(screen, clock):
    dt = clock.get_time()

    if constants.current_animator == constants.hero_death_animator:
        constants.current_animator.update(dt)
        constants.current_animator.draw(screen)
        return

    constants.current_animator.update(dt)
    constants.current_animator.draw(screen)
    now = pygame.time.get_ticks()

    if constants.attack_start_time and now - constants.attack_start_time > 700:
        constants.current_animator = constants.hero_idle_animator
        constants.attack_start_time = None

    if constants.defend_start_time and now - constants.defend_start_time > 900:
        constants.current_animator = constants.hero_idle_animator
        constants.defend_start_time = None

    if constants.heal_start_time and now - constants.heal_start_time > 1600:
        constants.current_animator = constants.hero_idle_animator
        constants.heal_start_time = None

def draw_enemy(screen, clock):
    dt = clock.get_time()

    if constants.enemy_current_animator == constants.enemy_death_animator:
        constants.enemy_current_animator.update(dt)
        constants.enemy_current_animator.draw(screen)
        return

    constants.enemy_current_animator.update(dt)
    constants.enemy_current_animator.draw(screen)
    now = pygame.time.get_ticks()

    if constants.enemy_attack_start_time and now - constants.enemy_attack_start_time > 1200:
        constants.enemy_current_animator = constants.enemy_idle_animator
        constants.enemy_attack_start_time = None

    if constants.enemy_defend_start_time and now - constants.enemy_defend_start_time > 1200:
        constants.enemy_current_animator = constants.enemy_idle_animator
        constants.enemy_defend_start_time = None

    if constants.enemy_heal_start_time and now - constants.enemy_heal_start_time > 1200:
        constants.enemy_current_animator = constants.enemy_idle_animator
        constants.enemy_heal_start_time = None

    if constants.enemy_charge_start_time and now - constants.enemy_charge_start_time > 1200:
        constants.enemy_current_animator = constants.enemy_idle_animator
        constants.enemy_charge_start_time = None

#######################
###DRAWING BOX "ENEMY USED X ON Y"
#######################
def draw_enemy_action_log(surface, log):
    if not log:
        return

    width = 550
    height = 40 + len(log) * 30
    x = (constants.SCREEN_WIDTH - width) // 2
    y = (constants.SCREEN_HEIGHT - height) // 2

    pygame.draw.rect(surface, constants.BLACK, (x, y, width, height), border_radius=8)
    pygame.draw.rect(surface, constants.WHITE, (x, y, width, height), 2, border_radius=8)

    for i, line in enumerate(log):
        txt = constants.font.render(line, True, constants.WHITE)
        surface.blit(txt, (x + 20, y + 20 + i * 30))

#######################
###DRAWING SLIDER FOR PARAMETRIC GATES ANGLE SELECTION
#######################
class UISlider:
    def __init__(self, rect, min_val, max_val, initial_val, on_change=None):
        self.rect = pygame.Rect(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.handle_radius = 10
        self.dragging = False
        self.on_change = on_change 

    def draw(self, surface):
        
        #track
        pygame.draw.line(surface, constants.WHITE, 
                         (self.rect.x, self.rect.centery), 
                         (self.rect.right, self.rect.centery), 3)

        #handle
        handle_x = self.rect.x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * self.rect.width
        pygame.draw.circle(surface, constants.LIGHT_BLUE, (int(handle_x), self.rect.centery), self.handle_radius)

        #label
        angle_deg = int(self.value * 180 / pi)
        label = constants.font.render(f"{angle_deg}°", True, constants.WHITE)
        surface.blit(label, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(self.rect.x - self.handle_radius, self.rect.y, self.rect.width + 2 * self.handle_radius, self.rect.height).collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
            new_value = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.value = new_value
            
            
            if self.on_change:
                self.on_change(self.value)

#######################
###TEXT BOXES FOR PERFORMED ACTION AFTER THE MEASUREMENT
#######################
class FloatingText:
    def __init__(self, text, pos, duration=3000, font=None, color=constants.WHITE):
        self.text = text
        self.pos = pos
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.font = font or pygame.font.Font(None, 28)
        self.color = color

    def draw(self, screen):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed < self.duration:
            
            # fixed box size (max expected string length is "Charging up")
            box_width = 140
            box_height = 35
            padding = 6

            box_x = self.pos[0] - box_width // 2
            box_y = self.pos[1] - box_height // 2
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

            bg_color = constants.BLACK
            border_color = constants.WHITE

            pygame.draw.rect(screen, bg_color, box_rect, border_radius=6)
            pygame.draw.rect(screen, border_color, box_rect, 1, border_radius=6)

            # render text
            text_surface = self.font.render(self.text, True, self.color)
            text_rect = text_surface.get_rect(center=box_rect.center)

            screen.blit(text_surface, text_rect)
            return True
        
        return False

#######################
###CREATE QUANTUM GATE BUTTONS
#######################
def create_gate_buttons():

    constants.buttons[:] = [b for b in constants.buttons if b.text not in constants.all_gates]

    for i, gate in enumerate(constants.gates):
        x = constants.buttons_start_x + i * (constants.button_width + constants.button_spacing)
        btn = UIButton((x, constants.start_y_gate, constants.button_width, constants.button_height), gate)

        #if the enemy is in the phase 2, player cannot use X gate
        if gate == "X" and constants.boss_phase >= 2:
            btn.action = None
            btn.icon = constants.lock_icon
            btn.color = constants.DARK_GRAY_2
        
        #if the enemy is in the phase 3, player cannot use X and H gates
        elif gate == "H" and constants.boss_phase >= 3:
            btn.action = None
            btn.icon = constants.lock_icon
            btn.color = constants.DARK_GRAY_2
        else:
            btn.text = gate
            btn.icon = None
            btn.action = lambda g=gate, b=btn: set_gate(g, b)

        constants.buttons.append(btn)

#######################
###CREATE QUBIT BUTTONS (0-4, 0 is leftmost)
#######################
def create_qubit_buttons(set_qubit_callback):

    for i in range(4):
        x = constants.buttons_start_x + i * (constants.button_width + constants.button_spacing)
        btn = UIButton((x, constants.start_y_qubit, constants.button_width, constants.button_height), f"Q{i}")
        btn.action = lambda q=i, b=btn: set_qubit_callback(q, b)
        constants.buttons.append(btn)

#######################
###CREATE CONTROL BUTTONS (APPLY, END TURN, AND PAGINATION ARROW)
#######################

def create_control_buttons(confirm_callback, end_turn_callback):
    """Creates Apply, End Turn, and Arrow (next gate page) buttons."""
    constants.buttons.append(UIButton(
        (45, constants.apply_y, 100, 40), "Apply", action=confirm_callback
    ))
    constants.buttons.append(UIButton(
        (165, constants.apply_y, 100, 40), "End Turn", action=end_turn_callback
    ))
    arrow_btn = UIButton(
        (constants.buttons_start_x + 4 * (constants.button_width + constants.button_spacing),
         constants.start_y_gate, 40, constants.button_height),
        "", next_gate_page
    )
    arrow_btn.icon = constants.arrow_icon
    constants.buttons.append(arrow_btn)

#######################
###STORING SELECTED VALUES FROM BUTTONS/SLIDER GLOBALLY
#######################
def set_gate(gate, button):
    constants.selected_gate = gate
    if constants.selected_gate_button:
        constants.selected_gate_button.selected = False
    constants.selected_gate_button = button
    button.selected = True

def set_param(angle):
    constants.selected_param = angle

def create_param_slider(on_change_callback):
    slider = UISlider(
        rect=(300, constants.SCREEN_HEIGHT - 20, 500, 20),
        min_val=0,
        max_val=pi,
        initial_val=pi / 2,
        on_change=on_change_callback
    )
    constants.selected_param = slider.value
    return slider

