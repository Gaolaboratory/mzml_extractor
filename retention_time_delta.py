import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from statistics import mean


def delta_retention_time(input_tsv_file, target_tsv_file):
    # adjusts the retention time of psm tsv files in the list to the input tsv file
    # based on the average difference in peptide retention times between the two psm files. 

    # first the input file is processed to add an "adjusted_time" which is the same as the retention, it's just for downstream compatibility
    ori_df = pd.read_csv(input_tsv_file, sep='\t', index_col=False)
    
    # drop duplicates
    ori_df = ori_df.drop_duplicates('Peptide', keep = False)

    # now process each file in the list
    new_df = pd.read_csv(target_tsv_file, sep = "\t", index_col = False)
    
    # drop duplicates
    new_df = new_df.drop_duplicates('Peptide', keep = False)
    
    # make the retention values floats to compare them
    ori_df['Retention'] = ori_df['Retention'].astype(float)
    new_df['Retention'] = new_df['Retention'].astype(float)
    
    # creating final df with only rentention times and differences and only looking at unique peptides (only identified once)
    merged_df = pd.merge(ori_df, new_df, on='Peptide', suffixes=('_df1', '_df2'))
    merged_df['retention_diff'] = merged_df['Retention_df2'] - merged_df['Retention_df1']
    final_df = merged_df[['Peptide','retention_diff', 'Retention_df1', 'Retention_df2']]
    final_df = final_df.drop_duplicates(subset='Peptide')
    
    dif_list = final_df['retention_diff'].tolist()
    
    # showing the average difference
    average_difference = mean(dif_list)
    print('compared to file:' + str(input_tsv_file))
    print('for file: ' + str(each_file))
    print( 'average difference is: ' + str(average_difference/60) + "mins")
        
        
        
    # adding column with the adjusted time
    new_df['Adjusted Retention'] = new_df['Retention'] + average_difference
    
    
    # showing the average difference in a hist plot
    bins = np.arange(min(dif_list), max(dif_list), 10) # fixed bin size
    plt.xlim([min(dif_list)-5, max(dif_list)+5])
    plt.hist(dif_list, bins=bins, alpha=0.5)
    plt.title('Time Difference (seconds)')
    plt.xlabel('Seconds (bin size = 5)')
    plt.ylabel('count')
    plt.show()
        
        
if __name__ == '__main__':
  # this function uses the search results from two files separated by the mzml_extractor using approximate total runtime and determine the delta between the assumed total runtime and actual runtime
  # for example, in our case, we have a 49s unexpected delay for our 35 min run, and we first split the files using exactly 35 minutes each, then search with MSFragger. The resulted psm.tsv files are used here to find that our delta runtime is 49s.
  delta_retention_time("C1_psm.tsv", "C2_psm.tsv")
