# vis_window.py

# Part of Mitigator Project
# can be used to render to sensors

__version__ = "0.0.0004"

import pygame
import threading
import time

print(f'vis_window.py {__version__}')


class Game_Vis_Window:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize the mixer module
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(f"FC Mitigator  T GVW [Game/Abstraction To Sensor/s] ver {__version__}")
        self.clock = pygame.time.Clock()
        self.running = True
        self.sound_stack = {}  # Dictionary to store sound objects
        self.image_stack = {}  # Dictionary to store image objects and their properties
        self.ready = False

        # Add attributes for bank, capital, total trades, open trades, and average profit
        self.bank = 0.0
        self.cap = 0.0
        self.trades_total = 0
        self.trades_open = 0
        self.avg_profit = 0.0
        self.trades_closed = 0
        self.trades_mitigated = 0
        self.trades_failed = 0
        self.trades_successful = 0
        self.trades_successful_mitigated = 0
        self.mitigation_lives_per_trade = 0
        self.mitigation_total_lives = 0

        # Font settings for displaying values
        self.font = pygame.font.Font(None, 36)
        self.text_color = (255, 255, 255)  # White color

    def add_image(self, file_name, name):
        """Add an image to the image stack."""
        try:
            image = pygame.image.load(file_name).convert_alpha()
            self.image_stack[name] = {'image': image, 'visible': True, 'pos': (0, 0)}
        except pygame.error as e:
            print(f"Failed to load image: {e}")

    def remove_image(self, name):
        """Remove an image from the stack."""
        if name in self.image_stack:
            del self.image_stack[name]

    def show_image(self, name):
        """Set an image to be visible."""
        if name in self.image_stack:
            self.image_stack[name]['visible'] = True

    def hide_image(self, name):
        """Set an image to be hidden."""
        if name in self.image_stack:
            self.image_stack[name]['visible'] = False

    def locate_image(self, name, x, y):
        """Set the position of an image."""
        if name in self.image_stack:
            self.image_stack[name]['pos'] = (x, y)

    def add_sound(self, file_name, name):
        """Add a sound to the sound stack."""
        try:
            self.sound_stack[name] = pygame.mixer.Sound(file_name)
        except pygame.error as e:
            print(f"Failed to load sound: {e}")

    def play_sound(self, name):
        """Play a sound once."""
        sound = self.sound_stack.get(name)
        if sound:
            sound.play()

    def loop_sound(self, name):
        """Play a sound on loop."""
        sound = self.sound_stack.get(name)
        if sound:
            sound.play(loops=-1)

    def stop_sound(self, name):
        """Stop a sound."""
        sound = self.sound_stack.get(name)
        if sound:
            sound.stop()

    def remove_sound(self, name):
        """Remove a sound from the stack and stop it if playing."""
        sound = self.sound_stack.pop(name, None)
        if sound:
            sound.stop()

    def run(self):
        """Run the game loop in a separate thread."""
        thread = threading.Thread(target=self.game_loop)
        thread.start()
        # Ensure the game loop has started
        while not self.is_ready():
            time.sleep(0.1)

    def game_loop(self):
        self.ready = True
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # Maintain 60 frames per second

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        # Update game logic here
        pass

    def render(self):
        self.screen.fill((0, 0, 0))  # Clear the screen
        # Render visible images from the stack
        for name, properties in self.image_stack.items():
            if properties['visible']:
                self.screen.blit(properties['image'], properties['pos'])

        # Render the bank, capital, total trades, open trades, and average profit
        self.render_values()

        pygame.display.flip()

    def render_values(self):
        """Render the values on the screen."""
        values_text = [
            f"Bank: £{self.bank:.2f}",
            f"Capital: £{self.cap:.2f}",
            f"Total Trades: {self.trades_total}",
            f"Open Trades: {self.trades_open}",
            f"Average Profit: £{self.avg_profit:.2f}",
            f"Closed Trades: {self.trades_closed}",
            f"Mitigated Trades: {self.trades_mitigated}",
            f"Failed Trades: {self.trades_failed}",
            f"Successful Trades: {self.trades_successful}",
            f"Successful Mitigated Trades: {self.trades_successful_mitigated}",
            f"Mitigation Lives per Trade: {self.mitigation_lives_per_trade}",
            f"Mitigation Total Lives: {self.mitigation_total_lives}"
        ]

        y_offset = 10
        for text in values_text:
            rendered_text = self.font.render(text, True, self.text_color)
            self.screen.blit(rendered_text, (10, y_offset))
            y_offset += 40

    def quit(self):
        pygame.quit()

    def is_ready(self):
        """Check if the game loop is ready."""
        if not self.ready:
            self.ready = True
            # delay may be needed for some systems
        return self.ready

    # Getter and setter methods
    def get_bank(self):
        return self.bank

    def set_bank(self, value):
        self.bank = value

    def get_cap(self):
        return self.cap

    def set_cap(self, value):
        self.cap = value

    def get_trades_total(self):
        return self.trades_total

    def set_trades_total(self, value):
        self.trades_total = value

    def get_trades_open(self):
        return self.trades_open

    def set_trades_open(self, value):
        self.trades_open = value

    def get_trades_closed(self):
        return self.trades_closed

    def set_trades_closed(self, value):
        self.trades_closed = value

    def get_trades_mitigated(self):
        return self.trades_mitigated

    def set_trades_mitigated(self, value):
        self.trades_mitigated = value

    def get_trades_failed(self):
        return self.trades_failed

    def set_trades_failed(self, value):
        self.trades_failed = value

    def get_trades_successful(self):
        return self.trades_successful

    def set_trades_successful(self, value):
        self.trades_successful = value

    def get_trades_successful_mitigated(self):
        return self.trades_successful_mitigated

    def set_trades_successful_mitigated(self, value):
        self.trades_successful_mitigated = value

    def get_mitigation_lives_per_trade(self):
        return self.mitigation_lives_per_trade

    def set_mitigation_lives_per_trade(self, value):
        self.mitigation_lives_per_trade = value

    def get_mitigation_total_lives(self):
        return self.mitigation_total_lives

    def set_mitigation_total_lives(self, value):
        self.mitigation_total_lives = value

    def get_avg_profit(self):
        return self.avg_profit

    def set_avg_profit(self, value):
        self.avg_profit = value
