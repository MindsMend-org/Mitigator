# FC 2024 Deep Learn M Q mince@foldingcircles.co.uk
# VJoypad.py
import pyautogui  # for simulating keyboard and mouse actions

class VirtualJoypad:
    def __init__(self, action_map):
        self.action_map = action_map  # Dictionary mapping generic actions to specific keys/buttons

    def perform_action(self, action):
        key = self.action_map.get(action)
        if key:
            pyautogui.press(key)  # Simulates pressing the key

"""
Example for a specific game map[ActionNAME: InOutKey]
action_map = {
    "UP": "w",
    "UPRIGHT": "e",
    "RIGHT": "d",
    "DOWNRIGHT": "x",
    "DOWN": "s",
    "DOWNLEFT": "z",
    "LEFT": "a",
    "UPLEFT": "q",
    "CENTER": "5",
    
    "BUTTON_A": "space",
    "BUTTON_B": "ctrl"
    
    "8": "w",
    "9": "e",
    "6": "d",
    "3": "x",
    "2": "s",
    "1": "z",
    "4": "a",
    "7": "q",
    "5": "5",
    
    "10": "space",
    "11": "ctrl"
}
action = ai_model.predict(game_state)  # Assuming ai_model.predict returns a generic action like "UP"
joypad.perform_action(action)
"""
