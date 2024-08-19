import curses
import os
import time

import logging_util as logger
import previewer


class PreviewerLogo:

    def __init__(self, root: previewer.Previewer):
        self.root = root


    def get_logo_file(self, height, width):
        logo = 'logo-ascii-0.txt'
        # if width >= 187 and height >= 22:
        #     logo = 'logo-ascii-5.txt'
        # if width >= 144 and height >= 12:
        #     logo = 'logo-ascii-4.txt'
        if width >= 93 and height >= 9:
            logo = 'logo-ascii-3.txt'
        elif 93 > width >= 63 and height >= 10:
            logo = 'logo-ascii-2.txt'
        elif 63 > width >= 42 and height >= 7:
            logo = 'logo-ascii-1.txt'
        return logo


    def draw_logo_animated(self, window, height, width):
        # height, width = window.getmaxyx()

        logo = self.get_logo_file(height, width)
        time.sleep(0.05)

        logger.info(f'drawing animated logo {logo} with h/w: {height}/{width}')

        start_x = [0, -5, -10, -15, -20, -25, -30, -35, -40, -45, -50, -55, -60, -65, -70, -75]
        finished = [False, False, False, False, False, False, False, False, False, False, False, False, False, ]

        complete = False
        logo_lines = self.open_internal_file_lines(f'logos/{logo}')
        logo_lines = [x.replace('{vs}', previewer.VERSION) for x in logo_lines]

        max_length = len(max(logo_lines, key=lambda x: len(x)))

        while not complete:

            for idx, line in enumerate(logo_lines):
                if start_x[idx] >= 0:
                    if start_x[idx] < len(line):

                        if idx == 0:
                            window.attron(curses.A_DIM)
                        if idx > 7:
                            window.attron(curses.color_pair(14))
                        elif idx > 3:
                            window.attron(curses.color_pair(15))
                        else:
                            window.attron(curses.color_pair(11))

                        window.addstr((int(height / 2) - 4) + idx,
                                      start_x[idx] + int((width - max_length) / 2), line[start_x[idx]])

                        window.attroff(curses.A_DIM)
                        window.attroff(curses.color_pair(11))
                        window.attroff(curses.color_pair(14))
                        window.attroff(curses.color_pair(15))
                    else:
                        finished[idx] = True

            window.noutrefresh()
            curses.doupdate()
            time.sleep(0.005)

            finish = True

            for idx, line in enumerate(logo_lines):
                start_x[idx] = start_x[idx] + 1
                if not finished[idx]:
                    finish = False

            complete = finish

        window.border()
        # stdscr.addstr(0, 10, 'Preview')

        window.noutrefresh()
        curses.doupdate()
        # stdscr.addstr(0, 50, "complete")

    def draw_logo(self, window, height, width):
        logo = self.get_logo_file(height, width)
        logo_lines = self.open_internal_file_lines(f'logos/{logo}')
        logo_lines = [x.replace('{vs}', previewer.VERSION) for x in logo_lines]

        logger.info(f'drawing logo {logo} with h/w: {height}/{width}')

        max_length = len(max(logo_lines, key=lambda x: len(x)))

        for idx, line in enumerate(logo_lines):
            if idx == 0:
                window.attron(curses.A_DIM)

            if idx > 7:
                window.attron(curses.color_pair(14))
            elif idx > 3:
                window.attron(curses.color_pair(15))
            else:
                window.attron(curses.color_pair(11))

            window.addstr((int(height / 2) - 4) + idx, int((width - max_length) / 2), line)

            window.attroff(curses.A_DIM)
            window.attroff(curses.color_pair(11))
            window.attroff(curses.color_pair(14))
            window.attroff(curses.color_pair(15))
        window.noutrefresh()
        curses.doupdate()
        window.border()

    def open_internal_file_lines(self, file):

        if self.root.is_zip:
            logger.info(f'opening zipped internal file {file}')
            import zipfile
            import io
            with zipfile.ZipFile(os.path.dirname(__file__)) as z:
                with z.open(f'{file }', 'r') as logo_file:
                    items_file = io.TextIOWrapper(logo_file)
                    # logo_lines = [x.replace('{vs}', VERSION) for x in items_file.readlines()]
                    logo_lines = [x for x in items_file.readlines()]
        else:
            logger.info(f'opening direct internal file {file}')
            with open(file, 'r') as logo_file:
                logo_lines = [x for x in logo_file.readlines()]

        return logo_lines