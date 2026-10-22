import sys
from time import sleep

import pygame

# Import the classes needed to manage the game.
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""

        # Initialize Pygame so its features are ready to use.
        pygame.init()

        # Create a clock to control the game's frame rate.
        self.clock = pygame.time.Clock()

        # Create an object to store the game's settings.
        self.settings = Settings()

        # Create the game window using the width and height
        # specified in the Settings class.
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))

        # Set the title displayed at the top of the game window.
        pygame.display.set_caption("Alien Invasion")

        # Create an object to store the player's game statistics.
        # Create a scoreboard to display the score, level, and ships.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # Create the player's ship.
        self.ship = Ship(self)

        # Create sprite groups to store bullets and aliens.
        # Sprite groups make it easier to update and manage
        # multiple game objects.
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        # Create the initial fleet of aliens.
        self._create_fleet()

        # Start Alien Invasion in an inactive state.
        # The player must click Play before the game begins.
        self.game_active = False

        # Create the Play button that appears when the game
        # is inactive.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""

        # Keep the game running until the player closes it.
        while True:

            # Check for keyboard and mouse events.
            self._check_events()

            # Update moving objects only while the game is active.
            if self.game_active:
                # Update the ship's position based on keyboard input.
                self.ship.update()

                # Update bullets, remove old bullets, and check
                # whether bullets have hit any aliens.
                self._update_bullets()

                # Update alien positions and check for collisions.
                self._update_aliens()

            # Redraw the screen to display the latest game state.
            self._update_screen()

            # Limit the game to approximately 60 frames per second.
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""

        # Retrieve all events that have occurred since
        # the previous time events were checked.
        for event in pygame.event.get():

            # Close the game when the player clicks the X button.
            if event.type == pygame.QUIT:
                sys.exit()

            # Check which key was pressed.
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            # Check which key was released.
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

            # Check whether the player clicked the mouse.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get the current position of the mouse cursor.
                mouse_pos = pygame.mouse.get_pos()

                # Check whether the Play button was clicked.
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""

        # Check whether the mouse position is inside the
        # rectangular area occupied by the Play button.
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)

        # Start a new game only if the button was clicked
        # and the game is currently inactive.
        if button_clicked and not self.game_active:

            # Reset dynamic settings, such as the game speed,
            # to their starting values.
            self.settings.initialize_dynamic_settings()

            # Reset the player's statistics for a new game.
            self.stats.reset_stats()

            # Update the displayed score, level, and remaining ships.
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Activate the game so objects can move and update.
            self.game_active = True

            # Remove any bullets and aliens left over from
            # a previous game.
            self.bullets.empty()
            self.aliens.empty()

            # Create a fresh fleet of aliens.
            # Move the ship back to the center of the screen.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor while the game is running.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""

        # Start moving the ship to the right when the
        # right arrow key is pressed.
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True

        # Start moving the ship to the left when the
        # left arrow key is pressed.
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True

        # Exit the game when the Q key is pressed.
        elif event.key == pygame.K_q:
            sys.exit()

        # Fire a bullet when the spacebar is pressed.
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""

        # Stop moving right when the right arrow key is released.
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False

        # Stop moving left when the left arrow key is released.
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""

        # Only create a bullet if the number of bullets on screen
        # is below the maximum allowed by the game settings.
        if len(self.bullets) < self.settings.bullets_allowed:

            # Create a new bullet at the ship's current position.
            new_bullet = Bullet(self)

            # Add the bullet to the sprite group so it can
            # be updated and drawn on the screen.
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""

        # Update the position of every bullet in the group.
        self.bullets.update()

        # Loop through a copy of the bullet group so bullets
        # can safely be removed while checking them.
        for bullet in self.bullets.copy():

            # Remove bullets that have moved beyond the top
            # of the screen, because they can no longer hit aliens.
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        # Check whether any bullets have collided with aliens.
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""

        # Detect collisions between bullets and aliens.
        # The True values mean that both the bullet and the
        # alien involved in a collision will be removed.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        # If collisions occurred, award points for the aliens hit.
        if collisions:
            # Each dictionary value contains the aliens hit by
            # a particular bullet.
            for aliens in collisions.values():

                # Award points for every alien destroyed.
                self.stats.score += self.settings.alien_points * len(aliens)

            # Refresh the displayed score.
            self.sb.prep_score()

            # Update the high score if the current score is higher.
            self.sb.check_high_score()

        # If no aliens remain, the player has cleared the fleet.
        if not self.aliens:

            # Remove any remaining bullets before creating
            # the next fleet.
            self.bullets.empty()

            # Create a new fleet of aliens.
            self._create_fleet()

            # Increase the speed of the game for the next level.
            self.settings.increase_speed()

            # Move to the next level and update the scoreboard.
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""

        # Check whether the player still has ships remaining.
        if self.stats.ships_left > 0:

            # Subtract one ship from the remaining ship count.
            self.stats.ships_left -= 1

            # Update the number of ships displayed on the screen.
            self.sb.prep_ships()

            # Remove all existing bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new alien fleet and return the ship
            # to the center of the screen.
            self._create_fleet()
            self.ship.center_ship()

            # Pause briefly so the player can notice the collision.
            sleep(0.5)

        else:
            # End the active game when no ships remain.
            self.game_active = False

            # Make the mouse cursor visible again so the player
            # can click the Play button to start a new game.
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""

        # Check whether an alien has reached either side
        # of the screen and move the fleet down if necessary.
        self._check_fleet_edges()

        # Update the positions of all aliens in the fleet.
        self.aliens.update()

        # Check whether any alien has collided with the ship.
        # The function returns a sprite if a collision is detected.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Check whether any alien has reached the bottom
        # of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""

        # Examine every alien in the fleet.
        for alien in self.aliens.sprites():

            # Compare the bottom of the alien's rectangle
            # with the height of the game screen.
            if alien.rect.bottom >= self.settings.screen_height:

                # Treat an alien reaching the bottom like
                # a collision with the player's ship.
                self._ship_hit()

                # Stop checking because the ship-hit response
                # has already been triggered.
                break

    def _create_fleet(self):
        """Create the fleet of aliens."""

        # Create a temporary alien to determine the size
        # of each alien's rectangle.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        # Set the starting position for the first alien.
        # Leave one alien's width and height as the margins.
        current_x, current_y = alien_width, alien_height

        # Continue creating rows while there is enough
        # vertical space for another row of aliens.
        while current_y < (self.settings.screen_height - 3 * alien_height):

            # Continue adding aliens across the current row
            # while there is enough horizontal space.
            while current_x < (self.settings.screen_width - 2 * alien_width):

                # Create an alien at the current coordinates.
                self._create_alien(current_x, current_y)

                # Move to the right to leave space for
                # the next alien in the same row.
                current_x += 2 * alien_width

            # The row is complete. Return to the left side
            # before creating the next row.
            current_x = alien_width

            # Move down to the next row, leaving space
            # between the rows.
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""

        # Create a new Alien object.
        new_alien = Alien(self)

        # Store the horizontal position as a floating-point
        # value so the alien's position can be updated smoothly.
        new_alien.x = x_position

        # Set the alien's rectangle coordinates.
        # Pygame uses the rectangle to position and draw the sprite.
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position

        # Add the new alien to the fleet's sprite group.
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""

        # Check each alien to see whether it has reached
        # the left or right edge of the screen.
        for alien in self.aliens.sprites():

            # The check_edges() method returns True when
            # an alien reaches an edge.
            if alien.check_edges():

                # Move the fleet down and reverse its direction.
                self._change_fleet_direction()

                # Only one alien needs to trigger the change.
                # Stop checking the remaining aliens.
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""

        # Move every alien down by the distance specified
        # in the game settings.
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed

        # Reverse the fleet's direction.
        # Multiplying by -1 changes 1 to -1 or -1 to 1.
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""

        # Fill the background with the configured background color.
        # This clears the previous frame before drawing the new one.
        self.screen.fill(self.settings.bg_color)

        # Draw every bullet on the screen.
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # Draw the player's ship at its current position.
        self.ship.blitme()

        # Draw all the aliens in the fleet.
        self.aliens.draw(self.screen)

        # Draw the score information, including the score,
        # high score, level, and remaining ships.
        self.sb.show_score()

        # Display the Play button whenever the game is inactive.
        if not self.game_active:
            self.play_button.draw_button()

        # Update the display to show everything drawn
        # during this frame.
        pygame.display.flip()


# Run the game only when this file is executed directly,
# rather than when it is imported into another Python file.
if __name__ == '__main__':

    # Create an instance of the AlienInvasion class.
    ai = AlienInvasion()

    # Start the game's main loop.
    ai.run_game()