#!/bin/bash

# mkdir user bin folder and move script in
[ -d ~/bin/ ] || mkdir ~/bin/
cp previewer.py ~/bin/preview

# give execution permissions
chmod +x ~/bin/preview

status_msg="was installed correctly"

#if grep -Fxq "$FILENAME" ~/.bashrc
if grep -Fxq "export PATH=\"\$PATH:\$HOME/bin\"" ~/.bashrc || grep -Fxq "export PATH=\"\$HOME/bin:\$PATH\"" ~/.bashrc
then
    # code if found
    echo "\$HOME/bin found in \$PATH, leaving as is"
else
  printf '$HOME/bin not found in $PATH.  Would you like to add it (in .bashrc) (y/n)? '
  read answer

  if [ "$answer" != "${answer#[Yy]}" ] ;
  then
      echo "Adding PATH export to ~/.bashrc"
      echo "export PATH=\"\$PATH:\$HOME/bin\"" >> ~/.bashrc
  else
    status_msg="may not be installed correctly"
  fi
fi

echo "previewer $status_msg, check it with command preview"

#source "$HOME/.bashrc"
exec bash  # workaround to reload bashrc, source command not work from inside script

exit 0



