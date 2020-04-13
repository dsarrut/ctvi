
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

    # CTVI_delta_HU = -1000/exh * (exh-inh)/(inh+1000)
    # (handles division by zero)
    t = np.ones_like(exh)*-1000.0
    ctvi1 = np.divide(t, exh, out=np.ones_like(exh), where=exh!=0)
    diff = exh-inh
    ctvi2 = np.divide(diff, inh+1000, out=np.zeros_like(exh), where=inh+1000!=0)
    ctvi = ctvi1*ctvi2

    # scaling factor
    spacing = exhale.GetSpacing()
    vol = spacing[0]*spacing[1]*spacing[2]
    ctvi = ctvi/-1000*vol
    
    # mask according to lung mask
    ctvi[mask==0] = 0

    # convert to float32 required by itk
    ctvi = ctvi.astype(
        np.float32)
    img = itk.image_from_array(ctvi)
    img.CopyInformation(exhale)
    
    return img


def img_gauss(img, sigma):
    '''
    Apply Gaussian smoothing filter.
    According to itk doc: 'Sigma is measured in the units of image spacing'
    '''
    ImageType = type(img)
    smoothFilter = itk.SmoothingRecursiveGaussianImageFilter[ImageType, ImageType].New()
    smoothFilter.SetInput(img)
    smoothFilter.SetSigma(sigma)
    smoothFilter.Update()
    return smoothFilter.GetOutput()


def img_median(img, radius):
    '''
    Median Filtering 
    '''
    ImageType = type(img)
    medianFilter = itk.MedianImageFilter[ImageType, ImageType].New()
    medianFilter.SetInput(img)
    medianFilter.SetRadius(radius)
    medianFilter.Update()
    return medianFilter.GetOutput()

