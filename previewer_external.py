import curses
import subprocess
import time

from previewer import Previewer
from previewer_preview import PreviewerPreview
from previewer_tree import PreviewerTree


class suspend_curses:
    """Context Manager to temporarily leave curses mode"""

    def __enter__(self):
        curses.endwin()

    def __exit__(self, exc_type, exc_val, tb):
        newscr = curses.initscr()
        newscr.addstr('Newscreen is %s\n' % newscr)
        newscr.refresh()
        curses.doupdate()


class PreviewerExternal:
    def __init__(self, root: Previewer, tree: PreviewerTree, preview: PreviewerPreview):
        self.root = root
        self.tree = tree
        self.preview = preview

    def open_file_with(self, app, wait=False):
        isdir = False
        if not self.root.focus_on_preview:
            isdir = self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_dir']
            dir1 = self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['file_path']
        else:
            dir1 = self.preview.preview_file_path

        if not isdir:
            with suspend_curses():
                subprocess.call([app, f"{dir1}"])
                if wait:
                    try:
                        while True:
                            time.sleep(0.5)
                    except KeyboardInterrupt:
                        self.root.screen.refresh()
                        pass

    def open_file(self, target):
        self.preview.preview_file_path = target
        self.root.focus_on_preview = True
        self.preview.initial_display = False

        lines7 = self.get_file_lines(target)
        try:
            file1 = open(self.preview.preview_file_path, 'r')
            # num_lines = sum(1 for _ in file1)
            # print(num_lines)
            self.preview.preview_file_content = file1.readlines()

            if len(self.preview.preview_file_content) < lines7:
                self.preview.preview_file_content.append('')
        except Exception as e:
            # todo: log somewhere
            pass

    def get_file_lines(self, filename):
        output = subprocess.check_output(('wc', '-l', filename))
        return int(output.decode().split(' ')[0]) + 1
