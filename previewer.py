#! /usr/bin/python3

import os
import curses
import sys


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
    # scroll_top_preview = 0
    #
    # preview_file_path = None
    # preview_file_content = []
    #
    # highlight_positions = [-1, -1, -1, -1]

    # cursor_x = 0
    # cursor_y = 0

    focus_on_preview = False
    # initial_display = True

    # mouse_key_event_press = None

    msg_window = None
    show_help = False
    last_error = ''

    # tree_window = None
    tree_panel = None
    preview_panel = None

    screen = None

    def __init__(self, root_dir, file_target, debug_statusbar=False):
        self.root_dir = root_dir  # instance variable unique to each instance
        self.root_dir = self.root_dir[:-1] if self.root_dir.endswith("/") else self.root_dir
        self.target_file = file_target
        self.debug_statusbar = debug_statusbar

        self.tree_panel = PreviewerTree(self)
        self.preview_panel = PreviewerPreview(self, initial_display=file_target is None)
        self.keys = PreviewerKeys(self, self.tree_panel, self.preview_panel)
        self.mouse = PreviewerMouse(self, self.tree_panel, self.preview_panel)
        self.external = PreviewerExternal(self, self.tree_panel, self.preview_panel)


    def resize_windows(self):
        self.tree_panel.tree_window.resize(self.height - 1, self.tree_panel.max_chars + 2)
        self.preview_panel.preview_window.resize(self.height - 1, self.width - (self.tree_panel.max_chars + 4))
        self.preview_panel.preview_window.mvwin(0, self.tree_panel.max_chars + 4)

    def draw_main(self, stdscr):

        self.screen = stdscr

        key = 0
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

        self.height, self.width = self.screen.getmaxyx()

        self.tree_panel.init_index()
        self.tree_panel.init_panel()

        self.preview_panel.init_panel()

        # Loop until q pressed
        while key != ord('q'):

            # Initialization
            self.screen.clear()
            self.tree_panel.tree_window.clear()
            self.preview_panel.preview_window.clear()
            self.height, self.width = self.screen.getmaxyx()

            if key == curses.KEY_DOWN:
                self.keys.key_down()

            elif key == curses.KEY_UP:
                self.keys.key_up()

            elif key == curses.KEY_RIGHT:
                self.keys.key_right()

            elif key == curses.KEY_LEFT:
                self.keys.key_left()

            elif key == 10:  # ENTER
                self.keys.key_enter()

            elif key == curses.KEY_BACKSPACE:
                self.external.open_file_with("cat", wait=True)

            elif key == 98:  # B
                self.external.open_file_with("vim")

            elif key == 110:  # N
                self.external.open_file_with("nano")

            elif key == 109:  # M
                self.external.open_file_with("micro")

            # todo: Redo with mouse event type
            elif key == 104:  # H / Help

                self.show_help = not self.show_help

            elif key == curses.KEY_MOUSE:
                self.mouse.key_mouse()

            statusbarstr = f"'q' : exit | ← → ↑ ↓ ↲ | 'b/n/m' : open in vim/nano/micro"

            if self.debug_statusbar:
                statusbarstr = statusbarstr + (" " * 30) + ("Key: {} | Pos: {}, {} | Len: {} | Idx: {} | Scrl1: {} | Scrl2: {} | hl: {}, {}, {}, {} | Colors: {} | err: {}"
                                .format(key, 0, self.tree_panel.cursor_y, str(len(self.tree_panel.full_index)),
                                        self.tree_panel.cursor_y + self.tree_panel.scroll_top, self.tree_panel.scroll_top,
                                        self.preview_panel.scroll_top_preview,
                                        self.preview_panel.highlight_positions[0], self.preview_panel.highlight_positions[1],
                                        self.preview_panel.highlight_positions[2], self.preview_panel.highlight_positions[3],
                                        curses.COLORS, self.last_error))

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
                self.preview_panel.draw_preview(key)

                # todo: wtf is this
                # if not self.focus_on_preview:
                #     # self.preview_window.move(self.tree_panel.cursor_y, self.cursor_x)
                #     self.preview_panel.preview_window.move(self.tree_panel.cursor_y, 0)

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

            if self.preview_panel.preview_window is not None:
                self.preview_panel.preview_window.refresh()

            if self.msg_window is not None:
                self.msg_window.refresh()

            # Wait for next input
            key = self.screen.getch()

    def main(self, ):
        curses.wrapper(self.draw_main)


if __name__ == "__main__":

    from previewer_tree import PreviewerTree
    from previewer_preview import PreviewerPreview
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
