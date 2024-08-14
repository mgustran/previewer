#! /usr/bin/python3

import curses
import os

import previewer


class PreviewerTree:

    counter_files = 0
    max_chars = 0

    dirlist_final = []
    full_index = []

    scroll_top = 0

    cursor_x = 0
    cursor_y = 0

    tree_window = None

    # from previewer import Previewer
    def __init__(self, root: previewer.Previewer):
        self.root = root



    def init_index(self):
        self.dirlist_final = self.reload_dirlist(self.root.root_dir)
        self.full_index = self.dirlist_final.copy()
        self.max_chars = len(max(self.full_index, key=lambda x: len(x["formatted_dirname"]))["formatted_dirname"])

    def init_panel(self):
        self.tree_window = curses.newwin(self.root.height - 1, self.max_chars + 2, 0, 0)

    def reload_dirlist(self, target_dir):
        dirlist = os.listdir(target_dir)

        list_final = []

        for x in dirlist:
            is_dir = os.path.isdir(os.path.join(target_dir, x))

            file_info = {
                "is_dir": is_dir,
                "file_path": os.path.join(target_dir, x),
                "file_name": x,
                # "file_size": os.path.getsize(os.path.join(target_dir, x)) if not is_dir else 0,
                "level": os.path.join(target_dir, x).replace(self.root.root_dir, "").count("/") - 1,
                "is_open": False,
            }

            signal = ("  " * file_info['level']) + (" - " if file_info['is_open'] else " + ")
            formatted_dirname = (signal if file_info['is_dir'] else ("   " + "  " * file_info['level'])) + file_info['file_name']
            file_info["formatted_dirname"] = formatted_dirname

            list_final.append(file_info)
            self.counter_files += 1

        sublist1 = sorted([x for x in list_final if x["is_dir"]], key=lambda z: z["file_name"])
        sublist2 = sorted([x for x in list_final if not x["is_dir"]], key=lambda z: z["file_name"])

        return sublist1 + sublist2

    def draw_file_tree(self):

        root_dirname = os.path.basename(self.root.root_dir) if self.root.root_dir != '/' else '/'

        self.tree_window.attron(curses.A_BOLD)
        if self.cursor_y == -1:
            self.tree_window.attron(curses.color_pair(2))

        self.tree_window.addstr(0, 0, " .. ")
        self.tree_window.attroff(curses.A_BOLD)
        extra_chars = self.max_chars - len(" .. ")
        # self.tree_window.attron(curses.color_pair(4))
        # self.tree_window.addstr(0, len(" .. "), (" " * extra_chars) + "  ||")
        # self.tree_window.attroff(curses.color_pair(4))
        self.tree_window.attroff(curses.color_pair(2))

        self.tree_window.attron(curses.color_pair(5))
        self.tree_window.attron(curses.A_BOLD)
        self.tree_window.addstr(1, 0, " " + root_dirname)
        self.tree_window.attroff(curses.A_BOLD)
        extra_chars = self.max_chars - (len(root_dirname) + 1)
        self.tree_window.attroff(curses.color_pair(5))

        y = 0

        for idx, dir in enumerate(self.full_index):

            if idx < self.scroll_top:
                continue

            if y > (self.root.height - 4):
                continue

            extra_chars = 0
            if dir["is_dir"]:
                self.tree_window.attron(curses.A_BOLD)
                if dir["file_name"].startswith("."):
                    self.tree_window.attron(curses.A_DIM)
                dir["formatted_dirname"] = dir["formatted_dirname"].replace(" + " if dir["is_open"] else " - ", " - " if dir["is_open"] else " + ")
            if self.cursor_y == y:
                if self.root.focus_on_preview:
                    self.tree_window.attron(curses.A_DIM)
                    self.tree_window.attron(curses.color_pair(1))
                else:
                    self.tree_window.attron(curses.color_pair(2))
                self.tree_window.addstr(y + 2, 0, dir["formatted_dirname"])
                extra_chars = self.max_chars - len(dir["formatted_dirname"])
                self.tree_window.addstr(y + 2, len(dir["formatted_dirname"]), (" " * extra_chars) + "  ")
                self.tree_window.attroff(curses.color_pair(2))
                self.tree_window.attroff(curses.color_pair(1))
            else:
                try:
                    if dir["file_path"] == self.root.preview_file_path:
                        self.tree_window.attron(curses.color_pair(1))
                        self.tree_window.attron(curses.A_DIM)
                    else:
                        self.tree_window.attron(curses.color_pair(6))
                    self.tree_window.addstr(y + 2, 0, dir["formatted_dirname"])
                    extra_chars = self.max_chars - len(dir["formatted_dirname"])
                    self.tree_window.addstr(y + 2, len(dir["formatted_dirname"]), (" " * extra_chars) + "  ")
                    self.tree_window.attron(curses.color_pair(1))
                    self.tree_window.attron(curses.color_pair(6))
                    self.tree_window.attron(curses.A_DIM)
                except Exception as e:
                    # todo: log error somewhere
                    # print(e)
                    pass
            self.tree_window.attroff(curses.A_BOLD)
            self.tree_window.attroff(curses.A_DIM)

            y = y + 1
