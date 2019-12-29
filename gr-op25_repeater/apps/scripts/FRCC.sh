#!/bin/bash
cd /home/pi/op25/gr-op25_repeater/apps
./rx.py --args "rtl" -N 'LNA:47' -S 2400000 -f 772.99375e6 -o 25000 -q -1 -T trunk.tsv -O bluealsa:DEV=00:1D:43:BA:A8:34 -V -2 -U 2> stderr.2
