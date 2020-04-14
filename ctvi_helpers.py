
import itk
import numpy as np

def ctvi(exhale, inhale, lung_mask, options):
    '''
    Doc todo.
    exhale, inhale, lung_mask: itk images
    options: dict
    '''

    exh = itk.array_from_image(exhale)
    inh = itk.array_from_image(inhale)
    mask = itk.array_from_image(lung_mask)

    # need to convert to float
    exh = exh.astype('float')
    inh = inh.astype('float')
    mask = mask.astype('float')

    # "... masks were adjusted to exclude any voxels with CT number > -250 HU"
    mask[exh>-250] = 0

    # voxel volume
    spacing = exhale.GetSpacing()
    vol = spacing[0]*spacing[1]*spacing[2]

    # Version1
    #ctvi = ctvi_delta_HU_Kipritidis2019(exh, inh, vol)

    # Version2
    ctvi = ctvi_delta_HU_Eslick2018(exh, inh, vol)

    # mask according to lung mask
    ctvi[mask==0] = 0

    # debug
    print(f'ctvi min-max: {np.min(ctvi)} {np.max(ctvi)} Q90% {np.quantile(ctvi[ctvi>0],0.9)}')

    # convert to float32 required by itk
    ctvi = ctvi.astype(np.float32)
    img = itk.image_from_array(ctvi)
    img.CopyInformation(exhale)

    return img


def ctvi_delta_HU_Kipritidis2019(exh, inh, vol):
    # Version1: Kipritidis2019, p1216
    # CTVI_delta_HU = -1000/exh * (exh-inh)/(inh+1000)
    # (handles division by zero)
    t = np.ones_like(exh)*-1000.0
    ctvi1 = np.divide(t, exh, out=np.zeros_like(exh), where=exh!=0)
    diff = exh-inh
    ctvi2 = np.divide(diff, inh+1000, out=np.zeros_like(exh), where=(inh+1000)!=0)
    ctvi = ctvi1*ctvi2
    # scaling factor ?
    #ctvi = ctvi/-1000*vol
    return ctvi


def ctvi_delta_HU_Eslick2018(exh, inh, vol):
    # Version2: Eslick2018, p269
    # CTVI_delta_HU = (exh-inh) / (inh+1000) * rho
    # rho = (ex+1000)/1000
    ctvi1 = exh-inh
    ctvi2 = inh+1000
    rho = np.divide(exh+1000, 1000)
    ctvi = np.divide(ctvi1, ctvi2, out=np.zeros_like(exh), where=ctvi2!=0)
    ctvi = ctvi*rho

    # remove negative values ?
    ctvi[ctvi<0] = 0
    
    return ctvi

