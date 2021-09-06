#!/usr/bin/env python
import os
import os.path
import numpy as np
import pandas as pd
from collections import OrderedDict
from utils import run_command, gzip, new_local_temp_dir

LDSTORE_VERSION = os.environ['LDSTORE_VERSION']

# inputs
INPUT_SAMPLES = os.environ['INPUT_SAMPLES']
INPUT_INCL_SAMPLES = os.environ['INPUT_INCL_SAMPLES']

# outputs
OUT_BCOR = os.environ['OUT_BCOR']
_OUT_LD = os.path.splitext(os.environ['OUT_LD'])[0]

if LDSTORE_VERSION == 'v1.1':
    CHROM = os.environ['CHROM']
    START = os.environ['START']
    END = os.environ['END']
    INPUT_INCL_VARIANTS = os.environ['INPUT_INCL_VARIANTS']
else:
    INPUT_Z = os.environ['INPUT_Z']
    CHROM = str(pd.read_csv(INPUT_Z, delim_whitespace=True, nrows=1).chromosome.iloc[0]).replace('chr', '')

# bgen files
BGEN_BUCKET = os.path.join(os.environ['BGEN_BUCKET'], os.environ['BGEN_DIRNAME'])
BGEN_FNAME_FORMAT = os.environ['BGEN_FNAME_FORMAT']
INPUT_BGEN = os.path.join(BGEN_BUCKET, BGEN_FNAME_FORMAT.format(CHROM))
n_threads = run_command(['grep', '-c', '^processor', '/proc/cpuinfo']).strip()
cpu_mem = '3.75'  # assuming standard machine type

if 'INPUT_BGI' in os.environ:
    INPUT_BGI = os.environ['INPUT_BGI']
else:
    INPUT_BGI = INPUT_BGEN + '.bgi'

# run ldstore
print('Running ldstore...')
tmpdir = new_local_temp_dir()

print(n_threads, cpu_mem)

if LDSTORE_VERSION == 'v1.1':
    OPTION_INCL_VARIANTS = []
    run_command([
        'ldstore', '--bgen', INPUT_BGEN,
        '--samples', INPUT_SAMPLES, '--incl-sample', INPUT_INCL_SAMPLES,
        '--bcor', OUT_BCOR, '--incl-range', '{}-{}'.format(START, END)
    ])
    run_command(['ldstore', '--bcor', OUT_BCOR, '--merge', n_threads])
    run_command(['ldstore', '--bcor', OUT_BCOR, '--matrix', _OUT_LD, '--incl-variants', INPUT_INCL_VARIANTS])
else:
    _INPUT_MASTER = os.path.join(tmpdir, 'master')
    _INPUT_INCL_SAMPLES = os.path.join(tmpdir, 'tmp.incl')

    # Subset incl (for X)
    samples = pd.read_csv(INPUT_SAMPLES, delim_whitespace=True)
    incl = pd.read_csv(INPUT_INCL_SAMPLES, header=None)
    incl = incl.loc[incl.iloc[:, 0].isin(samples.ID_1), :]
    incl.to_csv(_INPUT_INCL_SAMPLES, index=False, header=None)

    master = pd.DataFrame(
        OrderedDict((
            ('z', [INPUT_Z]),
            ('bgen', [INPUT_BGEN]),
            ('bgi', [INPUT_BGI]),
            ('bcor', [OUT_BCOR]),
            ('ld', [_OUT_LD]),
            ('sample', [INPUT_SAMPLES]),
            ('incl', [_INPUT_INCL_SAMPLES]),
            ('n_samples', [run_command(['wc', '-l', _INPUT_INCL_SAMPLES]).split()[0]])
        )))
    print(master)
    master.to_csv(_INPUT_MASTER, sep=';', index=False)

    run_command([
        'ldstore', '--in-files', _INPUT_MASTER,
        '--write-bcor',
        '--n-threads', n_threads  #, '--cpu-mem', cpu_mem
    ])
    run_command([
        'ldstore', '--in-files', _INPUT_MASTER,
        '--bcor-to-text'
    ])

# convert to npz
print('Gziping .ld file...')
gzip(_OUT_LD, bgzip=True, n_threads=n_threads)

print('Finished!')
