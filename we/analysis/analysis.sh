#!/bin/bash

cp ../west.h5 west.h5.bak

python plot_score.py
python plot_rmsd.py

evince score.pdf
evince rmsd.pdf
