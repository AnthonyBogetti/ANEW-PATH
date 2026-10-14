#!/bin/bash

cp west.h5 analysis/west.h5.bak

python analysis/plot_score.py
python analysis/plot_rmsd.py

evince analysis/score.pdf
evince analysis/rmsd.pdf
