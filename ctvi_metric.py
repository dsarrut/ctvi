
import itk
import numpy as np
from ctvi_helpers import *

def compute_ctvi(exhale, inhale, lung_mask, options):
    '''
    Doc todo.
    inputs: exhale, inhale, lung_mask as itk images
    options: dict
    output: itk image (float)
    '''

    exh = itk.array_view_from_image(exhale)
    inh = itk.array_view_from_image(inhale)
    mask = itk.array_view_from_image(lung_mask)

    # need to convert to float
    exh = exh.astype('float')
    inh = inh.astype('float')
    mask = mask.astype('float')

    # "... masks were adjusted to exclude any voxels with CT number > -250 HU"
    #mask[exh>-250] = 0
    # NOT HERE -> should be done elsewhere

    # voxel volume
    spacing = exhale.GetSpacing()
    vol = spacing[0]*spacing[1]*spacing[2]

    # inhale mass correction ?
    if options.mass_corrected_inhale:
        inh = mass_correction_inhale(exh, inh, mask)

    # main ctvi computation
    if options.ventil_type == 'Kipritidis2019':
        ctvi = ctvi_delta_HU_Kipritidis2019(exh, inh, vol, mask, options)
    if options.ventil_type == 'Kipritidis2015':
        ctvi = ctvi_delta_HU_Kipritidis2015(exh, inh, vol, mask, options)

    # mask according to lung mask
    ctvi[mask==0] = 0

    # debug
    print(f'ctvi min max mean std Q90%: {np.min(ctvi[mask==1]): 0.4f} {np.max(ctvi[mask==1]): 0.4f} '
          f'{np.mean(ctvi[mask==1]): 0.4f} {np.std(ctvi[mask==1]): 0.4f} '
          f'{np.quantile(ctvi[mask==1],0.9): 0.4f}')

    # convert to float32 required by itk
    ctvi = ctvi.astype(np.float32)
    img = itk.image_from_array(ctvi)
    img.CopyInformation(exhale)

    # Gaussian filter
    # According to itk doc: 'Sigma is measured in the units of image spacing'
    if options.sigma_gauss != 0:
        img = itk.recursive_gaussian_image_filter(img, sigma=options.sigma_gauss)

    # Median filter (recommanded)
    if options.radius_median != 0:
        img = median_filter_with_mask(img, mask, options.radius_median, options.radius_median)
        img = img.astype(np.float32)
        img = itk.image_from_array(img)
        img.CopyInformation(exhale)

    # remove 10% higher
    if options.remove_10pc:
        t = np.quantile(ctvi[ctvi>0], 0.9)
        print('Q90%', t)
        ctvi[ctvi>t] = 0
        img = itk.image_from_array(ctvi)
        img.CopyInformation(exhale)


    return img


def ctvi_delta_HU_Kipritidis2019(exh, inh, vol, mask, options):
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


def ctvi_delta_HU_Kipritidis2015(exh, inh, vol, mask, options):
    # Version3: Kipritidis2015, p37
    # CTVI_delta_HU = (exh-inh) / (inh+1000) * rho
    # rho = (ex+1000)/1000
    # inh should be mass corrected before

    # ctvi
    ctvi1 = exh - inh
    ctvi2 = inh + 1000
    ctvi = np.divide(ctvi1, ctvi2, out=np.zeros_like(exh), where=ctvi2!=0)

    # rho scaling
    rho = np.divide(exh + 1000, 1000)
    ctvi = ctvi * rho

    # remove negative values
    ctvi[ctvi<0] = 0
    
    return ctvi

def mass_correction_inhale(exh, inh, mask):
    # correct inhale lung density according to
    # fractional mass change due to the blood distribution
    # inh' =  HUin(x) − 1000 × f (1 + HUin(x)/1000)
    # f =􏰢 (sum ρ_in(x) - sum ρ_ex(x)) / sum ρ_in(x)
    # ρ(x)≡HU(x) + 1000
    exh_rho = np.sum(exh[mask == 1] + 1000)
    inh_rho = np.sum(inh[mask == 1] + 1000)
    #print('rho : ', exh_rho, inh_rho)
    f = (inh_rho - exh_rho) / exh_rho
    #print('f', f)

    # debug
    #print('mean exh', np.mean(exh[mask == 1]))
    #print('mean inh', np.mean(inh[mask == 1]))

    # correction to inhale image
    inhs = inh - 1000 * f * (1 + inh / 1000)

    # debug
    #print('mean inh', np.mean(inhs[mask == 1]))

    return inhs
