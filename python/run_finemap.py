#!/usr/bin/env python
import argparse
import gzip
import os.path
import tempfile
import numpy as np
import pandas as pd
from collections import OrderedDict
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG
from utils import run_command, gunzip


# logger
logger = getLogger(__name__)
log_format = Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = StreamHandler()
handler.setFormatter(log_format)
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


def generate_master(args):
    df = pd.DataFrame(
        OrderedDict((
            ('z', [args.z]),
            ('ld', [args.ld]),
            ('snp', [args.snp]),
            ('config', [args.config]),
            ('cred', [args.cred]),
            ('n_samples', [args.n_samples]),
            ('log', [args.log[:-4]])
        )))
    return(df)


def main(args):
    if args.triangular_ld_matrix:
        logger.info('--triangular-ld-matrix is specified. LD matrix is re-densified.')
        op = gzip.open if args.ld.endswith('gz') else open
        with op(args.ld) as f:
            R = np.loadtxt(f)
        n = R.shape[0]
        R[np.tril_indices(n)] = R.T[np.tril_indices(n)]
        args.ld = os.path.join(tempfile.mkdtemp(), 'full.ld')
        with open(args.ld, 'w') as f:
            np.savetxt(args.ld, R)
    elif args.ld.endswith('gz'):
        logger.info('Unzipping ld file')
        args.ld = gunzip(args.ld)

    logger.info('Generating master file')
    master = generate_master(args)
    master.to_csv(args.out + '.master', sep=';', index=False)

    if args.var_y is not None:
        prior_std = ['--prior-std', str(0.05 * np.sqrt(args.var_y))]
    elif args.phi is not None:
        prior_std = ['--prior-std', str(0.05 * np.sqrt(args.phi * (1 - args.phi)))]
    else:
        prior_std = []

    logger.info('Starting FINEMAP')
    run_command([
        'finemap', '--sss',
        '--in-files', args.out + '.master',
        '--log',
        '--n-causal-snps', str(args.n_causal_snps),
        '--n-threads', str(args.n_threads)
    ] + prior_std)

    logger.info('Finished!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--z', '-z', type=str, required=True)
    parser.add_argument('--ld', type=str, required=True)
    parser.add_argument('--out', type=str)
    parser.add_argument('--snp', type=str)
    parser.add_argument('--config', type=str)
    parser.add_argument('--cred', type=str)
    parser.add_argument('--log', type=str)
    parser.add_argument('--n-samples', '-n', type=int, required=True)
    parser.add_argument('--n-causal-snps', '-k', type=int, default=10)
    parser.add_argument('--n-threads', type=int, default=1)
    parser.add_argument('--corr-group', type=float, default=0.9)
    parser.add_argument('--var-y', type=float)
    parser.add_argument('--phi', type=float)
    parser.add_argument('--triangular-ld-matrix', action='store_true', help='Use triangular LD matrix')

    args = parser.parse_args()

    if args.out is None and any(map(lambda x: x is None, [args.snp, args.config, args.cred, args.log])):
        raise ValueError('Either --out or all of --snp, --config, --cred, and --log should be specified.')
    if args.out is None:
        args.out = 'tmp'
    if args.snp is None:
        args.snp = args.out + '.snp'
    if args.config is None:
        args.config = args.out + '.config'
    if args.cred is None:
        args.cred = args.out + '.cred'
    if args.log is None:
        args.log = args.out + '.log_sss'

    # logging
    fhandler = FileHandler(args.out + '.log', 'w+')
    fhandler.setFormatter(log_format)
    logger.addHandler(fhandler)

    # https://github.com/bulik/ldsc/blob/master/ldsc.py#L589
    opts = vars(args)
    # defaults = vars(parser.parse_args(''))
    # non_defaults = [x for x in opts.keys() if opts[x] != defaults[x]]
    non_defaults = [x for x in opts.keys()]
    call = "Call: \n"
    call += './' + os.path.basename(__file__) + ' \\\n'
    options = ['--' + x.replace('_', '-') + ' ' + str(opts[x]) + ' \\' for x in non_defaults]
    call += '\n'.join(options).replace('True', '').replace('False', '')
    call = call[0:-1] + '\n'
    logger.info(call)

    main(args)
