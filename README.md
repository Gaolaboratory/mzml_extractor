# mzml_extractor
Python script to extract mzml file from x minutes to y minutes, published with the "High throughput proteomics enabled by a fully automated dual-column liquid chromatography system coupled with mass spectrometry" manuscript (https://doi.org/10.26434/chemrxiv-2023-8lnlk)



**Purpose of the tool:** when using our dual-column dual-trap setup, the mass spectrometer is going to generate a continuous large raw file, which can then be converted by MSConvert to mzml file. This file contains all the scheduled runs as shown below. This tool aims to help the user to split these runs correctly into individual mzml files, so they can be searched separately. 

**Major considerations:** We found that at least on our instrument (Ultimate 3000), the reported running time is not entirely correct, there are some delays that could accumulate over time if not accounted for. Therefore, we wrote a script "*mzml_time_correction.py*" to detect and correct for this. This tool shall be used when establishing a new dual-column system. Specifically, multiple runs with the same standard mix should run on the dual-column system and then searched with the corresponding fasta. The resulting psm.tsv file can then be used together with the large mzML file to calculate the correct time shift.

![dual_column](https://github.com/Gaolaboratory/mzml_extractor/assets/114178668/c161891a-51b5-4678-9ad9-5f37d0daa4c0)



### mzml_time_correction.py

mzml_time_correction.py uses the original mzML file together with the search result file (psm.tsv or psm.tsv.gz, see our provided example) to correct for the unexpected and unreported delay in the LC system. It only needs to be used once for the first run with standard mix. Once the method is established, the same corrected retention time can be used for future run. This script does the following:

1. Read the MS1 part of the mzML file into data array, decoding the base64 encoded data may take some time
2. Find common peptides from the user supplied psm.tsv and the uncorrected retention time
3. Use about 10% (can be changed) of the common peptides as internal standards to find the optimal split time point
4. We use ±20ppm mass shift and ±1 minute as the tolerance to filter out MS1 data, and perform signal smoothing and peak finding
5. Clear peaks identified in all repeats will be used to correct for the retention time, suggestions will be given at the end to the users.

**Example:** 

```bash
python3 mzml_time_correction.py -m dual_column_elute_10_update_HeLa_6.mzML -p 60min_psm.tsv.gz -t [(0,3600),(3600,7200),(7200,10800),(10800,14400),(14400,18000),(18000,21600),(21600,25200),(25200,28800),(28800,32400),(32400,36000)] 
```

This will use the dual_column_elute_10_update_HeLa_6.mzML (provided in our PRIDE repository), search results: 60min_psm.tsv.gz, and the initial guess of the rough split time as input, to calculate the more precise split time to split multiple runs from the large mzML file.

**Options:**
  -h, --help            show this help message and exit
  -m MZML_FILE, --mzml_file MZML_FILE
                        mzml file path
  -p PSM_FILE, --psm_file PSM_FILE
                        psm file in tsv format, see our example tsv file for
                        the format, standard MSFragger output psm.tsv works
  -t TIME_SPLIT, --time_split TIME_SPLIT
                        time split in seconds

**Expected output:**

```python
Reading mzml file: /mnt/c/Users/bathy/Downloads/dual_column_elute_10_update_HeLa_6.mzML
Done reading mzml file, total ms1 spec: 42752
Retention time range from 0.004918958060443401 to 619.9982299804688 min
Done reading psm file, total psm: 135523
Using 251 peptides for alignment
Time difference between run 1 and run 2 is 59.77434539794922
Time difference between run 2 and run 3 is 61.68864440917969
Time difference between run 3 and run 4 is 59.74188232421875
Time difference between run 4 and run 5 is 61.678985595703125
Time difference between run 5 and run 6 is 59.76835632324219
Time difference between run 6 and run 7 is 61.57817077636719
Time difference between run 7 and run 8 is 59.76222229003906
Time difference between run 8 and run 9 is 61.568450927734375
Time difference between run 9 and run 10 is 59.93157958984375
measured split time for different run [(0, 3586), (3586, 7287), (7287, 10872), (10872, 14573), (14573, 18159), (18159, 21854), (21854, 25440), (25440, 29134), (29134, 32730), (32730, 37200)]
suggested command to split the mzml file:
python mzml_splitter_openms.py -i input.mzml -s [(0,3586),(3586,7287),(7287,10872),(10872,14573),(14573,18159),(18159,21854),(21854,25440),(25440,29134),(29134,32730),(32730,37200)]
```



### mzml_splitter_openms.py

mzml_splitter_openms.py uses python openms library to split the continous mzml file into individual runs

Requirement: Python 3 installed; Pyopenms installed (pip install pyopenms)

Usage: python3 mzml_splitter_openms.py [-h] [-i INPUT_FILE] [-s SPLIT_TIME_ARRAY]

**Example:** 

```bash
python mzml_splitter_openms.py -i input.mzML -s [(0,600),(600,1200),(1200,1800)]
```

This will split the input.mzML file to three files, using the time range given in seconds.

**Note:** there should be no space in the time range, some OS may require quote sign "[(0,600),(600,1200),(1200,1800)]"

**Options:**
  -h, --help   show this help message and exit

  -i INPUT_FILE, --input_file INPUT_FILE

  -s SPLIT_TIME_ARRAY, --split_time_array SPLIT_TIME_ARRAY  

split time array in the format of [(0, 2400),(2400, 4800)], numbers are in seconds

Gao lab mzml splitter 1.0, https://lab.gy, contact: yugao@uic.edu



### mzml_extractor.py

mzml_extractor.py provides example code to extract specific spectra from a given mzml file, note that this script extract only part of the file, not including the index and other part of the mzml.

**Example:** 

```bash
python mzml_extractor.py -i input.mzML -o output.mzML -s 60.0 -e 120.0
```

This will extract the 60-120 minutes part from input.mzML to output.mzML.

**Options:**

  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
  -s START_TIME, --start_time START_TIME 
                        start time in minute
  -e END_TIME, --end_time END_TIME
                        end time in minute, must be bigger than start time






### U3000Nano_dual_column_10samples_method_60min.meth and U3000Nano_dual_column_10samples_method_35min.meth
These two are example instrument method files for QE-HF coupled with Ultimate 3000, showing how to set up the 10 consecutive runs with our dual-trap dual-column system.
