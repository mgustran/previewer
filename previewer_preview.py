import curses

import previewer

class PreviewerPreview:
    
    scroll_top_preview = 0

    preview_file_path = None
    preview_file_content = []

    highlight_positions = [-1, -1, -1, -1]
    
    preview_window = None

    def __init__(self, root: previewer.Previewer, initial_display=True):
        self.root = root
        self.initial_display = initial_display
        
    def init_panel(self):
        self.preview_window = curses.newwin(self.root.height - 1, self.root.width - (self.root.tree_panel.max_chars + 4), 0, (self.root.tree_panel.max_chars + 4))
        
    def draw_preview(self, key):

        title = f"Previewer"[:self.root.width - 1]
        subtitle = f"Written by mgustran"[:self.root.width - 1]
        keystr = "Last key pressed: {}".format(key)[:self.root.width - 1]
        
        if self.initial_display:
            # Draw Initial display
            # Centering calculations
            start_x_title = int((self.root.width // 2) - (len(title) // 2) - len(title) % 2)
            start_x_subtitle = int((self.root.width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
            start_x_keystr = int((self.root.width // 2) - (len(keystr) // 2) - len(keystr) % 2)
            start_y = int((self.root.height // 2) - 2)

            # Turning on attributes for title
            self.preview_window.attron(curses.color_pair(2))
            self.preview_window.attron(curses.A_BOLD)

            # Rendering title
            self.preview_window.addstr(start_y, start_x_title, title)

            # Turning off attributes for title
            self.preview_window.attroff(curses.color_pair(2))
            self.preview_window.attroff(curses.A_BOLD)

            # Print rest of text
            self.preview_window.addstr(start_y + 1, start_x_subtitle, subtitle)
            # self.screen.addstr(start_y + 2, (self.width // 2) - 2, '-' * 4)
            # self.screen.addstr(start_y + 3, start_x_keystr, keystr)

        # Cursor outside tree view, show preview display
        else:
            # Print File Preview
            prefix_len = len(str(len(self.preview_file_content))) + 2
            prefix_len_2 = len(str(len(self.preview_file_content)))
            filename = self.preview_file_path
            if self.root.root_dir != '/':
                filename = self.preview_file_path.replace(self.root.root_dir, '')
            filename = filename[1:] if filename.startswith('/') else filename
            self.preview_window.attron(curses.color_pair(1))
            self.preview_window.addstr(0, 3 + prefix_len, "Preview file: ")
            self.preview_window.attron(curses.A_BOLD)
            self.preview_window.addstr(0, 3 + prefix_len + len("Preview file: "), filename)
            self.preview_window.attroff(curses.A_BOLD)
            self.preview_window.addstr(1, 3 + prefix_len, len("Preview file: " + filename) * "-")
            self.preview_window.attroff(curses.color_pair(1))

            if self.scroll_top_preview > 0:
                self.preview_window.attron(curses.color_pair(1))
                self.preview_window.addstr(2, 2, "..")
                self.preview_window.attroff(curses.color_pair(1))

            # todo: fix line longer than terminal width
            y = 0
            for idx, line in enumerate(self.preview_file_content):
                if self.scroll_top_preview > idx:
                    continue
                if y <= (self.root.height - 6):
                    self.preview_window.attron(curses.color_pair(1))
                    self.preview_window.addstr(3 + y, 1, " " * self.get_spaces_by_number(idx + 1, prefix_len_2) + str(
                        idx + 1) + " |")
                    self.preview_window.attroff(curses.color_pair(1))
                    self.preview_window.addstr(3 + y, 3 + prefix_len, line)
                    self.preview_window.attroff(curses.A_REVERSE)
                    y = y + 1

                if y == (self.root.height - 5) and idx < len(self.preview_file_content) - 1:  # Last line
                    self.preview_window.attron(curses.color_pair(1))
                    self.preview_window.addstr(3 + y, 2, "..")
                    self.preview_window.attroff(curses.color_pair(1))
                    break

            if self.root.mouse.mouse_key_event_press is False:
                self.preview_window.chgat(self.highlight_positions[1], self.highlight_positions[0], 10, curses.A_REVERSE)

    def get_spaces_by_number(self, index, max_index):
        return max_index - len(str(index))