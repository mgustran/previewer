import curses
import subprocess
import time

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

from previewer import Previewer
from previewer_preview import PreviewerPreview
from previewer_tree import PreviewerTree

from pygments_converter import TERMINAL_CUSTOM_COLORS


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

        self.preview.preview_file_content = []

        lines7 = self.get_file_lines(target)
        try:
            file1 = open(self.preview.preview_file_path, 'r')

            code1 = file1.read()
            code2 = code1.encode('utf-8')

            try:
                # formatter = TerminalFormatter(bg='dark')
                formatter = TerminalFormatter(bg='dark', colorscheme=TERMINAL_CUSTOM_COLORS)
                lexer = get_lexer_for_filename(file1.name)
                result1 = highlight(code2, lexer, formatter)
            except ClassNotFound:
                result1 = code1
            file1.close()

            original = code1.split('\n')
            coloured = result1.split('\n')

            for idx, line in enumerate(original):
                self.preview.preview_file_content.append([line, coloured[idx]])

            if len(self.preview.preview_file_content) < lines7:
                self.preview.preview_file_content.append(['', ''])

        except Exception as e:
            self.root.last_error = str(e)

    def get_file_lines(self, filename):
        output = subprocess.check_output(('wc', '-l', filename))
        return int(output.decode().split(' ')[0]) + 1
