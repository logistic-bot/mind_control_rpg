"""
This file implements the Scene class, which contains convenience methods for all Scenes.
"""

from src.core.render.render import CursesRenderer


class Scene:
    """
    The base class for all Scenes, contains convenience methods.
    """
    def __init__(self, renderer: CursesRenderer) -> None:
        self.renderer = renderer

    def sleep_key(self, delay: float) -> bool:
        """
        Wait until a key is pressed, or the delay is exceeded.

        For more documentation, see CursesRenderer.wait_keypress_delay()

        :param delay: How many seconds to wait for a key press
        """
        if delay == 0:
            return False

        key = self.renderer.wait_keypress_delay(delay)
        return key == -1

    def addinto_centred(self, y_pos: int, text: str, delay: float = 0, pager_delay: float = 2) -> \
            bool:
        """
        Add a text into, centered vertically, with optional delay between lines.

        If the terminal is not tall enough, the text will be paged. In that case, the parameter
        pager_delay is used to delay each page.

        :param y_pos: The y position where the text should be displayed
        :param text: The text to be displayed
        :param delay: Delay between each line
        :param pager_delay: Delay between each page
        :return: True if the text was skipped, False otherwise
        """
        line_count = len(text.splitlines())
        max_lines = self.renderer.max_y - 2
        all_lines = text.splitlines()

        if y_pos < 1:
            # Fix potential issues with incorrect y_pos

            # When this is called from addinto_all_centred, and the text is too long, y_pos will
            # be negative; this fixes that.
            y_pos = 1

        # If the text is too long for the terminal, it needs to be paged.
        if line_count > max_lines:  # -2 for the borders
            # We will first show as many lines as we can, then recurse with the remaining lines
            next_lines = "\n".join(all_lines[:max_lines])
            remaining_lines = "\n".join(all_lines[max_lines - 5:])

            # If the text was skipped, skip will be True
            skip = self.addinto_centred(y_pos, next_lines, delay, pager_delay)

            # We wait for an additional delay between each page. skip_all will be True if the
            # delay is skipped, in that case we don't display the next pages.
            skip_all = not self.sleep_key(pager_delay)
            self.clear() # clear the screen for the next page

            if skip: # If the text animation was skipped, skip the text animation for the next pages
                # This works because the delay is reused when recursing
                delay = 0

            if skip_all: # if the delay between pages was skipped, skip remaining pages.
                return True # Since remaining pages were skipped, text was skipped.

            self.addinto_centred(y_pos, remaining_lines, delay, pager_delay) # recurse for the
            # remaining lines

            self.sleep_key(pager_delay)  # wait for the last page

            return skip or skip_all # if anything was skipped, return True

        # To add a delay between each line, we loop over each line
        for idx, line in enumerate(text.splitlines()):
            line = line.strip() # Remove whitespace at start and end

            middle_of_screen = self.renderer.max_x / 2
            middle_of_text = len(line) / 2

            # we need to round this to avoid passing a float to self.renderer.add_text
            x_pos = round(middle_of_screen - middle_of_text)
            correct_y_pos = y_pos + idx # Shift each new line downwards

            self.renderer.addtext(x_pos, correct_y_pos, line)
            self.refresh() # to view each line being added, we need to refresh the screen

            if line == "":
                continue # do not delay if the line is blank

            full_delay = self.sleep_key(delay) # full delay is True if the delay was not skipped
            if not full_delay: # if the delay was skipped make the delay 0 and do not wait for
                # following lines
                delay = 0

        return delay == 0 # If something was skipped, return True

    def addinto_all_centred(self, text: str, delay: float = 0, pager_delay: float = 2) -> bool:
        """
        Adds a text into the canvas, completely centred.

        For more documentation, see Scene.addinto_centred()

        :param text: The text to be displayed
        :param delay: How many seconds to wait between each line
        :param pager_delay: How many seconds to wait between each page.
        """
        line_count = len(text.splitlines())
        return self.addinto_centred(round(self.renderer.max_y / 2) - round(line_count / 2), text,
                                    delay,
                                    pager_delay)

    def refresh(self) -> None:
        """
        Refresh the screen, making sure that all modified characters are displayed correctly.
        :return:
        """
        self.renderer.refresh()

    def clear(self) -> None:
        """
        Clear the screen, and redraw the borders.
        """
        self.renderer.clear_screen()