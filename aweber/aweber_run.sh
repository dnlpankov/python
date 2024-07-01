#!/bin/bash

# Activate the Conda environment
source /home/deploy/miniconda3/etc/profile.d/conda.sh
conda activate aweber

# Run the Python script
python /home/deploy/python/aweber/get_data.py

