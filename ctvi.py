#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import itk
from box import Box
from ctvi_metric import *

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--exhale', '-e')
@click.option('--inhale', '-i')
@click.option('--lung_mask', '-m')
@click.option('--output', '-o')
@click.option('--sigma_gauss', '-g', default=0)
@click.option('--radius_median', '-r', default=0)
@click.option('--radius_erode_mask', default=0)
@click.option('--rho_normalize', is_flag=True)
def ctvi(exhale, inhale, lung_mask, output, radius_erode_mask, sigma_gauss, radius_median, rho_normalize):
    '''
    Doc todo
    '''

    exhale = itk.imread(exhale)
    inhale = itk.imread(inhale)
    lung_mask = itk.imread(lung_mask)

    # options
    options = Box()
    options.ventil_type = 'Kipritidis2015'
    options.rho_normalize = rho_normalize
    options.sigma_gauss = sigma_gauss
    options.radius_median = radius_median
    options.remove_10pc = False
    options.mass_corrected_inhale = True

    if radius_erode_mask != 0:
        mask = itk.array_view_from_image(lung_mask)
        mask[mask != 0] = 1
        lung_mask = erode_mask(lung_mask, radius_erode_mask)

    # go
    ctvi = compute_ctvi(exhale, inhale, lung_mask, options)

    itk.imwrite(ctvi, output)

# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi()
