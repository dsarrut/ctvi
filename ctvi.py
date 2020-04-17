#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from ctvi_helpers import *
import itk

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--exhale', '-e')
@click.option('--inhale', '-i')
@click.option('--lung_mask', '-m')
@click.option('--output', '-o')
@click.option('--sigma_gauss', '-s', default=0)
@click.option('--radius_median', '-r', default=0)
def ctvi_click(exhale, inhale, lung_mask, output, sigma_gauss, radius_median):
    '''
    Doc todo
    '''

    print(exhale, inhale, lung_mask)
    exhale = itk.imread(exhale)
    inhale = itk.imread(inhale)
    lung_mask = itk.imread(lung_mask)

    options={} # FIXME later 
    ctvi = compute_ctvi(exhale, inhale, lung_mask, options)

    # Gaussian filter
    # According to itk doc: 'Sigma is measured in the units of image spacing'
    if sigma_gauss != 0:
        ctvi = itk.recursive_gaussian_image_filter(ctvi, sigma=sigma_gauss)

    # Median filter (recommanded)
    if radius_median != 0:
        #itk.imwrite(ctvi, 'ctvi_before.mhd')
        #ctvim = itk.median_image_filter(ctvi, radius=radius_median)
        #itk.imwrite(ctvim, 'ctvi_median.mhd')
        dctvi = dilate_at_boundaries(ctvi, 1)
        #itk.imwrite(dctvi, 'ctvi_before_dilated.mhd')
        ctvi = itk.median_image_filter(dctvi, radius=radius_median)
        #itk.imwrite(ctvi, 'ctvi_median_after_dilated.mhd')

        
    itk.imwrite(ctvi, output)

# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi_click()
