#!/bin/bash

source `which virtualenvwrapper.sh`
source ~/start_py3cv4.sh
cd ~/Hobbyist_Curso/chapter16-drowsiness_detection/
python detect_drowsiness_v02.py --conf config/config.json