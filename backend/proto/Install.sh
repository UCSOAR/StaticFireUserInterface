#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ]; then
    brew install protobuf   
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    apt install protobuf
fi