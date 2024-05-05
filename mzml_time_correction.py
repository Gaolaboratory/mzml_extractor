import argparse
import re
import pandas as pd
import numpy as np
import random
import mstool
from scipy.signal import savgol_filter, find_peaks
import sys


def find_range_indexes(ndarray, start_value, end_value):
    """Finds the starting and ending indices for given start and end values within an array."""
    start_index = np.searchsorted(ndarray, start_value, side='left')
    end_index = np.searchsorted(ndarray, end_value, side='right') - 1
    return start_index, end_index


def psm_time_correction(mzml_file, psm_file, range_list):
    """Processes the given mzml and psm files to compute time corrections based on given ranges."""
    print(f"Reading mzml file: {mzml_file}")
    mzml_data, index_dict = mstool.read_mzml_ms1(mzml_file)
    print(f"Done reading mzml file, total ms1 spec: {len(index_dict)}")
    print(f"Retention time range from {mzml_data[0][0]} to {mzml_data[0][-1]} min")

    compression_method = 'gzip' if psm_file.endswith('.gz') else None
    df = pd.read_csv(psm_file, compression=compression_method, sep='\t')
    print(f"Done reading psm file, total psm: {len(df)}")

    common_peptides = set.intersection(*[set(df[(df['Retention'] >= start) & (df['Retention'] < end) & (df['Charge'] == 2)]['Peptide']) for start, end in range_list])
    sample = random.sample(list(common_peptides), int(len(common_peptides) * 0.1))
    print(f"Using {len(sample)} peptides for alignment")

    sample_ret_dict = {pep: [0] * len(range_list) for pep in sample}
    for idx, (start_time, end_time) in enumerate(range_list):
        for peptide in sample:
            peptide_data = df[(df['Retention'] >= start_time) & (df['Retention'] < end_time) & (df['Peptide'] == peptide)]
            median_rt = peptide_data['Retention'].median()
            mz_value = peptide_data['Calculated M/Z'].median()
            rt_min = median_rt / 60
            data_start, data_end = find_range_indexes(mzml_data[0], rt_min - 1, rt_min + 1)
            data_selected = mzml_data[:, data_start:data_end]
            min_mz, max_mz = mz_value * (1 - 20e-6), mz_value * (1 + 20e-6)
            data_selected = data_selected[:, (data_selected[1] > min_mz) & (data_selected[1] < max_mz)]

            if data_selected.shape[1] > 30:
                smooth_y = savgol_filter(data_selected[2], 13, 3)
                peaks, _ = find_peaks(smooth_y, height=smooth_y.max() / 2)
                if peaks.size > 0:
                    peak_time = data_selected[0, peaks[np.argmax(data_selected[2, peaks])]]
                    sample_ret_dict[peptide][idx] = peak_time

    time_diff_list = list(zip(*[sample_ret_dict[pep] for pep in sample if 0 not in sample_ret_dict[pep]]))
    time_diff_suggestion = [0]
    for i in range(len(range_list) - 1):
        time_diff = np.median([b - a for a, b in zip(time_diff_list[i], time_diff_list[i + 1])])
        print(f"Time difference between run {i + 1} and run {i + 2} is {time_diff}")
        time_diff_suggestion.append(time_diff_suggestion[-1] + round(time_diff * 60))
    time_diff_suggestion.append(round(mzml_data[0][-1] * 60))

    return sample, sample_ret_dict, time_diff_suggestion


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='python3 mzml_time_correction.py',
        description='This program helps you to correct the split time of mzml file',
        epilog='Gao lab mzml time correction 1.0, https://lab.gy, contact: yugao@uic.edu')
    parser.add_argument('-m', '--mzml_file', help='mzml file path')
    parser.add_argument('-p', '--psm_file', help='psm file in tsv format, see our example tsv file for the format, standard MSFragger output psm.tsv works')
    parser.add_argument('-t', '--time_split', help='time split in seconds')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    range_list = [tuple(map(float, i.split(','))) for i in re.findall(r"\((.*?)\)", args.time_split)]
    peptide_used_for_correction, correction_time_dict, time_diff_suggestion = psm_time_correction(args.mzml_file, args.psm_file, range_list)
    suggest_split = [(time_diff_suggestion[idx], time_diff_suggestion[idx+1]) for idx, val in enumerate(time_diff_suggestion[:-1])]
    print("measured split time for different run", suggest_split)
    print("suggested command to split the mzml file:\npython mzml_splitter_openms.py -i input.mzml -s [%s]" % ','.join([f"({a},{b})" for a, b in suggest_split]))
