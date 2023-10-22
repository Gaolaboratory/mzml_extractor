# mzml_extractor
Python script to extract mzml file from x minutes to y minutes, published with the "High throughput proteomics enabled by a fully automated dual-column liquid chromatography system coupled with mass spectrometry" manuscript (https://doi.org/10.26434/chemrxiv-2023-8lnlk)

![dual_column](https://github.com/Gaolaboratory/mzml_extractor/assets/114178668/c161891a-51b5-4678-9ad9-5f37d0daa4c0)


# mzml_splitter_openms.py
mzml_splitter_openms.py uses python openms library to split the continous mzml file into individual runs

Requirement: Python 3 installed; Pyopenms installed (pip install pyopenms)

Usage: python3 mzml_splitter_openms.py [-h] [-i INPUT_FILE] [-s SPLIT_TIME_ARRAY]

Example: python mzml_splitter_openms.py -i input.mzml -s [(0,600),(600,1200),(1200,1800)]

options:
  -h, --help            
  show this help message and exit
  
  -i INPUT_FILE, --input_file INPUT_FILE
  
  -s SPLIT_TIME_ARRAY, --split_time_array SPLIT_TIME_ARRAY
  split time array in the format of [(0, 2400),(2400, 4800)], numbers are in seconds

Gao lab mzml splitter 1.0, https://lab.gy, contact: yugao@uic.edu
