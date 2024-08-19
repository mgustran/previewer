#! /usr/bin/python3

import os
import curses
import sys
from datetime import datetime

import logging_util as logger

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

    msg_window = None
    show_help = False

    stats_window = None
    show_file_stats = None

    last_error = ''

    tree_panel = None
    preview_panel = None

    screen = None

    def __init__(self, root_dir, file_target, debug_statusbar=False, is_zip=False):

        from previewer_tree import PreviewerTree
        from previewer_preview import PreviewerPreview
        from previewer_keys import PreviewerKeys
        from previewer_mouse import PreviewerMouse
        from previewer_external import PreviewerExternal
        from previewer_logo import PreviewerLogo

        self.root_dir = root_dir  # instance variable unique to each instance
        self.root_dir = self.root_dir[:-1] if self.root_dir.endswith("/") else self.root_dir
        self.target_file = file_target
        self.debug_statusbar = debug_statusbar

        self.tree_panel = PreviewerTree(self)
        self.preview_panel = PreviewerPreview(self, initial_display=file_target is None)
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
                self.show_help = not self.show_help

            elif key == 102:  # F / FIle Stats
                self.show_file_stats = not self.show_file_stats

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
                logger.error(exception=e)
                pass

            if self.show_help:
                self.msg_window = curses.newwin(10, 38, int(self.height / 2) - 5, int(self.width / 2) - 19)
                self.msg_window.bkgd(' ', curses.color_pair(12))
                self.msg_window.border()
                self.msg_window.addstr(0, 17, "HELP", curses.color_pair(19))
                self.msg_window.addstr(1, 2, "Navigation", curses.color_pair(17))
                self.msg_window.addstr(1, 16, "← → ↑ ↓ ↲ ⭾ / mouse", curses.color_pair(18))
                self.msg_window.addstr(3, 2, "Alternate Panel Focus", curses.color_pair(17))
                self.msg_window.addstr(3, 32, "TAB", curses.color_pair(18))
                self.msg_window.addstr(4, 2, "Set Root Folder / Open File", curses.color_pair(17))
                self.msg_window.addstr(4, 31, "ENTER", curses.color_pair(18))
                self.msg_window.addstr(6, 2, "Select / Copy", curses.color_pair(17))
                self.msg_window.addstr(6, 17, "mouse drag / C", curses.color_pair(18))
                self.msg_window.addstr(6, 33, "WIP", curses.color_pair(19))
                self.msg_window.addstr(8, 2, "Open in", curses.color_pair(17))
                self.msg_window.addstr(8, 11, "vim: B  nano: N  micro: M", curses.color_pair(18))
            else:
                if self.msg_window is not None:
                    self.msg_window.erase()
                    self.msg_window = None

            if self.show_file_stats:

                file_name = self.preview_panel.preview_file_path if self.focus_on_preview else self.tree_panel.full_index[self.tree_panel.cursor_y]['file_path']
                stats = os.stat(file_name)

                # c_date = datetime.utcfromtimestamp(stats.st_ctime).strftime('%d/%m/%Y %H:%M:%S')
                m_date = datetime.utcfromtimestamp(stats.st_mtime).strftime('%d/%m/%Y %H:%M:%S')
                a_date = datetime.utcfromtimestamp(stats.st_atime).strftime('%d/%m/%Y %H:%M:%S')
                is_dir = os.path.isdir(file_name)

                self.stats_window = curses.newwin(12, 38, int(self.height / 2) - 5, int(self.width / 2) - 19)
                self.stats_window.bkgd(' ', curses.color_pair(12))
                self.stats_window.border()
                self.stats_window.addstr(0, 17, "STATS", curses.color_pair(19))
                self.stats_window.addstr(1, 2, "Location", curses.color_pair(17))
                self.stats_window.addstr(1, 11, file_name, curses.color_pair(18))
                self.stats_window.addstr(4, 2, "Modified", curses.color_pair(17))
                self.stats_window.addstr(4, 15, m_date, curses.color_pair(18))
                self.stats_window.addstr(6, 2, "Accessed", curses.color_pair(17))
                self.stats_window.addstr(6, 15, a_date, curses.color_pair(18))
                self.stats_window.addstr(8, 2, "Size", curses.color_pair(17))
                self.stats_window.addstr(8, 15, str(stats.st_size) + " bytes", curses.color_pair(18))
                self.stats_window.addstr(10, 2, "Type", curses.color_pair(17))
                self.stats_window.addstr(10, 15, "Folder" if is_dir else "File", curses.color_pair(18))
            else:
                if self.stats_window is not None:
                    self.stats_window.erase()
                    self.stats_window = None

            # Render status bar
            try:

                self.screen.attron(curses.color_pair(13))
                self.screen.addstr(self.height-1, 0, statusbarstr)
                self.screen.addstr(self.height-1, len(statusbarstr), (" " * (self.width - len(statusbarstr))))
                self.screen.attroff(curses.color_pair(13))
            except Exception as e:
                self.last_error = str(e)
                # logger.info(exception=e)
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

            if self.msg_window is not None:
                self.msg_window.refresh()

            if self.stats_window is not None:
                self.stats_window.refresh()

            # Wait for next input
            key = self.screen.getch()

    def main(self, ):
        curses.wrapper(self.draw_main)
