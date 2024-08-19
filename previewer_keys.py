import threading

from pynput.keyboard import Listener, Key

from previewer import Previewer
from previewer_preview import PreviewerPreview
from previewer_tree import PreviewerTree


class PreviewerKeys:

    def __init__(self, root: Previewer, tree: PreviewerTree, preview: PreviewerPreview):
        self.root = root
        self.tree = tree
        self.preview = preview

        self.keyboard_thread = None
        self.listener = None

        self.shift_pressed = False

        # Collect events until released
        if self.keyboard_thread is None:
            self.keyboard_thread = threading.Thread(target=self.init_keyboard, name='tamare2', args=(), daemon=True)
            self.keyboard_thread.start()

    def init_keyboard(self):
        with Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            self.listener = listener
            self.listener.join()

    def key_down(self):
        if not self.root.focus_on_preview:
            if self.tree.cursor_y < self.root.height - 6:
                if self.tree.cursor_y < len(self.tree.full_index) - 1:
                    self.tree.cursor_y = self.tree.cursor_y + 1
            else:
                if len(self.tree.full_index) - (self.tree.scroll_top + 1 if self.tree.scroll_top > 0 else 0) > (self.root.height - 6):
                    self.tree.scroll_top = self.tree.scroll_top + 1
        else:
            if (self.preview.scroll_y + (self.root.height - 4)) > len(self.preview.preview_file_content):
                pass
            else:
                self.preview.scroll_y = self.preview.scroll_y + 1

    def key_up(self):
        if not self.root.focus_on_preview:
            if self.tree.cursor_y > 0:
                self.tree.cursor_y = self.tree.cursor_y - 1
            else:
                if self.tree.scroll_top > 0:
                    self.tree.scroll_top = self.tree.scroll_top - 1
                elif self.tree.cursor_y == 0:
                    self.tree.cursor_y = -1
        else:
            self.preview.scroll_y = (self.preview.scroll_y - 1) if self.preview.scroll_y > 0 else self.preview.scroll_y

    def key_right(self):
        if not self.root.focus_on_preview and self.tree.cursor_y != -1:
            if self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_dir']:
                self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_open'] = True
                dir_files = self.tree.reload_dirlist(
                    target_dir=self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top][
                        'file_path'])
                for idx, file in enumerate(dir_files):
                    self.tree.full_index.insert(self.tree.cursor_y + self.tree.scroll_top + (idx + 1),
                                                      file)
                self.tree.reload_max_chars()
            else:
                self.preview.scroll_y = 0
                self.preview.scroll_x = 0
                self.root.external.open_file(
                    self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['file_path'])

        elif self.root.focus_on_preview:
            max_length = len(max(self.preview.preview_file_content, key=lambda x: len(x[0]))[0])
            prefix_len = len(str(len(self.preview.preview_file_content))) + 5
            if self.preview.scroll_x < ((max_length - self.preview.width) + prefix_len):
                self.preview.scroll_x = self.preview.scroll_x + 1

    def key_left(self):
        if not self.root.focus_on_preview:
            if self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_dir']:
                self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_open'] = False
                self.tree.full_index = [f for f in self.tree.full_index if not f['file_path'].startswith(
                    self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top][
                        'file_path'] + '/')]
            self.tree.reload_max_chars()
        else:
            if self.preview.scroll_x > 0:
                self.preview.scroll_x = self.preview.scroll_x - 1

    def key_enter(self):
        if not self.root.focus_on_preview:

            if self.tree.cursor_y == -1 and self.root.root_dir != '/':
                self.root.root_dir = self.root.root_dir[0:self.root.root_dir.rfind('/')] if self.root.root_dir.rfind('/') != 0 else '/'
                self.tree.cursor_y = 0
                self.tree.scroll_top = 0

            elif self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_dir']:
                self.root.root_dir = self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['file_path']
                self.tree.cursor_y = 0
                self.tree.scroll_top = 0

            else:
                self.preview.scroll_y = 0
                self.preview.scroll_x = 0
                self.root.external.open_file(
                    self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['file_path'])
                return

            self.tree.dirlist_final = self.tree.reload_dirlist(self.root.root_dir)
            self.tree.full_index = self.tree.dirlist_final.copy()
            self.tree.reload_max_chars()

    # @staticmethod
    def on_press(self, key):
        if key == Key.shift:
            self.shift_pressed = True


    # @staticmethod
    def on_release(self, key):
        if key == Key.shift:
            self.shift_pressed = False
