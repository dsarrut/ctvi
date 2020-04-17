#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import itk
from ctvi_helpers import *

# --------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--input', '-i')
@click.option('--output', '-o')
@click.option('--radius', '-r', default=1)
def erod(input, output, radius):
    '''
    Erode a binary image by the given radius (in pixel)
    '''

    mask = itk.imread(input)
    o = erode_mask(mask, radius)
    itk.imwrite(o, output)

# --------------------------------------------------------------------------
if __name__ == '__main__':
    erod()
