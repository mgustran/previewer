#!/bin/bash

# give execution permissions
chmod +x previewer.py

# mkdir user bin folder and move script in
mkdir ~/bin/
cp previewer.py ~/bin/previewer

printf 'Would you like to add ~/bin to PATH (y/n)? '
read answer

if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Adding PATH export to ~/.bashrc"
    echo "export PATH=\"$PATH:$HOME/bin\"" >> ~/.bashrc
fi

