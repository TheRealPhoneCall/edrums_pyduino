#! /bin/bash

# Get the arguments
command=$1
board=$2

if [[ $command=='run' ]]; then
    echo "Executing platformio run command..."
    if [[ $board=='uno' ]]; then
        echo "Compiling code for arduino uno..."
        pio run -e uno
    elif [[ $board=='nano' ]]; then
        echo "Compiling code for arduino nano..."
        pio run -e nanoatmega328
    fi
elif [[ $command=='upload' ]]; then
    echo "Executing platformio upload command..."
    if [[ $board=='uno' ]]; then
        echo "Uploading code for arduino uno..."
        pio run -e uno --target upload
    elif [[ $board=='nano' ]]; then
        echo "Uploading code for arduino nano..."
        pio run -e nanoatmega328 --target upload
    fi
elif [[ $command=='monitor' ]]; then
    echo "Executing platformio device monitor..."
    pio device monitor    
fi