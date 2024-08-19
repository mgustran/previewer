import curses
import logging_util as logger
import threading

import culour_mod as culour

import previewer
from previewer_logo import PreviewerLogo
from pygments_converter import format_pygments_line


class PreviewerPreview:
    
    scroll_y = 0
    scroll_x = 0

    preview_file_path = None
    preview_file_content: list[list] = []

    highlight_positions = [-1, -1, -1, -1]
    
    preview_window = None
    preview_pad = None

    width, height = 0, 0

    thread = None

    def __init__(self, root: previewer.Previewer, initial_display=True):
        self.root = root
        self.initial_display = initial_display
        self.initial_display_animation = True
        self.logo = PreviewerLogo(self.root)


    def init_panel(self):
        # self.preview_window = curses.newwin(self.root.height - 1, self.root.width - (self.root.tree_panel.max_chars + 4), 0, (self.root.tree_panel.max_chars + 4))
        self.preview_window = curses.newwin(self.root.height - 1, self.root.width - (self.root.tree_panel.width), 0, (self.root.tree_panel.width))
        
    def draw_preview(self):

        self.height, self.width = self.preview_window.getmaxyx()
        
        if self.initial_display:

            # Start Animation
            if self.initial_display_animation and self.thread is None:
                self.thread = threading.Thread(target=self.logo.draw_logo_animated, name='tamare', args=(self.preview_window, self.height, self.width, ), daemon=True)
                self.thread.start()
            else:
                self.logo.draw_logo(self.preview_window, self.height, self.width)

            # working culour preformatted text, but breaks current pairs
            # culour.addstr(self.preview_window, start_y + 2, start_x_subtitle, "I \033[91mlove\033[0m Stack Overflow")
            # culour.addstr(self.preview_window, start_y + 3, start_x_subtitle, "\x1b[96mprint\x1b[0m \x1b[93m\"\x1b[0m\x1b[93mHello World\x1b[0m\x1b[93m\"\x1b[0m\x1b[90m\x1b[0m")

        # Cursor outside tree view, show preview display
        else:

            # Clear Animation
            if self.thread is not None:
                self.thread.join()
                self.thread = None
                self.preview_window.clear()

            if self.root.focus_on_preview:
                self.preview_window.attron(curses.color_pair(11))
            else:
                self.preview_window.attron(curses.A_DIM)
            self.preview_window.border()
            self.preview_window.attroff(curses.A_DIM)
            self.preview_window.attroff(curses.color_pair(11))

            # Create pad with line max length limit
            max_length = len(max(self.preview_file_content, key=lambda x: len(x[0]))[0])
            if self.preview_pad is None:
                self.preview_pad = curses.newpad(self.height - 3, max_length + 1)
            else:
                self.preview_pad.resize(self.height - 3, max_length + 1)
                self.preview_pad.clear()


            # Print File Preview
            prefix_len = len(str(len(self.preview_file_content)))
            filename = self.preview_file_path
            if self.root.root_dir != '/':
                filename = self.preview_file_path.replace(self.root.root_dir, '')
            filename = filename[1:] if filename.startswith('/') else filename

            self.preview_window.addstr(0, 10, ' File: ')
            self.preview_window.addstr(0, 17, filename + ' ')

            if self.scroll_y > 0:
                self.preview_window.attron(curses.color_pair(11))
                self.preview_window.addstr(1, 2, "..")
                self.preview_window.attroff(curses.color_pair(11))
            self.preview_window.addstr(1, prefix_len + 3, " ___", curses.color_pair(11))

            y = 0
            for idx, line in enumerate(self.preview_file_content):
                if self.scroll_y > idx:
                    continue
                if y <= (self.root.height - 6):
                    self.preview_window.attron(curses.color_pair(11))
                    self.preview_window.attron(curses.A_DIM)
                    self.preview_window.addstr(2 + y, 1, " " * self.get_spaces_by_number(idx + 1, prefix_len) + str(idx + 1) + " |")
                    self.preview_window.attroff(curses.color_pair(11))
                    self.preview_window.attroff(curses.A_DIM)
                    try:
                        culour.addstr(self.preview_pad, y, 0, format_pygments_line(line))
                    except Exception as e:
                        self.root.last_error = str(e)
                        logger.error(exception=e)
                    self.preview_window.attroff(curses.A_REVERSE)
                    y = y + 1

                if y == (self.root.height - 5) and idx < len(self.preview_file_content) - 1:  # Last line
                    self.preview_window.attron(curses.color_pair(11))
                    self.preview_window.addstr(2 + y, 2, "..")
                    self.preview_window.attroff(curses.color_pair(11))
                    break

            if self.root.mouse.mouse_key_event_press is False:
                self.preview_pad.chgat(self.highlight_positions[1], self.highlight_positions[0], 10, curses.A_REVERSE)

            # self.preview_pad.refresh(0, 0, 10, 10, 10, 10)

    def get_spaces_by_number(self, index, max_index):
        return (max_index - len(str(index))) + 1