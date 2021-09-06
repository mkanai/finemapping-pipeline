#!/usr/bin/env python
import os
from utils import run_command

# inputs
INPUT_Z = os.environ['INPUT_Z']
INPUT_LD = os.environ['INPUT_LD']

OUT_SNP = os.environ['OUT_SNP']
OUT_CONFIG = os.environ['OUT_CONFIG']
OUT_CRED = os.environ['OUT_CRED']
OUT_LOG = os.environ['OUT_LOG']

N_SAMPLES = os.environ['N_SAMPLES']

if 'PHI' in os.environ and os.environ['PHI'] not in ['None', '']:
    PHI = ['--phi', os.environ['PHI']]
else:
    PHI = []

print('Running FINEMAP...')
run_command([
    'python', '/home/run_finemap.py',
    '--z', INPUT_Z,
    '--ld', INPUT_LD,
    '-n', N_SAMPLES,
    '--snp', OUT_SNP,
    '--config', OUT_CONFIG,
    '--cred', OUT_CRED,
    '--log', OUT_LOG
] + PHI)
