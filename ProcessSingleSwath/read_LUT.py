import numpy as np
import matplotlib.pyplot as plt


def load_LUT(LUTscale,LUT_Y_Offset,LUT_raw_file):

    with open(LUT_raw_file,'rb') as fid:
        data = np.fromfile(fid,dtype=np.uint16)

    # print(f'shape of "data": {data.shape}')

    LUT_data = data.reshape([512,1536])

    # print(f'Shape of LUT_data: {LUT_data.shape}')

    fy = LUT_data[0:256,:]
    fz = LUT_data[256:,:]

    # print(f'shape of fx = {fx.shape}')
    # print(f'shape of fz = {fz.shape}')

    rows = fy.shape[0]
    cols = fy.shape[1]

    y_LUT = np.zeros([rows,cols])#.astype(np.uint16)
    z_LUT = np.zeros([rows,cols])#.astype(np.uint16)

    for u in range(rows):
        for v in range(cols):
            # x_LUT[u,v] = (fx[u,v] ^0x8000 + 32768) * LUTscale / 65536
            # z_LUT[u,v] = (fz[u,v] ^0x8000 + 32768) * LUTscale / 65536

            y_LUT[u,v] = fy[u,v] * LUTscale / 65536 +LUT_Y_Offset
            z_LUT[u,v] = fz[u,v] * LUTscale / 65536
    
    return y_LUT,z_LUT


if __name__ == '__main__':
    fy,fz = load_LUT(1102,-556.9,'DeltaBasin (InAir)_scl 001102_yoff-0556.9_zoff 0000.0_LUT.raw')

    ax1 = plt.subplot(211)
    ax1.imshow(fy)
    ax1.set_title('$f_y$')
    ax2 = plt.subplot(212)
    ax2.imshow(fz)
    ax2.set_title('$f_z$')
    plt.show()
