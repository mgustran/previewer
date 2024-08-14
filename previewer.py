#! /usr/bin/python3

import subprocess
import os
import curses
import sys
import time



def init_colors():
    # Start colors in curses
    curses.start_color()

    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)


class Previewer:

    # counter_files = 0
    # max_chars = 0
    #
    # dirlist_final = []
    # full_index = []
    height, width = 0, 0

    # scroll_top = 0
    scroll_top_preview = 0

    preview_file_path = None
    preview_file_content = []

    highlight_positions = [-1, -1, -1, -1]

    # cursor_x = 0
    # cursor_y = 0

    focus_on_preview = False
    initial_display = True

    # mouse_key_event_press = None

    msg_window = None
    show_help = False
    last_error = ''

    # tree_window = None
    tree_panel = None
    preview_window = None

    screen = None

    def __init__(self, root_dir, file_target, debug_statusbar=False):
        self.root_dir = root_dir  # instance variable unique to each instance
        self.root_dir = self.root_dir[:-1] if self.root_dir.endswith("/") else self.root_dir
        self.target_file = file_target
        self.initial_display = file_target is not None
        self.debug_statusbar = debug_statusbar

        self.tree_panel = PreviewerTree(self)
        self.keys = PreviewerKeys(self, self.tree_panel)
        self.mouse = PreviewerMouse(self, self.tree_panel)
        self.external = PreviewerExternal(self, self.tree_panel)


    def get_spaces_by_number(self, index, max_index):
        return max_index - len(str(index))

    def resize_windows(self):
        self.tree_panel.tree_window.resize(self.height - 1, self.tree_panel.max_chars + 2)
        self.preview_window.resize(self.height - 1, self.width - (self.tree_panel.max_chars + 4))
        self.preview_window.mvwin(0, self.tree_panel.max_chars + 4)

    def draw_main(self, stdscr):

        self.screen = stdscr

        k = 0
        # self.cursor_x = 0
        self.tree_panel.cursor_y = 0

        # Clear and refresh the screen for a blank canvas
        self.screen.clear()
        self.screen.refresh()

        # Setup mouse and keyboard inputs
        curses.curs_set(0)
        self.screen.keypad(1)
        # curses.mousemask(1)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        init_colors()



        # self.dirlist_final = self.reload_dirlist(self.root_dir)
        # self.tree_panel.full_index = self.dirlist_final.copy()
        # self.tree_panel.max_chars = len(max(self.tree_panel.full_index, key=lambda x: len(x["formatted_dirname"]))["formatted_dirname"])
        self.tree_panel.init_index()

        self.height, self.width = self.screen.getmaxyx()

        self.tree_panel.init_panel()
        # self.tree_window = curses.newwin(self.height - 1, self.tree_panel.max_chars + 2, 0, 0)
        self.preview_window = curses.newwin(self.height - 1, self.width - (self.tree_panel.max_chars + 4), 0, (self.tree_panel.max_chars + 4))

        # self.tree_window.bkgd(' ', curses.color_pair(3))

        subtitle_str = "Written by mgustran"

        # Loop until q pressed
        while (k != ord('q')):

            # Initialization
            self.screen.clear()
            self.tree_panel.tree_window.clear()
            self.preview_window.clear()
            self.height, self.width = self.screen.getmaxyx()

            if k == curses.KEY_DOWN:
                self.keys.key_down()

            elif k == curses.KEY_UP:
                self.keys.key_up()

            elif k == curses.KEY_RIGHT:
                self.keys.key_right()

            elif k == curses.KEY_LEFT:
                self.keys.key_left()

            elif k == 10:  # ENTER
                self.keys.key_enter()

            elif k == curses.KEY_BACKSPACE:
                self.external.open_file_with("cat", wait=True)

            elif k == 98:  # B
                self.external.open_file_with("vim")

            elif k == 110:  # N
                self.external.open_file_with("nano")

            elif k == 109:  # M
                self.external.open_file_with("micro")

            # todo: Redo with mouse event type
            elif k == 104:  # H / Help

                self.show_help = not self.show_help

            elif k == curses.KEY_MOUSE:
                self.mouse.key_mouse()

            # Declaration of strings
            # todo: remove debugging prints - key pressed
            title = f"Previewer"[:self.width-1]
            subtitle = f"{subtitle_str}"[:self.width-1]
            keystr = "Last key pressed: {}".format(k)[:self.width-1]

            statusbarstr = f"'q' : exit | ← → ↑ ↓ | 'b/n/m' : open in vim/nano/micro"

            if self.debug_statusbar:
                statusbarstr = statusbarstr + (" " * 30) + ("Key: {} | Pos: {}, {} | Len: {} | Idx: {} | Scrl1: {} | Scrl2: {} | hl: {}, {}, {}, {} | Colors: {} | err: {}"
                                .format(k, 0, self.tree_panel.cursor_y, str(len(self.tree_panel.full_index)), self.tree_panel.cursor_y + self.tree_panel.scroll_top, self.tree_panel.scroll_top, self.scroll_top_preview,
                                        self.highlight_positions[0], self.highlight_positions[1], self.highlight_positions[2], self.highlight_positions[3], curses.COLORS, self.last_error))
            # else:
            #     statusbarstr = f"'q' : exit | ← → ↑ ↓ | 'b/n/m' : open in vim/nano/micro"

            if k == 0:
                keystr = "No key press detected..."[:self.width-1]

            # Render status bar

            try:

                self.screen.attron(curses.color_pair(3))
                self.screen.addstr(self.height-1, 0, statusbarstr)
                self.screen.addstr(self.height-1, len(statusbarstr), (" " * (self.width - len(statusbarstr) - 1)))
                self.screen.attroff(curses.color_pair(3))
            except Exception as e:
                # todo: log error somewhere
                # self.screen.addstr(self.height - 1, 0, str(e))
                pass
            # Print Dir List
            try:

                # Resize Windows
                self.resize_windows()

                # Draw Separator
                for y in range(0, self.height - 1):
                    self.screen.addstr(y, self.tree_panel.max_chars + 2, "||")

                if self.target_file is not None:
                    self.external.open_file(self.target_file)
                    menu_index = next((idx for idx, x in enumerate(self.tree_panel.full_index) if x['file_path'] == self.target_file), None)
                    if menu_index is not None:
                        self.tree_panel.cursor_y = menu_index
                    self.target_file = None

                # Draw File Tree
                self.tree_panel.draw_file_tree()

                # Cursor in tree view, show initial display
                if self.initial_display:
                    # Draw Initial display
                    # Centering calculations
                    start_x_title = int((self.width // 2) - (len(title) // 2) - len(title) % 2)
                    start_x_subtitle = int((self.width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
                    start_x_keystr = int((self.width // 2) - (len(keystr) // 2) - len(keystr) % 2)
                    start_y = int((self.height // 2) - 2)

                    # Turning on attributes for title
                    self.preview_window.attron(curses.color_pair(2))
                    self.preview_window.attron(curses.A_BOLD)

                    # Rendering title
                    self.preview_window.addstr(start_y, start_x_title, title)

                    # Turning off attributes for title
                    self.preview_window.attroff(curses.color_pair(2))
                    self.preview_window.attroff(curses.A_BOLD)

                    # Print rest of text
                    self.preview_window.addstr(start_y + 1, start_x_subtitle, subtitle)
                    # self.screen.addstr(start_y + 2, (self.width // 2) - 2, '-' * 4)
                    # self.screen.addstr(start_y + 3, start_x_keystr, keystr)

                # Cursor outside tree view, show preview display
                else:
                    # Print File Preview
                    prefix_len = len(str(len(self.preview_file_content))) + 2
                    prefix_len_2 = len(str(len(self.preview_file_content)))
                    filename = self.preview_file_path
                    if self.root_dir != '/':
                        filename = self.preview_file_path.replace(self.root_dir, '')
                    filename = filename[1:] if filename.startswith('/') else filename
                    self.preview_window.attron(curses.color_pair(1))
                    self.preview_window.addstr(0, 3 + prefix_len, "Preview file: ")
                    self.preview_window.attron(curses.A_BOLD)
                    self.preview_window.addstr(0, 3 + prefix_len + len("Preview file: "), filename)
                    self.preview_window.attroff(curses.A_BOLD)
                    self.preview_window.addstr(1, 3 + prefix_len, len("Preview file: " + filename) * "-")
                    self.preview_window.attroff(curses.color_pair(1))

                    if self.scroll_top_preview > 0:
                        self.preview_window.attron(curses.color_pair(1))
                        self.preview_window.addstr(2, 2, "..")
                        self.preview_window.attroff(curses.color_pair(1))

                    # todo: fix line longer than terminal width
                    y = 0
                    for idx, line in enumerate(self.preview_file_content):
                        if self.scroll_top_preview > idx:
                            continue
                        if y <= (self.height - 6):
                            self.preview_window.attron(curses.color_pair(1))
                            self.preview_window.addstr(3 + y, 1, " " * self.get_spaces_by_number(idx + 1, prefix_len_2) + str(idx + 1) + " |")
                            self.preview_window.attroff(curses.color_pair(1))
                            self.preview_window.addstr(3 + y, 3 + prefix_len, line)
                            self.preview_window.attroff(curses.A_REVERSE)
                            y = y + 1

                        if y == (self.height - 5) and idx < len(self.preview_file_content) - 1:  # Last line
                            self.preview_window.attron(curses.color_pair(1))
                            self.preview_window.addstr(3 + y, 2, "..")
                            self.preview_window.attroff(curses.color_pair(1))
                            break

                    if self.mouse.mouse_key_event_press is False:
                        self.preview_window.chgat(self.highlight_positions[1], self.highlight_positions[0], 10, curses.A_REVERSE)


                if not self.focus_on_preview:
                    # self.preview_window.move(self.tree_panel.cursor_y, self.cursor_x)
                    self.preview_window.move(self.tree_panel.cursor_y, 0)

                if self.show_help:
                    self.msg_window = curses.newwin(7, 20, 10, 10)
                    self.msg_window.bkgd(' ', curses.color_pair(2))
                    # self.msg_window.
                    self.msg_window.attron(curses.color_pair(5))
                    self.msg_window.addstr(0, 0, "PATACAS")
                    self.msg_window.attroff(curses.color_pair(5))
                    self.msg_window.overlay(self.screen)
                    # self.init_colors()
                else:
                    if self.msg_window is not None:
                        self.msg_window.erase()
                        self.msg_window = None

            except Exception as e:
                print(e)
                self.last_error = str(e)
                # todo: log error somewhere
                pass

            # Refresh the screen
            self.screen.refresh()

            if self.tree_panel.tree_window is not None:
                self.tree_panel.tree_window.refresh()

            if self.preview_window is not None:
                self.preview_window.refresh()

            if self.msg_window is not None:
                self.msg_window.refresh()

            # Wait for next input
            k = self.screen.getch()

    def main(self, ):
        curses.wrapper(self.draw_main)


if __name__ == "__main__":

    from previewer_tree import PreviewerTree
    from previewer_keys import PreviewerKeys
    from previewer_mouse import PreviewerMouse
    from previewer_external import PreviewerExternal

    current_dir = os.getcwd()
    target_file = None
    debug = False

    args = sys.argv

    if "--debug" in args:
        debug = True
        args.remove("--debug")

    if len(args) > 1:
        current_dir = args[1]

        is_absolute = current_dir.startswith('/')

        if not is_absolute:
            if current_dir.startswith('~'):
                current_dir = os.path.expanduser(current_dir)
            elif current_dir.startswith("./"):
                current_dir = current_dir[2:]
            else:
                current_dir = os.path.abspath(current_dir)

        if not os.path.isdir(current_dir):
            target_file = current_dir
            current_dir = current_dir[:current_dir.rfind("/")]

        if not os.path.exists(current_dir):
            print("Invalid directory: " + current_dir, file=sys.stderr)
            current_dir = os.getcwd()

    app = Previewer(current_dir, target_file, debug)
    app.main()
