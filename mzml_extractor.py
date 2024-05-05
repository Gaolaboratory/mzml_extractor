import argparse
import mmap
import sys

# general function to find all string pairs in file using mmap
def find_string(mzml_read_fp, match_tag_start, match_tag_end):
    encoded_start_tag = match_tag_start.encode('utf-8')
    encoded_end_tag = match_tag_end.encode('utf-8')
    len_end_tag = len(match_tag_end)
    data_positions = []
    m = mmap.mmap(mzml_read_fp.fileno(), 0, access=mmap.ACCESS_READ)
    while (start := m.find(encoded_start_tag)) != -1:
        m.seek(start)
        ret_time_pos = m.find(b'accession="MS:1000016"') # scan start time
        m.seek(ret_time_pos)
        ret_time = float(m.read(100).decode('utf-8').split('value=')[1].split('"')[1])
        end = m.find(encoded_end_tag)
        data_positions.append((start, end + len_end_tag, ret_time))
        m.seek(end + len_end_tag)
    return data_positions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='python3 mzml_extractor.py',
        description='This program helps you to extract certain time portion of the mzml file into a new mzml file',
        epilog='Gao lab mzml extractor 1.0, https://lab.gy, contact: yugao@uic.edu')
    parser.add_argument('-i', '--input_file')
    parser.add_argument('-o', '--output_file')
    parser.add_argument('-s', '--start_time', help='start time in minute')
    parser.add_argument('-e', '--end_time', help='end time in minute, must be bigger than start time')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    start = float(args.start_time)
    end = float(args.end_time)
    print("Extracting %s from %s min to %s min to %s" % (args.input_file, start, end, args.output_file))
    data_positions = find_string(open(args.input_file), "<spectrum ", "</spectrum>")
    with open(args.output_file, 'wb') as fo, open(args.input_file, 'rb') as fin:
        fo.write(fin.read(data_positions[0][0]))
        time_range = [i for i in data_positions if start < i[2] < end]
        fin.seek(time_range[0][0])
        fo.write(fin.read(time_range[-1][1] - time_range[0][0]))
        fin.seek(data_positions[-1][1])
        fo.write(fin.read())
        print("Done")
