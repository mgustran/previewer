
from previewer import Previewer
from previewer_preview import PreviewerPreview
from previewer_tree import PreviewerTree


class PreviewerKeys:
    # from previewer_tree import PreviewerTree

    def __init__(self, root: Previewer, tree: PreviewerTree, preview: PreviewerPreview):
        self.root = root
        self.tree = tree
        self.preview = preview

    def key_down(self):
        if not self.root.focus_on_preview:
            if self.tree.cursor_y < self.root.height - 4:
                if self.tree.cursor_y < len(self.tree.full_index) - 1:
                    self.tree.cursor_y = self.tree.cursor_y + 1
            else:
                if len(self.tree.full_index) - (self.tree.scroll_top + 1 if self.tree.scroll_top > 0 else 0) > (self.root.height - 4):
                    self.tree.scroll_top = self.tree.scroll_top + 1
        else:
            if (self.preview.scroll_top_preview + (self.root.height - 4)) > len(self.preview.preview_file_content):
                pass
            else:
                self.preview.scroll_top_preview = self.preview.scroll_top_preview + 1

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
            self.preview.scroll_top_preview = (self.preview.scroll_top_preview - 1) if self.preview.scroll_top_preview > 0 else self.preview.scroll_top_preview

    def key_right(self):
        if not self.root.focus_on_preview:
            self.preview.scroll_top_preview = 0
            # subtitle_str = "Trying to open " + [self.tree_panel.cursor_y + self.scroll_top]['file_path']
            if self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_dir']:
                self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_open'] = True
                dir_files = self.tree.reload_dirlist(
                    target_dir=self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top][
                        'file_path'])
                for idx, file in enumerate(dir_files):
                    self.tree.full_index.insert(self.tree.cursor_y + self.tree.scroll_top + (idx + 1),
                                                      file)
                self.tree.max_chars = len(
                    max(self.tree.full_index, key=lambda x: len(x["formatted_dirname"]))["formatted_dirname"])
            else:
                self.root.external.open_file(
                    self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['file_path'])

    def key_left(self):
        if not self.root.focus_on_preview:
            # subtitle_str = "Trying to close " + self.tree_panel.full_index[self.tree_panel.cursor_y + self.scroll_top]['file_path']
            if self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_dir']:
                self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top]['is_open'] = False
                self.tree.full_index = [f for f in self.tree.full_index if not f['file_path'].startswith(
                    self.tree.full_index[self.tree.cursor_y + self.tree.scroll_top][
                        'file_path'] + '/')]
            self.tree.max_chars = len(
                max(self.tree.full_index, key=lambda x: len(x["formatted_dirname"]))["formatted_dirname"])
        else:
            self.root.focus_on_preview = False
            # self.preview_file_path = None

    def key_enter(self):
        # subtitle_str = "Trying to reverse path from " + self.root_dir
        if not self.root.focus_on_preview and self.tree.cursor_y == -1 and self.root.root_dir != '/':
            # subtitle_str = "Trying to reverse path from " + self.root_dir
            self.root.root_dir = self.root.root_dir[0:self.root.root_dir.rfind('/')] if self.root.root_dir.rfind('/') != 0 else '/'
            # if self.root_dir.rfind('/') != 0 or len(self.root_dir) > 0 and self.root_dir.startswith("/"):
            self.tree.dirlist_final = self.tree.reload_dirlist(self.root.root_dir)
            self.tree.full_index = self.tree.dirlist_final.copy()
            self.tree.max_chars = len(max(self.tree.full_index, key=lambda x: len(x["formatted_dirname"]))["formatted_dirname"])
        else:
            pass
