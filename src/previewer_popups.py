import curses
import os
from datetime import datetime

from src.previewer import Previewer


class PreviewerPopups:

    msg_window = None
    show_help = False

    stats_window = None
    show_file_stats = False

    def __init__(self, root: Previewer):
        self.root = root

    def validate_and_render_popups(self):
        if self.show_help:
            self.msg_window = curses.newwin(10, 38, int(self.root.height / 2) - 5, int(self.root.width / 2) - 19)
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

            file_name = self.root.preview_panel.preview_file_path if self.root.focus_on_preview else \
            self.root.tree_panel.full_index[self.root.tree_panel.cursor_y]['file_path']
            stats = os.stat(file_name)

            m_date = datetime.utcfromtimestamp(stats.st_mtime).strftime('%d/%m/%Y %H:%M:%S')
            a_date = datetime.utcfromtimestamp(stats.st_atime).strftime('%d/%m/%Y %H:%M:%S')
            is_dir = os.path.isdir(file_name)

            self.stats_window = curses.newwin(12, 38, int(self.root.height / 2) - 5, int(self.root.width / 2) - 19)
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
