#!/bin/bash
cd /home/pi/op25/gr-op25_repeater/apps
#./rx.py --args "rtl" -N 'LNA:47' -S 2400000 -f 853.85000e6 -o 25000 -q -1 -T ColoradoDTRSTrunk.tsv -V -2 -O bluealsa:DEV=00:1D:43:BA:A8:34 -U -l 56111 2> stderr.2
./rx.py --args "rtl" -N 'LNA:47' -S 2400000 -f 853.85000e6 -o 25000 -q -1 -T ColoradoDTRSTrunk.tsv -V -2 -O hw:0,0 -U -l 56111 2> stderr.2


