#!/bin/sh

for file in `ls images/`; do
    python process_img.py -o processed -p images/${file} -f anime
done
