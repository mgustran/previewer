

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