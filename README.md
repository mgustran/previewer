# Previewer
Previewer is a file browser for linux terminal written in python with curses. \
It is meant to easily preview files, with a folder tree list as navigation system

![](https://github.com/mgustran/proxy-resources/blob/master/previewer-screenshot-2.png?raw=true)

### Features
- View Folder Tree
- Preview file
- Jump to vim / nano / micro editors with key B / N / M
- Select and copy with mouse and/or special keys - WIP
- Configurable action keys - WIP
- Git changes list (similar to intellij) - TODO

### Requirements
- Linux Terminal (I don't know if it works with Windows nor am I going to check it by now)
- Python 3

### Installation
- Method 1 - Install script (recommended) :\
`git clone https://github.com/mgustran/previewer.git` \
`cd previewer` \
`bash install.sh`


- Method 2 - Alias :\
`git clone https://github.com/mgustran/previewer.git` \
`cd previewer` \
`echo "alias preview=\"python3 $(pwd)/previewer.py\"" >> ~/.bashrc` 

### Usage
- `preview` Opens current working dir
- `preview <folder_path>` Opens dir passed as argument
- `preview <folder_path> --debug ` Change statusbar by developer useful info

\
Thanks to Clay McLeod for an [excellent example](https://gist.github.com/claymcleod/b670285f334acd56ad1c) to start learning python curses
