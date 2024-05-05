from lxml import etree
import base64
import numpy as np
import pyarrow as pa
import zlib

# MS accessions and default values

ms_access_data_encoding_dict = {"MS:1000519": "32i",
                                "MS:1000520": "16e",
                                "MS:1000521": "32f",
                                "MS:1000522": "64q",
                                "MS:1000523": "64d"}

ms_access_data_compression_dict = {"MS:1000576": "none",
                                   "MS:1000574": "zlib"}

ms_access_data_array_type_dict = {"MS:1000514": "mz",
                                  "MS:1000515": "int",
                                  "MS:1000516": "charge"}

precursor_value_dict = {'precursor_mz': 0.0,
                        'precursor_chg': 2,
                        'precursor_int': 0,
                        'ret_time': 0.0}

precursor_value_translate_dict = {'MS:1000744': 'precursor_mz',
                                  'MS:1000041': 'precursor_chg',
                                  'MS:1000042': 'precursor_int'}

data_type_ms_access = {"MS:1000519": "data_encoding",
                       "MS:1000520": "data_encoding",
                       "MS:1000521": "data_encoding",
                       "MS:1000522": "data_encoding",
                       "MS:1000523": "data_encoding",
                       "MS:1000576": 'data_compression',
                       "MS:1000574": 'data_compression',
                       "MS:1000514": "data_type",
                       "MS:1000515": "data_type",
                       "MS:1000516": "data_type"}

data_type_dict = {'data_encoding': '32f',
                  'data_compression': 'none',
                  'data_type': 'mz'}

data_type_ms_access_value = {"MS:1000519": "32i",
                             "MS:1000520": "16e",
                             "MS:1000521": "32f",
                             "MS:1000522": "64q",
                             "MS:1000523": "64d",
                             "MS:1000576": 'none',
                             "MS:1000574": 'zlib',
                             "MS:1000514": "mz",
                             "MS:1000515": "int",
                             "MS:1000516": "charge"}

np_dtype_numtype = {'i': np.int32, 'e': np.single, 'f': np.float32, 'q': np.int64, 'd': np.float64}

fields = [pa.field('spec_no', pa.int32()), pa.field('ret_time', pa.float32()), pa.field('mz', pa.float32()),
          pa.field('int', pa.float32()), pa.field('ms_level', pa.int8()), pa.field('precursor', pa.float32()),
          pa.field('charge', pa.int8()), pa.field('mass_bin', pa.int16())]  # , pa.field('global_spec_id', pa.int64())
table_schema = pa.schema(fields)

# default values
ms_level = 1
base_peak = 0
total_int = 0
ignore_list = []
ignore_set = set()


def base64_decoder(base64_data, number_fmt, compress_method, array_type):
    num_type = np_dtype_numtype[number_fmt[-1]]
    decode_base64 = base64.decodebytes(base64_data.encode('ascii'))
    if compress_method == 'zlib':
        decode_base64 = zlib.decompress(decode_base64)
    data = np.frombuffer(decode_base64, dtype=num_type)
    return data


def read_mzml_ms1(mzml_file):
    index_dict = {}
    with open(mzml_file) as fo:
        tree = etree.parse(fo)
        i = 0
        length_spec_no_list = [(int(j.get('defaultArrayLength')), int(j.get('id').split("scan=")[-1])) for j in tree.findall(".//run/spectrumList/spectrum", namespaces=tree.getroot().nsmap) if
                               'MS:1000579' in [i.get('accession') for i in j.getchildren()]]
        total_numbers = sum([i[0] for i in length_spec_no_list])
        spec_no_list = [i[1] for i in length_spec_no_list]
        data_array = np.zeros([3, total_numbers], dtype=np.float32)
        for each_spectrum in tree.findall(".//run/spectrumList/spectrum", namespaces=tree.getroot().nsmap):
            spec_no = int(each_spectrum.get('id').split("scan=")[-1])
            if int(each_spectrum.get('id').split("scan=")[-1]) in spec_no_list:
                spectrum_length = int(each_spectrum.get('defaultArrayLength'))
                if spectrum_length > 0:
                    for each_spectrum_cvParam in each_spectrum.getchildren():  # read ms level information
                        if each_spectrum_cvParam.tag == '{http://psi.hupo.org/ms/mzml}scanList':
                            for each_scanList_cvParam in each_spectrum_cvParam.find('scan', namespaces=tree.getroot().nsmap).getchildren():
                                ms_access = each_scanList_cvParam.get('accession')
                                if ms_access == 'MS:1000016':
                                    ret_time = float(each_scanList_cvParam.get('value'))

                    for each_binary_data_array in each_spectrum.findall('binaryDataArrayList/binaryDataArray', namespaces=tree.getroot().nsmap):
                        for each in each_binary_data_array.getchildren():
                            if each.tag == '{http://psi.hupo.org/ms/mzml}cvParam':
                                ms_access = each.get('accession')
                                if ms_access in data_type_ms_access:
                                    data_type_dict[data_type_ms_access[ms_access]] = data_type_ms_access_value[ms_access]
                            elif each.tag == '{http://psi.hupo.org/ms/mzml}binary':
                                b64_data = each.text
                        binary_data = base64_decoder(b64_data, data_type_dict['data_encoding'], data_type_dict['data_compression'], data_type_dict['data_type'])
                        if data_type_dict['data_type'] == 'mz':
                            data_array[1, i:i + spectrum_length] = binary_data
                        elif data_type_dict['data_type'] == 'int':
                            data_array[2, i:i + spectrum_length] = binary_data
                        data_array[0, i:i + spectrum_length] = np.full(spectrum_length, ret_time)
                    index_dict[spec_no] = (i, i + spectrum_length)
                    i += spectrum_length
    return data_array, index_dict
