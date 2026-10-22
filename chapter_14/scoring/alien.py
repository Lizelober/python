# alien.py

import pygame

# Import the Sprite class from Pygame.
# Sprite is the base class for game objects that can be
# added to sprite groups and managed by Pygame.
from pygame.sprite import Sprite

# Import Path to build a file path that works across
# different operating systems.
from pathlib import Path


class Alien(Sprite):
    """A class to represent a single alien in the fleet."""

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""

        # Initialize the parent Sprite class.
        # This allows the alien to work with Pygame sprite groups.
        super().__init__()

        # Get a reference to the game's screen.
        self.screen = ai_game.screen

        # Get the game settings, including alien speed
        # and the fleet's movement direction.
        self.settings = ai_game.settings

        # Build the path to the alien image.
        # __file__ represents the location of this Python file.
        # parent gets the folder containing alien.py.
        # The image is stored in the images subfolder.
        image_path = Path(__file__).parent / 'images' / 'alien.bmp'

        # Load the alien image from the specified file path.
        self.image = pygame.image.load(image_path)

        # Create a rectangle around the image.
        # Pygame uses this rectangle to position the alien
        # and detect collisions with other game objects.
        self.rect = self.image.get_rect()

        # Start each new alien near the top-left corner
        # of the screen, leaving a margin equal to its size.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position as
        # a floating-point number.
        # This allows the alien to move in small increments
        # instead of being restricted to whole-number positions.
        self.x = float(self.rect.x)

    def check_edges(self):
        """Return True if alien is at edge of screen."""

        # Get a rectangle representing the entire game screen.
        screen_rect = self.screen.get_rect()

        # Return True if the alien has reached or passed
        # the right edge, or if its left edge has reached
        # or passed the left side of the screen.
        # Otherwise, return False.
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self):
        """Move the alien right or left."""

        # Calculate the alien's new horizontal position.
        # alien_speed determines how fast it moves.
        # fleet_direction determines the direction:
        #  1  = move right
        # -1  = move left
        self.x += self.settings.alien_speed * self.settings.fleet_direction

        # Update the rectangle's horizontal position
        # so the alien appears at its new location.
        # Pygame uses rect to draw the image on the screen.
        self.rect.x = self.x
