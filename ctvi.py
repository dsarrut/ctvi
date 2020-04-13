#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import itk
from ctvi_helpers import *

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--exhale', '-e')
@click.option('--inhale', '-i')
@click.option('--lung_mask', '-m')
@click.option('--output', '-o')
@click.option('--sigma_gauss', '-s', default=0)
def ctvi_click(exhale, inhale, lung_mask, output, sigma_gauss):
    '''
    Doc todo
    '''

    print(exhale, inhale, lung_mask)
    exhale = itk.imread(exhale)
    inhale = itk.imread(inhale)
    lung_mask = itk.imread(lung_mask)

    options={}
    o = ctvi(exhale, inhale, lung_mask, options)

    

    if sigma_gauss != 0:
        o = img_gauss(o, sigma_gauss)
        
    itk.imwrite(o, output)

# --------------------------------------------------------------------------
if __name__ == '__main__':
    ctvi_click()
