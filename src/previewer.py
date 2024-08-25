#! /usr/bin/python3

import curses

from src.logging_util import Log

VERSION = 'v0.2'   # Should be 4 char

def init_colors():
    # Start colors in curses
    curses.start_color()

    curses.init_pair(11, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(14, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(15, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(16, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(17, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(18, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(19, curses.COLOR_RED, curses.COLOR_BLUE)


class Previewer:

    height, width = 0, 0

    focus_on_preview = False

    last_error = ''

    screen = None

    def __init__(self, root_dir, file_target, debug_statusbar=False, is_zip=False):

        from src.previewer_tree import PreviewerTree
        from src.previewer_preview import PreviewerPreview
        from src.previewer_keys import PreviewerKeys
        from src.previewer_mouse import PreviewerMouse
        from src.previewer_external import PreviewerExternal
        from src.previewer_logo import PreviewerLogo
        from src.previewer_popups import PreviewerPopups

        self.root_dir = root_dir  # instance variable unique to each instance
        self.root_dir = self.root_dir[:-1] if self.root_dir.endswith("/") else self.root_dir
        self.target_file = file_target
        self.debug_statusbar = debug_statusbar

        self.tree_panel = PreviewerTree(self)
        self.preview_panel = PreviewerPreview(self, initial_display=file_target is None)
        self.popups = PreviewerPopups(self)
        self.keys = PreviewerKeys(self, self.tree_panel, self.preview_panel)
        self.mouse = PreviewerMouse(self, self.tree_panel, self.preview_panel)
        self.external = PreviewerExternal(self, self.tree_panel, self.preview_panel)
        self.logo = PreviewerLogo(self)

        self.is_zip = is_zip


    def resize_windows(self):
        self.tree_panel.tree_window.resize(self.height - 1, self.tree_panel.max_chars + 2)
        self.preview_panel.preview_window.resize(self.height - 1, self.width - (self.tree_panel.max_chars + 2))
        self.preview_panel.preview_window.mvwin(0, self.tree_panel.max_chars + 2)

    def draw_main(self, stdscr):

        self.screen = stdscr

        key = 0

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

            elif key == 9:  # TAB
                self.focus_on_preview = not self.focus_on_preview

            elif key == 10:  # ENTER
                self.keys.key_enter()

            elif key == 98:  # B
                self.external.open_file_with("vim")

            elif key == 110:  # N
                self.external.open_file_with("nano")

            elif key == 109:  # M
                self.external.open_file_with("micro")

            elif key == 104:  # H / Help
                self.popups.show_help = not self.popups.show_help

            elif key == 102:  # F / FIle Stats
                self.popups.show_file_stats = not self.popups.show_file_stats

            # todo: Add show hidden files key

            elif key == curses.KEY_MOUSE:
                self.mouse.key_mouse()

            # elif key == curses.KEY_RESIZE:
                # self.width, self.height = self.screen.getmaxyx()
                # self.tree_panel.width, self.tree_panel.height = self.tree_panel.tree_window.getmaxyx()
                # self.preview_panel.width, self.preview_panel.height = self.preview_panel.preview_window.getmaxyx()

            statusbarstr = f"'q' : exit | 'h' : help"

            if self.debug_statusbar:
                statusbarstr = statusbarstr + (" " * 10) + ("w/h: {},{} | Key: {} | Pos: {}, {} | Len: {} | Idx: {} | Scrl1: {} | Scrl2: {} | hl: {}, {}, {}, {} | Colors: {} | err: {}"
                                .format(self.preview_panel.width, self.preview_panel.height, key, 0, self.tree_panel.cursor_y, str(len(self.tree_panel.full_index)),
                                        self.tree_panel.cursor_y + self.tree_panel.scroll_top, self.tree_panel.scroll_top,
                                        self.preview_panel.scroll_y,
                                        self.preview_panel.highlight_positions[0], self.preview_panel.highlight_positions[1],
                                        self.preview_panel.highlight_positions[2], self.preview_panel.highlight_positions[3],
                                        curses.COLORS, self.last_error))
            # Print Dir List
            try:

                # Resize Windows
                self.resize_windows()

                # Open File passed as argument
                if self.target_file is not None:
                    self.external.open_file(self.target_file)
                    menu_index = next((idx for idx, x in enumerate(self.tree_panel.full_index) if x['file_path'] == self.target_file), None)
                    if menu_index is not None:
                        self.tree_panel.cursor_y = menu_index
                    self.target_file = None

                # Draw File Tree Panel
                self.tree_panel.draw_file_tree()

                # Draw Preview Panel
                self.preview_panel.draw_preview()

            except Exception as e:
                self.last_error = str(e)
                Log.error(exception=e)
                # tb = traceback.format_exc()
                print('tanma')
                # Log.error(traceback.format_exc())


            self.popups.validate_and_render_popups()

            # Render status bar
            try:

                self.screen.attron(curses.color_pair(13))
                self.screen.addstr(self.height-1, 0, statusbarstr)
                self.screen.addstr(self.height-1, len(statusbarstr), (" " * (self.width - len(statusbarstr))))
                self.screen.attroff(curses.color_pair(13))
            except Exception as e:
                self.last_error = str(e)
                # Log.info(exception=e)
                # logging.error(e)
                pass

            # Refresh the screen
            self.screen.refresh()

            if self.tree_panel.tree_window is not None:
                self.tree_panel.tree_window.refresh()

            if self.preview_panel.preview_window is not None:
                self.preview_panel.preview_window.refresh()

            if self.preview_panel.preview_pad is not None:
                prefix_len = len(str(len(self.preview_panel.preview_file_content))) + 4
                self.preview_panel.preview_pad.refresh(0, self.preview_panel.scroll_x, 2, self.tree_panel.width + prefix_len, self.height - 3, self.width - 2)

            if self.popups.msg_window is not None:
                self.popups.msg_window.refresh()

            if self.popups.stats_window is not None:
                self.popups.stats_window.refresh()

            # Wait for next input
            key = self.screen.getch()

    def main(self, ):
        curses.wrapper(self.draw_main)
