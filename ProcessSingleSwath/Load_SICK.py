import tkinter.filedialog as fd
import numpy as np
import xml.etree.ElementTree as ET
import export_as_geotiff as export
import matplotlib.pyplot as plt

filename = fd.askopenfilename(filetypes=[('Processed SICK Scans','*TopoData.dat')])

file = filename.split('/')[-1]
# Open the binary file
with open(filename, 'rb') as f:
    # Read the binary data into a NumPy array
    data = np.fromfile(f, dtype=np.float32)  # Adjust dtype according to your data type

data[data==-9999] = np.nan

# Get Grid start and end from filename: 
grid_inds = [file.find('Grid='),file.find('Grid=')+len('Grid=')]
xy_inds   = [file.find('XY='),file.find('XY=')+len('XY=')]

grid_string = file[grid_inds[-1]:xy_inds[0]]
grid_string = grid_string.strip().replace('(','').replace(')','')
grid = np.asarray(grid_string.split('x')).astype('float')

xy_string = file[xy_inds[-1]:]
xy_string = xy_string.strip().replace('(','').replace(')','').replace('_TopoData.DAT','')
print(xy_string)
xy_start_string  = xy_string.split(' to ')[0]
xy_end_string    = xy_string.split(' to ')[1]
xy_start         = np.asarray(xy_start_string.split(',')).astype('float')
xy_end           = np.asarray(xy_end_string.split(',')).astype('float')

xmin = xy_start[0]
xmax = xy_end[0]
ymin = xy_start[1]
ymax = xy_end[1]

# Read the Corresponding XML File: 
xml_filename = filename[0:-4]+'.xml'
xml_data = ET.parse(xml_filename)
root = xml_data.getroot()
width = int(root.find('.//parameter[@name="width"]').text)

topo = data.reshape([int(len(data)/width),width])
topo = np.flip(topo,0)

print(f'Number of Datapoints: {topo.flatten().shape}')

export.export_geotiff(topo,file,xmin,xmax,ymin,ymax)
plt.figure()
plt.imshow(topo)
plt.show()

