#!/bin/bash

for d in */ ; do
    cd "$d"
    rm "output.txt"
    cd ../
done
