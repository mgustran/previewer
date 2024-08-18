import curses
import logging_util as logger

from previewer import Previewer
from previewer_preview import PreviewerPreview
from previewer_tree import PreviewerTree


class PreviewerMouse:

    mouse_key_event_press = None

    def __init__(self, root: Previewer, tree: PreviewerTree, preview: PreviewerPreview):
        self.root = root
        self.tree = tree
        self.preview = preview

    def key_mouse(self):
        try:
            self.mouse_key_event_press = None
            mouse_event = curses.getmouse()

            # add scroll function type
            if mouse_event[4] == 65536:  # scroll up
                self.root.keys.key_up()

            elif mouse_event[4] == 2097152:  # scroll down
                self.root.keys.key_down()

            else:
                if self.preview.preview_file_path is not None:
                    if mouse_event[4] == 2:
                        self.mouse_key_event_press = True
                    elif mouse_event[4] == 1:
                        self.mouse_key_event_press = False
                    elif mouse_event[4] == 4:
                        self.root.highlight_positions = [-1, -1, -1, -1]

                    if self.mouse_key_event_press is not None:
                        prefix_len = len(str(len(self.preview.preview_file_content))) + 2
                        # original
                        # self.highlight_positions[0 if mouse_key_event_press else 2] = mouse_event[1] - (self.tree_panel.max_chars + 10 + prefix_len)
                        # self.highlight_positions[1 if mouse_key_event_press else 3] = mouse_event[2] - 3 + self.scroll_top_preview

                        self.preview.highlight_positions[0 if self.mouse_key_event_press else 2] = mouse_event[1]
                        self.preview.highlight_positions[1 if self.mouse_key_event_press else 3] = mouse_event[2]

        except Exception as e:
            self.root.last_error = str(e)
            logger.error(exception=e)
