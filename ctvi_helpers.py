
import itk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap
from box import Box

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
    #erodeFilter.SetBackgroundValue(0)
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


def pix_vol(img):
    spacing = img.GetSpacing()
    return spacing[0]*spacing[1]*spacing[2]


def median_filter_with_mask(img, mask, radius_dilatation, radius_median):

    # debug
    debug = False
    if debug:
        input = img
        itk.imwrite(img, 'ctvi_before.mhd')
        ctvim = itk.median_image_filter(img, radius=radius_median)
        itk.imwrite(ctvim, 'ctvi_median.mhd')

    dimg = dilate_at_boundaries(img, radius_dilatation)

    if debug:
        itk.imwrite(dimg, 'ctvi_before_dilated.mhd')

    imgm = itk.median_image_filter(dimg, radius = radius_median)

    if debug:
        itk.imwrite(imgm, 'ctvi_median_after_dilated.mhd')

    # reapply mask after median
    imgm = itk.array_from_image(imgm)
    imgm = imgm.astype('float')
    imgm[mask == 0] = 0

    if debug:
        imgm = imgm.astype(np.float32)
        a = itk.image_from_array(imgm)
        a.CopyInformation(input)
        itk.imwrite(a, 'ctvi_median_final.mhd')

    return imgm


def check_same_geometry(img1, img2):

    origin1 = img1.GetOrigin()
    origin2 = img2.GetOrigin()
    if not np.allclose(origin1, origin2):
        raise TypeError(f'images have incompatible origins: {origin1} versus {origin2}')

    spacing1 = img1.GetSpacing()
    spacing2 = img2.GetSpacing()
    if not np.allclose(spacing1, spacing2):
        raise TypeError(f'images have incompatible spacing: {spacing1} versus {spacing2}')

    dire1 = itk.GetArrayFromVnlMatrix(img1.GetDirection().GetVnlMatrix().as_matrix())
    dire2 = itk.GetArrayFromVnlMatrix(img2.GetDirection().GetVnlMatrix().as_matrix())

    if not np.allclose(dire1, dire2):
        raise TypeError(f'images have incompatible origins: {dire1} versus {dire2}')



def lung_mass_and_volume(img, img_mask):
    '''
    Mass in g
    Volume in L
    # HU = 1000 x (mu-mu_w) / (mu_w - mu_air)
    # mu = HU/1000 * (mu_w-mu_a) + mu_w
    # This is WRONG for H > 0 !
    # See for ex Schneider2000
    '''

    data = itk.array_view_from_image(img)
    mask = itk.array_view_from_image(img_mask)
    check_same_geometry(img, img_mask)

    # lung volume (be sure to consider all labels != 0 in the mask)
    pixel_vol = pix_vol(img) # in mm3
    mask[mask !=0 ] = 1
    n = mask.sum()
    lung_vol = n*pixel_vol*1e-6 # vol in L

    # lung mass
    mu_w = 1
    mu_a = 0.0
    d = data / 1000.0 * (mu_w - mu_a) + mu_w
    d[mask == 0] = 0.0
    lung_mass = d.sum()*pixel_vol*1e-3 # mass in grams

    stat = Box()
    stat.mass_g = lung_mass
    stat.volume_L = lung_vol
    stat.pixels_count = n
    stat.pixel_volume_mm3 = pixel_vol
    return stat


def basics_stats(img, mask):
    stat = Box()
    stat.pixels_count = mask.sum()
    stat.min = np.min(img[mask != 0])
    stat.max = np.max(img[mask != 0])
    stat.mean = np.mean(img[mask != 0])
    stat.std = np.std(img[mask != 0])
    stat.q90 = np.quantile(img[mask != 0], 0.9)
    stat.q10 = np.quantile(img[mask != 0], 0.1)

    return stat















