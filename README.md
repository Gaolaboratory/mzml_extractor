# mzml_extractor
Python script to extract mzml file from x minutes to y minutes, published with the "High throughput proteomics enabled by a fully automated dual-column liquid chromatography system coupled with mass spectrometry" manuscript (https://doi.org/10.26434/chemrxiv-2023-8lnlk)

![dual_column](https://github.com/Gaolaboratory/mzml_extractor/assets/114178668/c161891a-51b5-4678-9ad9-5f37d0daa4c0)


# mzml_splitter_openms.py
mzml_splitter_openms.py uses python openms library to split the continous mzml file into individual runs

Requirement: Python 3 installed; Pyopenms installed (pip install pyopenms)

Usage: python3 mzml_splitter_openms.py [-h] [-i INPUT_FILE] [-s SPLIT_TIME_ARRAY] [-p PREFIX]

Example 1: python mzml_splitter_openms.py -i input.mzML -s [(0,600),(600,1200),(1200,1800)]
This will split input.mzML into three files:
input_0.0-600.0.mzML
input_600.0-1200.0.mzML
input_1200.0-1800.0.mzML


Example 2: python mzml_splitter_openms.py -p dual_col -i input.mzML -s [(0,600),(600,1200),(1200,1800)]
This will split input.mzML into three files:
dual_col_0.0-600.0.mzML
dual_col _600.0-1200.0.mzML
dual_col _1200.0-1800.0.mzML


options:
  -h, --help            
  show this help message and exit
  
  -i INPUT_FILE, --input_file INPUT_FILE
  -p PREFIX, --prefix FILE_PREFIX
  -s SPLIT_TIME_ARRAY, --split_time_array SPLIT_TIME_ARRAY
  split time array in the format of [(0, 2400),(2400, 4800)], numbers are in seconds

Gao lab mzml splitter 1.0, https://lab.gy, contact: yugao@uic.edu


# mzml_extractor.py

mzml_extractor.py provides example code to extract specific spectra from a given mzml file, note that this script extract only part of the file, not including the index and other part of the mzml.


### U3000Nano_dual_column_10samples_method_60min.meth and U3000Nano_dual_column_10samples_method_35min.meth
These two are example instrument method files for QE-HF coupled with Ultimate 3000, showing how to set up the 10 consecutive runs with our dual-trap dual-column system.
