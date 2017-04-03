#! /bin/bash

# Print starting programs
STRING="Fixing local git server"
echo $STRING

git config --global pack.windowMemory "200m"
git config --global pack.threads "1"
git config --global pack.packSizeLimit "200m"