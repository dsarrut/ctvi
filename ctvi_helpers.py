
import itk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm

def compute_ctvi(exhale, inhale, lung_mask, options):
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

def get_colormap1():
    # color palette
    # https://matplotlib.org/tutorials/colors/colormaps.html
    cmap = plt.get_cmap('afmhot')
    cmap_ct = plt.get_cmap('gray')

    # build another palette with opacity 
    ncolors = 256
    color_array = cmap(range(ncolors))
    color_array[0:1, -1] = 0
    color_array[1:, -1] = 0.8
    map_object = LinearSegmentedColormap.from_list(name='afmhot_alpha',colors=color_array)
    plt.register_cmap(cmap=map_object)
    cmap = plt.get_cmap('afmhot_alpha')

    # https://matplotlib.org/3.2.1/tutorials/colors/colormapnorms.html
    norm=colors.Normalize()
    #norm=colors.PowerNorm(gamma=2)
    #norm=colors.LogNorm()

    return cmap, cmap_ct, norm


def get_slice(img, axis, slice_nb):
    if axis == 0:
        img = img[slice_nb, :, :]
    if axis == 1:
        img = img[:, slice_nb, :]
        # upside down
        img = np.flip(img, 0)
    if axis == 2:
        img = img[:, :, slice_nb]
        # upside down
        img = np.flip(img, 0)
    return img


def save_img(filename, ctvi, ct, mask, cmap, cmap_ct, norm):
    #https://fengl.org/2014/07/09/matplotlib-savefig-without-borderframe/
    # create an image with the exact same nb of pixels than the images
    # if spacing is not equal -> will be incorrect
    sizes = np.shape(ctvi)
    height = float(sizes[0])
    width = float(sizes[1])
    fig = plt.figure()
    fig.set_size_inches(width/height, 1, forward=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(ct, aspect='equal', cmap=cmap_ct, alpha=1.0, vmax=300, vmin=-1000)
    ax.imshow(ctvi, aspect='equal', cmap=cmap, norm=norm, vmax=1.0)
    plt.savefig(filename, dpi = height) 
    plt.close()


def erode_mask(image, radius):
    '''
    I did not manage to use the following filter:
    o = itk.binary_erode_image_filter(mask, ???)
    help(itk.binary_erode_image_filter)
    '''

    ImageType = type(image)
    Dimension = image.GetImageDimension()
    
    StructuringElementType = itk.FlatStructuringElement[Dimension]
    structuringElement = StructuringElementType.Ball(radius)
    ErodeFilterType = itk.BinaryErodeImageFilter[ImageType,
                                                 ImageType,
                                                 StructuringElementType]
    erodeFilter = ErodeFilterType.New()
    erodeFilter.SetInput(image)
    erodeFilter.SetForegroundValue(1)
    erodeFilter.SetKernel(structuringElement)
    erodeFilter.Update()
    
    return erodeFilter.GetOutput()



def dilate_at_boundaries(image, radius):
    '''
    Dilate the input image only near boundaries (defined by values == 0)
    '''

    ImageType = type(image)
    Dimension = image.GetImageDimension()

    StructuringElementType = itk.FlatStructuringElement[Dimension]
    structuringElement = StructuringElementType.Ball(radius)

    grayscaleFilter = itk.GrayscaleDilateImageFilter[
        ImageType, ImageType, StructuringElementType].New()
    grayscaleFilter.SetInput(image)
    grayscaleFilter.SetKernel(structuringElement)
    grayscaleFilter.Update()

    o = grayscaleFilter.GetOutput()

    o = itk.array_from_image(o)
    c = itk.array_from_image(image)
    o[c>0.0] = 0
    o = c+o

    o = itk.image_from_array(o)
    o.CopyInformation(image)

    return o


def OLD_median_image_filter(image, radius):

    ImageType = type(image)
    Dimension = image.GetImageDimension()
    medianFilter = itk.MedianImageFilter[ImageType, ImageType].New()
    medianFilter.SetInput(radius)
    medianFilter.SetRadius(radius)
    medianFilter.Update()
    o = medianFilter.GetOutput()

    return o
