#! /usr/bin/python3

import subprocess
import os
import curses
import sys
import time


class suspend_curses():
    """Context Manager to temporarily leave curses mode"""

    def __enter__(self):
        curses.endwin()

    def __exit__(self, exc_type, exc_val, tb):
        newscr = curses.initscr()
        newscr.addstr('Newscreen is %s\n' % newscr)
        newscr.refresh()
        curses.doupdate()


class PreviewerFunctions:

    def __init__(self, root):
        self.root = root

    # def manage_input(self, key):

    def key_down(self):
        if self.root.cursor_y >= 0:
            if self.root.cursor_y < self.root.height - 2 and self.root.cursor_y < len(self.root.full_index) - 1:
                self.root.cursor_y = self.root.cursor_y + 1
            else:
                if len(self.root.full_index) - (self.root.scroll_top + 1 if self.root.scroll_top > 0 else 0) > (self.root.height - 2):
                    self.root.scroll_top = self.root.scroll_top + 1
        else:
            if (self.root.scroll_top_preview + (self.root.height - 4)) > len(self.root.preview_file_content):
                pass
            else:
                self.root.scroll_top_preview = self.root.scroll_top_preview + 1

    def key_up(self):
        if self.root.cursor_y >= 0:
            if self.root.cursor_y > 0:
                self.root.cursor_y = self.root.cursor_y - 1
            else:
                if self.root.scroll_top > 0:
                    self.root.scroll_top = self.root.scroll_top - 1
        else:
            self.root.scroll_top_preview = (self.root.scroll_top_preview - 1) if self.root.scroll_top_preview > 0 else self.root.scroll_top_preview


