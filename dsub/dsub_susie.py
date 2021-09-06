#!/usr/bin/env python
import os
import sys
import subprocess as sp


def run_command(args, stderr=sp.STDOUT):
    try:
        if sys.version_info < (3,):
            output = sp.check_output(args, stderr=stderr)
        else:
            output = sp.check_output(args, encoding='utf-8', stderr=stderr)
        print(output)
        return (output)
    except sp.CalledProcessError as e:
        print(e.output)
        raise e


def is_existent(key, null_values=['None', '']):
    return key in os.environ and os.environ[key] not in null_values


# inputs
INPUT_Z = os.environ['INPUT_Z']
INPUT_LD = os.environ['INPUT_LD']

OUT_SNP = os.environ['OUT_SNP']
OUT_CRED = os.environ['OUT_CRED']
OUT_LOG = os.environ['OUT_LOG']
N_SAMPLES = os.environ['N_SAMPLES']

if is_existent('DOMINANT'):
    DOMINANT = ['--dominant']
else:
    DOMINANT = []

if is_existent('OUT_RDS'):
    RDS = [
        '--susie-obj', os.environ['OUT_RDS'],
        '--write-alpha',
        '--save-susie-obj'
    ]
else:
    RDS = []

if is_existent('VAR_Y'):
    VAR_Y = ['--var-y', os.environ['VAR_Y']]
else:
    VAR_Y = []

if is_existent('YTY'):
    YTY = ['--yty', os.environ['INPUT_YTY']]
elif is_existent('INPUT_YTY'):
    with open(os.environ['INPUT_YTY'], 'r') as f:
        YTY = ['--yty', f.read().strip()]
else:
    YTY = []

print('Running susieR...')
cmd = [
    'run_susieR.R',
    '--z', INPUT_Z,
    '--ld', INPUT_LD,
    '-n', N_SAMPLES,
    '--snp', OUT_SNP,
    '--cred', OUT_CRED,
    '--log', OUT_LOG
] + DOMINANT + RDS + VAR_Y + YTY

run_command(cmd)
