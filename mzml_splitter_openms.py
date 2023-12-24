import argparse
import re
import pyopenms as ms
import os
import time
import sys

def split_mzml_by_time(mzml_path, rt_ranges, prefix=""):
    ### rt_ranges should be a list of tuple to indicate the start and end time
    ### examples of rt_ranges: [(0,2400),(2400,4800)]
    ### the splited mzml files will be saved into the same path as orginal mzml file
    start_time = time.time()
    mzml_file = mzml_path
    rt_ranges = rt_ranges
    if prefix == "":
        prefix = os.path.basename(mzml_file)
    for i, (start, stop) in enumerate(rt_ranges):
        output_file = os.path.join(os.path.dirname(mzml_file), f"%s_{i + 1}_rt_{start}-{stop}.mzML"%prefix)
        exp = ms.MSExperiment()
        ms.MzMLFile().load(mzml_file, exp)
        print(time.time() - start_time)
        filtered_exp = ms.MSExperiment()
        j = 0
        for spectrum in exp.getSpectra():
            if start <= spectrum.getRT() <= stop:
                spectrum.setNativeID(f"scan={j+1}")
                filtered_exp.addSpectrum(spectrum)
                j+=1
        ms.MzMLFile().store(output_file, filtered_exp)
        print(i,j, (start, stop), time.time() - start_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='python3 mzml_splitter_openms.py',
        description='Example: python mzml_splitter_openms.py -i input.mzml -s [(0,600),(600,1200),(1200,1800)]',
        epilog='Gao lab mzml splitter 1.0, https://lab.gy, contact: yugao@uic.edu')
    parser.add_argument('-i', '--input_file')
    parser.add_argument('-s', '--split_time_array', help='split time array in the format of [(0, 2400),(2400, 4800)], numbers are in seconds')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    print("Extracting %s ..." % (args.input_file))
    range_list = [tuple(map(float, i.split(','))) for i in re.findall(r"\((.*?)\)", args.split_time_array)]
    split_mzml_by_time(args.input_file, range_list)
