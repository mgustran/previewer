#!/bin/bash

# Clean build and dist folders
if [ "$1" = "--fast" ]
then
  # remove all files in build folder except six.py, which comes from some dependency
   find ./build/ -maxdepth 1  ! -name 'six.py' -type f -exec rm -f {} +
else
  rm -rf build/*
fi
rm -rf build/logos
rm -rf dist/*

# Copy files to build folder
[ -d build ] || mkdir build
cp ./*.py build/
cp -r logos build/logos

# Install dependencies to build folder
if [ "$1" = "--fast" ]
then
  echo "Using deps already in build folder"
else
  python3 -m pip install -r requirements.txt --target build
fi


# Package App
[ -d dist ] || mkdir dist
python3 -m zipapp "$(pwd)/build" -o "$(pwd)/dist/previewer.pyz"

# Check if alias is already in .bashrc before adding it
if grep -Fxq "alias preview=\"python3 $(pwd)/dist/previewer.pyz\"" ~/.bashrc
then
    # code if found
    printf "alias found in ~/.bashrc, leaving as is\n"
else
  printf 'alias not found in ~/.bashrc.  Adding it\n'
  echo "alias preview=\"python3 $(pwd)/dist/previewer.pyz\"" >> ~/.bashrc
fi

exit 0
