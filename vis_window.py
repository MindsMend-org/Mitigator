# vis_window.py

# Part of Mitigator Project
# can be used to render to sensors

__version__ = "0.0.0001"
import pygame
import threading
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

    def game_loop(self):
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
        pygame.display.flip()

    def quit(self):
        pygame.quit()
