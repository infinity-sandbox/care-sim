#!/bin/bash

# should run on local machine
# scp ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub applicare@20.110.94.64:~/.ssh/

chmod 600 /home/applicare/.ssh/id_ed25519
chmod 644 /home/applicare/.ssh/id_ed25519.pub

eval "$(ssh-agent -s)"
ssh-add /home/applicare/.ssh/id_ed25519

ssh -T git@bitbucket.org

############git config############
# git config --global user.name "Abel Mitiku"
# git config --global user.email "abelmgetnet@gmail.com"
# git config --global core.editor vim
# git config --global credential.helper cache
# git config --global credential.helper "cache --timeout=3600"
# git config --global --list