class Previewer:

    counter_files = 0
    max_chars = 0

    dirlist_final = []
    full_index = []
    height, width = 0, 0

    scroll_top = 0
    scroll_top_preview = 0

    preview_file_path = None
    preview_file_content = []

    highlight_positions = [-1, -1, -1, -1]

    def __init__(self, root_dir, debug_statusbar=False):
        self.root_dir = root_dir  # instance variable unique to each instance
        self.root_dir = self.root_dir[:-1] if self.root_dir.endswith("/") else self.root_dir
        self.functions = PreviewerFunctions(self)
        self.debug_statusbar = debug_statusbar

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
                "level": os.path.join(target_dir, x).replace(self.root_dir, "").count("/") - 1,
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


    def draw_index(self, stdscr):

        y = 0

        for idx, dir in enumerate(self.full_index):

            if idx < self.scroll_top:
                continue

            if y > (self.height - 2):
                continue

            extra_chars = 0
            if dir["is_dir"]:
                stdscr.attron(curses.A_BOLD)
                if dir["file_name"].startswith("."):
                    stdscr.attron(curses.A_DIM)
                dir["formatted_dirname"] = dir["formatted_dirname"].replace(" + " if dir["is_open"] else " - ", " - " if dir["is_open"] else " + ")
            if self.cursor_y == y:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, 0, dir["formatted_dirname"])
                extra_chars = self.max_chars - len(dir["formatted_dirname"])
                stdscr.addstr(y, len(dir["formatted_dirname"]), (" " * extra_chars) + "  ")
                stdscr.attroff(curses.color_pair(2))
            else:
                try:
                    stdscr.addstr(y, 0, dir["formatted_dirname"])
                    extra_chars = self.max_chars - len(dir["formatted_dirname"])
                    stdscr.addstr(y, len(dir["formatted_dirname"]), (" " * extra_chars) + "  ")
                except Exception as e:
                    # todo: log error somewhere
                    # print(e)
                    pass
            stdscr.attroff(curses.A_BOLD)
            stdscr.attroff(curses.A_DIM)

            stdscr.attron(curses.color_pair(4))
            stdscr.addstr(y, (len(dir["formatted_dirname"]) + len(" " * extra_chars) + 2), "|  |")
            stdscr.attroff(curses.color_pair(4))

            y = y + 1


    def get_spaces_by_number(self, index, max_index):
        return max_index - len(str(index))

    def draw_menu(self, stdscr):
        k = 0
        self.cursor_x = 0
        self.cursor_y = 0

        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()

        # Setup mouse and keyboard inputs
        curses.curs_set(0)
        stdscr.keypad(1)
        # curses.mousemask(1)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        # Start colors in curses
        curses.start_color()
        # curses.init_color(10, 400,   400,   900)  # Blue going to magenta
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        # curses.init_pair(4, 10, curses.COLOR_BLACK)

        self.dirlist_final = self.reload_dirlist(self.root_dir)
        self.full_index = self.dirlist_final.copy()
        self.max_chars = len(max(self.full_index, key=lambda x: len(x["formatted_dirname"]))["formatted_dirname"])

        subtitle_str = "Written by mgustran"

        # Loop until q pressed
        while (k != ord('q')):

            # Initialization
            stdscr.clear()
            self.height, self.width = stdscr.getmaxyx()

            if k == curses.KEY_DOWN:

                self.functions.key_down()

            elif k == curses.KEY_UP:

                self.functions.key_up()

            elif k == curses.KEY_RIGHT:

                if self.cursor_y >= 0:
                    self.scroll_top_preview = 0
                    subtitle_str = "Trying to open " + self.full_index[self.cursor_y + self.scroll_top]['file_path']
                    if self.full_index[self.cursor_y + self.scroll_top]['is_dir']:
                        self.full_index[self.cursor_y + self.scroll_top]['is_open'] = True
                        dir_files = self.reload_dirlist(target_dir=self.full_index[self.cursor_y + self.scroll_top]['file_path'])
                        for idx, file in enumerate(dir_files):
                            self.full_index.insert(self.cursor_y + self.scroll_top + (idx + 1), file)
                        self.max_chars = len(max(self.full_index, key=lambda x: len(x["formatted_dirname"]))["formatted_dirname"])
                    else:
                        self.preview_file_path = self.full_index[self.cursor_y + self.scroll_top]['file_path']
                        self.cursor_y = -1
                        try:
                            file1 = open(self.preview_file_path, 'r')
                            self.preview_file_content = file1.readlines()
                        except Exception as e:
                            # todo: log somewhere
                            pass

            elif k == curses.KEY_LEFT:

                if self.cursor_y >= 0:
                    subtitle_str = "Trying to close " + self.full_index[self.cursor_y + self.scroll_top]['file_path']
                    if self.full_index[self.cursor_y + self.scroll_top]['is_dir']:
                        self.full_index[self.cursor_y + self.scroll_top]['is_open'] = False
                        self.full_index = [f for f in self.full_index if not f['file_path'].startswith(self.full_index[self.cursor_y + self.scroll_top]['file_path'] + '/')]
                    self.max_chars = len(max(self.full_index, key=lambda x: len(x["formatted_dirname"]))["formatted_dirname"])
                else:
                    if self.preview_file_path is not None:
                        self.cursor_y = [idx for idx, f in enumerate(self.full_index) if f['file_path'] == self.preview_file_path][0] - self.scroll_top
                    else:
                        self.cursor_y = 0
                    self.preview_file_path = None

            elif k == curses.KEY_BACKSPACE:

                if not self.full_index[self.cursor_y + self.scroll_top]['is_dir']:

                    with suspend_curses():
                        subprocess.call(["cat", f"{self.full_index[self.cursor_y + self.scroll_top]['file_path']}"])
                        try:
                            while True:
                                time.sleep(0.5)
                        except KeyboardInterrupt:
                            stdscr.refresh()
                            pass

            elif k == 98:  # B

                isdir = False
                dir1 = None
                if self.cursor_y >= 0:
                    isdir = self.full_index[self.cursor_y + self.scroll_top]['is_dir']
                    dir1 = self.full_index[self.cursor_y + self.scroll_top]['file_path']
                else:
                    dir1 = self.preview_file_path

                if not isdir:

                    with suspend_curses():
                        subprocess.call(["vim", f"{dir1}"])

            elif k == 110:  # N

                isdir = False
                dir1 = None
                if self.cursor_y >= 0:
                    isdir = self.full_index[self.cursor_y + self.scroll_top]['is_dir']
                    dir1 = self.full_index[self.cursor_y + self.scroll_top]['file_path']
                else:
                    dir1 = self.preview_file_path

                if not isdir:

                    with suspend_curses():
                        subprocess.call(["nano", f"{dir1}"])

            elif k == 109:  # M

                isdir = False
                dir1 = None
                if self.cursor_y >= 0:
                    isdir = self.full_index[self.cursor_y + self.scroll_top]['is_dir']
                    dir1 = self.full_index[self.cursor_y + self.scroll_top]['file_path']
                else:
                    dir1 = self.preview_file_path

                if not isdir:

                    with suspend_curses():
                        # subprocess.call(["guake", "--split-vertical", "-e", f"micro {dir1}"])
                        subprocess.call(["micro", f"{dir1}"])

            # todo: Redo with mouse event type
            # elif k == 104:  # H / Highlight
            #
            #     if self.cursor_y == -1:
            #
            #         self.highlight_positions[0] = curses.getmouse()[2]

            elif k == curses.KEY_MOUSE:
                try:
                    mouse_key_event_press = None
                    mouse_event = curses.getmouse()

                    # add scroll function type
                    if mouse_event[4] == 65536:  # scroll up
                        self.functions.key_up()
                        # pass
                    elif mouse_event[4] == 2097152:  # scroll down
                        self.functions.key_down()
                        # pass

                    else:
                        if self.preview_file_path is not None:
                            if mouse_event[4] == 2:
                                mouse_key_event_press = True
                            elif mouse_event[4] == 1:
                                mouse_key_event_press = False
                            elif mouse_event[4] == 4:
                                self.highlight_positions = [-1, -1, -1, -1]

                            if mouse_key_event_press is not None:
                                prefix_len = len(str(len(self.preview_file_content))) + 2
                                self.highlight_positions[0 if mouse_key_event_press else 2] = mouse_event[1] - (self.max_chars + 10 + prefix_len)
                                self.highlight_positions[1 if mouse_key_event_press else 3] = mouse_event[2] - 3 + self.scroll_top_preview

                        else:
                            # stdscr.addstr(0, 50, str(mouse_event))
                            # stdscr.addstr(1, 50, str(mouse_key_event_press))
                            pass
                except Exception as e:
                    # todo: log error somewhere
                    stdscr.addstr(2, 50, "TAMARE: " + str(e))

            # Declaration of strings
            # todo: remove debugging prints - key pressed
            title = f"Previewer"[:self.width-1]
            subtitle = f"{subtitle_str}"[:self.width-1]
            keystr = "Last key pressed: {}".format(k)[:self.width-1]

            if self.debug_statusbar:
                statusbarstr = ("Key: {} | Pos: {}, {} | Len: {} | Idx: {} | Scrl1: {} | Scrl2: {} | hl: {}, {}, {}, {}"
                                .format(k, self.cursor_x, self.cursor_y, str(len(self.full_index)), self.cursor_y + self.scroll_top, self.scroll_top, self.scroll_top_preview,
                                        self.highlight_positions[0], self.highlight_positions[1], self.highlight_positions[2], self.highlight_positions[3]))
            else:
                statusbarstr = f"'q' : exit | ← → ↑ ↓ | 'b/n/m' : open in vim/nano/micro"

            if k == 0:
                keystr = "No key press detected..."[:self.width-1]

            # Render status bar

            try:

                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(self.height-1, 0, statusbarstr)
                stdscr.addstr(self.height-1, len(statusbarstr), (" " * (self.width - len(statusbarstr) - 1)))
                stdscr.attroff(curses.color_pair(3))
            except Exception as e:
                # todo: log error somewhere
                # stdscr.addstr(self.height - 1, 0, str(e))
                pass
            # Print Dir List
            try:
                self.draw_index(stdscr)

                # Cursor in tree view, show initial display
                if self.cursor_y >= 0:
                    # Draw Initial display
                    # Centering calculations
                    start_x_title = int((self.width // 2) - (len(title) // 2) - len(title) % 2)
                    start_x_subtitle = int((self.width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
                    start_x_keystr = int((self.width // 2) - (len(keystr) // 2) - len(keystr) % 2)
                    start_y = int((self.height // 2) - 2)

                    # Turning on attributes for title
                    stdscr.attron(curses.color_pair(2))
                    stdscr.attron(curses.A_BOLD)

                    # Rendering title
                    stdscr.addstr(start_y, start_x_title, title)

                    # Turning off attributes for title
                    stdscr.attroff(curses.color_pair(2))
                    stdscr.attroff(curses.A_BOLD)

                    # Print rest of text
                    stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
                    stdscr.addstr(start_y + 2, (self.width // 2) - 2, '-' * 4)
                    stdscr.addstr(start_y + 3, start_x_keystr, keystr)

                # Cursor outside tree view, show preview display
                else:
                    # Print File Preview
                    prefix_len = len(str(len(self.preview_file_content))) + 2
                    prefix_len_2 = len(str(len(self.preview_file_content)))
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(0, self.max_chars + 10 + prefix_len, "Preview file: " + self.preview_file_path)
                    stdscr.addstr(1, self.max_chars + 10 + prefix_len, len("Preview file: " + self.preview_file_path) * "-")
                    stdscr.attroff(curses.color_pair(1))

                    # todo: fix line longer than terminal width
                    y = 0
                    for idx, line in enumerate(self.preview_file_content):
                        if self.scroll_top_preview > idx:
                            continue
                        if y <= self.height - 5:
                            stdscr.attron(curses.color_pair(1))
                            stdscr.addstr(3 + y, self.max_chars + 8, " " * self.get_spaces_by_number(idx + 1, prefix_len_2) + str(idx + 1) + " |")
                            stdscr.attroff(curses.color_pair(1))
                            # if highlight_positions[] == y:
                            #     stdscr.attron(curses.A_REVERSE)
                            stdscr.addstr(3 + y, self.max_chars + 10 + prefix_len, line)
                            stdscr.attroff(curses.A_REVERSE)
                            y = y + 1


                if self.cursor_y >= 0:
                    stdscr.move(self.cursor_y, self.cursor_x)


            except Exception as e:
                # todo: log error somewhere
                pass

            # Refresh the screen
            stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()


    def main(self, ):
        curses.wrapper(self.draw_menu)


if __name__ == "__main__":
    current_dir = os.getcwd()
    debug = False

    if len(sys.argv) > 1:
        current_dir = sys.argv[1]

    if "--debug" in sys.argv:
        debug = True

    app = Previewer(current_dir, debug)
    app.main()
