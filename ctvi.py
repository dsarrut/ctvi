#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from ctvi_helpers import *
import itk
from box import Box

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--exhale', '-e')
@click.option('--inhale', '-i')
@click.option('--lung_mask', '-m')
@click.option('--output', '-o')
@click.option('--sigma_gauss', '-s', default=0)
@click.option('--radius_median', '-r', default=0)
@click.option('--rho_normalize', is_flag=True)
def ctvi_click(exhale, inhale, lung_mask, output, sigma_gauss, radius_median, rho_normalize):
    '''
    Doc todo
    '''

    print(exhale, inhale, lung_mask)
    exhale = itk.imread(exhale)
    inhale = itk.imread(inhale)
    lung_mask = itk.imread(lung_mask)

    # options
    options = Box() # FIXME later
    options.rho_normalize = rho_normalize
    options.sigma_gauss = sigma_gauss
    options.radius_median = radius_median
    options.remove_10pc = True
    
    ctvi = compute_ctvi(exhale, inhale, lung_mask, options)

    itk.imwrite(ctvi, output)

# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi_click()
