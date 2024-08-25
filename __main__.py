#! /usr/bin/python3

import os
import sys

from src.logging_util import Log
from src.previewer import Previewer

if __name__ == "__main__":

    app_folder = os.path.expanduser('~/.config/previewer')
    if not os.path.exists(app_folder):
        os.makedirs(app_folder)

    Log.init(app_folder)

    current_dir = os.getcwd()
    target_file = None
    debug = False

    args = sys.argv

    is_zipped = args[0].endswith('.pyz')

    if "--debug" in args:
        debug = True
        args.remove("--debug")

    if len(args) > 1:
        current_dir = args[1]

        is_absolute = current_dir.startswith('/')

        if not is_absolute:
            if current_dir.startswith('~'):
                current_dir = os.path.expanduser(current_dir)
            elif current_dir.startswith("./"):
                current_dir = current_dir[2:]
            else:
                current_dir = os.path.abspath(current_dir)

        if not os.path.isdir(current_dir):
            target_file = current_dir
            current_dir = current_dir[:current_dir.rfind("/")]

        if not os.path.exists(current_dir):
            print("Invalid directory: " + current_dir, file=sys.stderr)
            current_dir = os.getcwd()

    app = Previewer(current_dir, target_file, debug, is_zipped)
    app.main()