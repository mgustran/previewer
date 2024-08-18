import curses
import logging_util as logger
import threading
import time

import culour_mod as culour

import previewer
from pygments_converter import format_pygments_line


class PreviewerPreview:
    
    scroll_top_preview = 0

    preview_file_path = None
    preview_file_content: list[list] = []

    highlight_positions = [-1, -1, -1, -1]
    
    preview_window = None

    width, height = 0, 0

    thread = None
    thread_stop = True

    def __init__(self, root: previewer.Previewer, initial_display=True):
        self.root = root
        self.initial_display = initial_display
        self.initial_display_animation = True

    def draw_logo_animated(self, stdscr):
        start_x = [0, -5, -10, -15, -20, -25, -30, -35, -40, -45, -50, -55, -60, -65, -70, -75]
        finished = [False, False, False, False, False, False, False, False, False, False, False, False, False, ]

        complete = False
        with open('test/logo-ascii-2.txt', 'r') as logo_file:

            logo_lines = logo_file.readlines()

            max_length = len(max(logo_lines, key=lambda x: len(x)))

            while not complete:

                for idx, line in enumerate(logo_lines):
                    if start_x[idx] >= 0:
                        if start_x[idx] < len(logo_lines[idx]):

                            if idx == 0:
                                stdscr.attron(curses.A_DIM)

                            if idx > 7:
                                stdscr.attron(curses.color_pair(14))
                            elif idx > 3:
                                stdscr.attron(curses.color_pair(15))
                            else:
                                stdscr.attron(curses.color_pair(11))

                            stdscr.addstr((int(self.height / 2) - 4) + idx,
                                          start_x[idx] + int((self.width - max_length) / 2), logo_lines[idx][start_x[idx]])

                            stdscr.attroff(curses.A_DIM)
                            stdscr.attroff(curses.color_pair(11))
                            stdscr.attroff(curses.color_pair(14))
                            stdscr.attroff(curses.color_pair(15))
                        else:
                            finished[idx] = True

                stdscr.noutrefresh()
                curses.doupdate()
                time.sleep(0.01)

                finish = True

                for idx, line in enumerate(logo_lines):
                    start_x[idx] = start_x[idx] + 1
                    if not finished[idx]:
                        finish = False

                complete = finish

            # stdscr.addstr(0, 50, "complete")
            stdscr.noutrefresh()
            curses.doupdate()

    def draw_logo(self):

        with open('test/logo-ascii-2.txt', 'r') as logo_file:

            logo_lines = logo_file.readlines()
            max_length = len(max(logo_lines, key=lambda x: len(x)))
            start_x = int((self.width - max_length) / 2)

            for idx, line in enumerate(logo_lines):
                if idx == 0:
                    self.preview_window.attron(curses.A_DIM)

                if idx > 7:
                    self.preview_window.attron(curses.color_pair(14))
                elif idx > 3:
                    self.preview_window.attron(curses.color_pair(15))
                else:
                    self.preview_window.attron(curses.color_pair(11))

                self.preview_window.addstr((int(self.height / 2) - 4) + idx, int((self.width - max_length) / 2), logo_lines[idx])

                self.preview_window.attroff(curses.A_DIM)
                self.preview_window.attroff(curses.color_pair(11))
                self.preview_window.attroff(curses.color_pair(14))
                self.preview_window.attroff(curses.color_pair(15))
                # stdscr.noutrefresh()
                # curses.doupdate()
                # time.sleep(0.01)



    def init_panel(self):
        self.preview_window = curses.newwin(self.root.height - 1, self.root.width - (self.root.tree_panel.max_chars + 4), 0, (self.root.tree_panel.max_chars + 4))
        
    def draw_preview(self, key):

        self.height, self.width = self.preview_window.getmaxyx()

        title = f"Previewer"[:self.root.width - 1]
        subtitle = f"Written by mgustran"[:self.root.width - 1]
        keystr = "Last key pressed: {}".format(key)[:self.root.width - 1]
        
        if self.initial_display:

            # Start Animation
            if self.initial_display_animation:
                self.thread = threading.Thread(target=self.draw_logo_animated, name='tamare', args=(self.preview_window,), daemon=True)
                self.thread_stop = False
                self.thread.start()
                self.initial_display_animation = False
            else:
                self.draw_logo()

            # working culour preformatted text, but breaks current pairs
            # culour.addstr(self.preview_window, start_y + 2, start_x_subtitle, "I \033[91mlove\033[0m Stack Overflow")
            # culour.addstr(self.preview_window, start_y + 3, start_x_subtitle, "\x1b[96mprint\x1b[0m \x1b[93m\"\x1b[0m\x1b[93mHello World\x1b[0m\x1b[93m\"\x1b[0m\x1b[90m\x1b[0m")

        # Cursor outside tree view, show preview display
        else:

            # Clear Animation
            if self.thread is not None:
                self.thread_stop = True
                self.thread.join()
                self.thread = None
                self.preview_window.clear()


            # Print File Preview
            prefix_len = len(str(len(self.preview_file_content))) + 2
            prefix_len_2 = len(str(len(self.preview_file_content)))
            filename = self.preview_file_path
            if self.root.root_dir != '/':
                filename = self.preview_file_path.replace(self.root.root_dir, '')
            filename = filename[1:] if filename.startswith('/') else filename
            self.preview_window.attron(curses.color_pair(11))
            self.preview_window.addstr(0, 3 + prefix_len, "Preview file: ")
            self.preview_window.attron(curses.A_BOLD)
            self.preview_window.addstr(0, 3 + prefix_len + len("Preview file: "), filename)
            self.preview_window.attroff(curses.A_BOLD)
            self.preview_window.addstr(1, 3 + prefix_len, len("Preview file: " + filename) * "-")
            self.preview_window.attroff(curses.color_pair(11))

            if self.scroll_top_preview > 0:
                self.preview_window.attron(curses.color_pair(11))
                self.preview_window.addstr(2, 2, "..")
                self.preview_window.attroff(curses.color_pair(11))

            # todo: Add horizontal scroll
            # todo: Fix long line jumping to next line
            y = 0
            for idx, line in enumerate(self.preview_file_content):
                if self.scroll_top_preview > idx:
                    continue
                if y <= (self.root.height - 6):
                    self.preview_window.attron(curses.color_pair(11))
                    self.preview_window.addstr(3 + y, 0, " " * self.get_spaces_by_number(idx + 1, prefix_len_2) + str(idx + 1) + " |")
                    self.preview_window.attroff(curses.color_pair(11))
                    try:
                        culour.addstr(self.preview_window, 3 + y, 3 + prefix_len, format_pygments_line(line))
                    except Exception as e:
                        self.root.last_error = str(e)
                        logger.error(exception=e)
                    self.preview_window.attroff(curses.A_REVERSE)
                    y = y + 1

                if y == (self.root.height - 5) and idx < len(self.preview_file_content) - 1:  # Last line
                    self.preview_window.attron(curses.color_pair(11))
                    self.preview_window.addstr(3 + y, 2, "..")
                    self.preview_window.attroff(curses.color_pair(11))
                    break

            if self.root.mouse.mouse_key_event_press is False:
                self.preview_window.chgat(self.highlight_positions[1], self.highlight_positions[0], 10, curses.A_REVERSE)

    def get_spaces_by_number(self, index, max_index):
        return (max_index - len(str(index))) + 1