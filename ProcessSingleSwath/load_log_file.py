import pandas as pd
import numpy as np

def read_log(filename):
    rows_to_skip = np.arange(51)
    data = pd.read_csv(filename,skiprows=rows_to_skip)

    CamX = data['CamX']
    CamY = data['CamY']
    CamZ = data['CamZ']

    reading_header = True
    with open(filename,'r') as fid: 
        while reading_header:
            line = fid.readline()
            if "mmperprofile" in line.lower():
                mmPerProfile = int(line.split(',')[-1])
            if "swathwidthmm" in line.lower():
                SwathWidthMM = int(line.split(',')[-1])
            if "column headers" in line.lower():
                reading_header = False

    return CamX,CamY,CamZ,SwathWidthMM,mmPerProfile

if __name__ == '__main__':
    filename = './example_sick_scan_with_swath_files/20240529_exp2_wood_Scan0001_Pass0003(SwathMM_+00000.0, +00000.0 to +09759.0).LOG'
    CamX,CamY,CamZ = read_log(filename)

    # print(CamY,CamZ)

