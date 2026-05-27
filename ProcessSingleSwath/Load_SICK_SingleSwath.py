import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os
import read_LUT 
import ProgressBar
import load_log_file as load_log
from tkinter import filedialog
import export_as_geotiff

files = filedialog.askopenfilenames(title='Select Swath .DAT File or Files',filetypes=[('Swath File','*.DAT')])

# LUT_File = filedialog.askopenfile(title='Select LUT .Raw File',filetypes=[('LUT Table File','*.raw')])


for file in files:
    dat_file = file#'./example_sick_scan_with_swath_files/20240529_exp2_wood_Scan0001_Pass0003(SwathMM_+00000.0, +00000.0 to +09759.0).DAT'
    log_file = file[0:-4]+'.LOG'  #./example_sick_scan_with_swath_files/20240529_exp2_wood_Scan0001_Pass0003(SwathMM_+00000.0, +00000.0 to +09759.0).LOG'
    xml_file = file[0:-4]+'.XML' #'./example_sick_scan_with_swath_files/20240529_exp2_wood_Scan0001_Pass0003(SwathMM_+00000.0, +00000.0 to +09759.0).XML'

    CamX,CamY,CamZ,SwathWidthMM,mmPerProfile = load_log.read_log(log_file)

    file_size = os.stat(dat_file).st_size
    width = 1536

    def read_profile(fid):
        mark_data = fid.read(20)
        intensity_data = fid.read(1536)
        range_data = fid.read(3072)
        # range_data = (np.frombuffer(range_data,np.uint16)^0x8000+32768)*1102/65536
        range_data = np.frombuffer(range_data,np.uint16)#*1102/65536
        cursor_pos = fid.tell()

        return range_data,cursor_pos
    # Open the binary file
    topo_px = []
    with open(dat_file, 'rb') as f:
        # Read the binary data into a NumPy array
        cursor_pos = 0
        while cursor_pos < file_size:
            range_data,cursor_pos = read_profile(f)
            topo_px.append(range_data)

    length = len(topo_px)

    topo_px = np.asarray(topo_px)
    topo_px = topo_px.reshape([int(length),width]).astype(np.float64)
    topo_px[topo_px==0] = np.nan

    u = np.linspace(1,8192,256)
    v = np.linspace(1,1536,1536)

    LUT_file = 'DeltaBasin (InAir)_scl 001102_yoff-0556.9_zoff 0000.0_LUT.raw'
    LUT_Scale = 1102
    LUT_Y_Offset = -556.9
    print(f'Using LUT: {LUT_file}\nScale={LUT_Scale}\nY_Offset={LUT_Y_Offset}')
    fy,fz = read_LUT.load_LUT(LUT_Scale,LUT_Y_Offset,LUT_file)

    rows = topo_px.shape[0]
    cols = topo_px.shape[1]

    if rows != len(CamY):
        raise Exception("Number of profiles in swath does not match the number of CamY points in the LOG file.")

    y_scan_width = SwathWidthMM #mm
    x_spacing    = mmPerProfile #mm
    num_of_y_points = int(y_scan_width/x_spacing)+1
    y_grid = np.linspace(-y_scan_width/2,y_scan_width/2,num_of_y_points)

    topo_y_mm = np.zeros([rows,cols])
    topo_z_mm = np.zeros([rows,cols])
    topo_z_mm_regrid = np.zeros([rows,num_of_y_points])

    print(f'\nProcessing {file.split('/')[-1]}')
    for row in range(rows):
        ProgressBar.printProgressBar(row,rows,length=50,prefix=f'Processing Profile {row} of {rows}')
        for pix in range(cols): 
            # Look up values in LUT for calibrated y and z
            topo_y_mm[row,pix] = np.interp(topo_px[row,pix],u,fy[:,pix])
            topo_z_mm[row,pix] = CamZ[row] - np.interp(topo_px[row,pix],u,fz[:,pix])
        
        # regrid to uniform grid spacing
        # first, sort y data into assending order:
        ind_sort = np.argsort(topo_y_mm[row,:])
        y_sorted = topo_y_mm[row,ind_sort]
        z_sorted = topo_z_mm[row,ind_sort]
        # regrid to a uniform spacing, interpolating between points.
        ## using np.interp probably isn't the best way to do this since there are NAN's present
        topo_z_mm_regrid[row,:] = np.interp(y_grid,y_sorted,z_sorted)


        # ax1 = plt.subplot(111)
        # i = row
        # ax1.plot(topo_y_mm[i,:],topo_z_mm[i,:],'.')
        # ax1.plot(y_grid,topo_z_mm_regrid[i,:],'.')
        # ax1.set_xlabel('Calibrated Y Position')
        # ax1.set_ylabel('Calibrated Z Position')
        # ax1.set_title(f'Profile Number: {i}')
        # plt.grid()
        # ax1.legend(['Calibrated Data','Regridded, Calibrated Data'])
        # plt.show()

    xmin = CamX.min()
    xmax = CamX.max()
    ymin = y_grid.min()+CamY[0]
    ymax = y_grid.max()+CamY[0]

    # ax1 = plt.subplot(121)
    # ax1.imshow(topo_z_mm)
    # ax1.set_title('Calibrated Z')
    # ax1.axis('equal')
    # ax2 = plt.subplot(122)
    # ax2.imshow(topo_z_mm_regrid)
    # ax2.set_title('Calibrated & Regridded Z')
    # ax2.axis('equal')
    # plt.show()

    export_as_geotiff.export_geotiff(topo_z_mm_regrid,filename=file[0:-4]+'_Processed.tif',xmin=ymin,xmax=ymax,ymin=xmin,ymax=xmax)