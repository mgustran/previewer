# Previewer
Previewer is a file browser for linux terminal written in python with curses. \
It is meant to easily preview files, with a folder tree list as navigation system

![](https://raw.githubusercontent.com/mgustran/proxy-resources/master/Peek%202024-08-19%2023-37.gif)

### Features
- View Folder Tree
- Preview non-binary files
- Jump to vim / nano / micro editors with key B / N / M - Will migrate to configurable actions

### Requirements
- Any Linux Terminal (I don't know if it works with Windows nor am I going to check it by now)
- Python 3

### Installation
- ~~Method 1 - Install script (recommended) :~~  Deprecated: migrating to pyinstaller \
~~`git clone https://github.com/mgustran/previewer.git` \
`cd previewer` \
`bash install.sh`~~


- Method 2 - ZipApp & Alias :\
`git clone https://github.com/mgustran/previewer.git` \
`cd previewer` \
`bash install-alias.sh` \
 \* Can use `--fast` to skip dependency install, be sure to run it without 1st time 

### Usage
- `preview` Opens current working dir
- `preview <path>` Opens folder/file passed as argument
- `... --debug ` Add developer "useful" info to statusbar

### Licences
- GNU GPL, see LICENCE file
- Using a modified version of [culour](https://github.com/spellr/culour) (GNU GPL) to work with pygments library

\
Thanks to Clay McLeod for an [excellent example](https://gist.github.com/claymcleod/b670285f334acd56ad1c) to start learning python curses