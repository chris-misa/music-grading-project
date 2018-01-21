#!/bin/bash

for d in */ ; do
    cd "$d"
    echo "grading student $d"
    for f in * ; do
        cat "$f" >> output.txt
    done
    echo "done grading student $d"
    cd ../
done
