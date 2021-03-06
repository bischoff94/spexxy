import logging

import numpy as np
import pandas as pd

from spexxy.data import Isochrone


def add_parser(subparsers):
    # init parser
    parser = subparsers.add_parser('apply', help='Apply isochrone to photometry')
    parser.set_defaults(func=run)

    # parameters
    parser.add_argument('isochrone', help='File containing the isochrone', type=str)
    parser.add_argument('photometry', help='File containing the photometry', type=str)
    parser.add_argument('-o', '--output', help='Output file', type=str, default='cmpiso.csv')
    parser.add_argument('--id', help='IDs from photometry file to copy to the output', nargs='+')
    parser.add_argument('--filter1', help='First filter to use', type=str, default="F606W")
    parser.add_argument('--filter2', help='Second filter to use', type=str, default="F814W")
    parser.add_argument('--filter1-iso', help='First filter in isochrone to use (--filter1 if empty)', type=str)
    parser.add_argument('--filter2-iso', help='Second filter in isochrone to use (--filter2 if empty)', type=str)
    parser.add_argument('--nearest', help='Use nearest neighbour instead of polynomial', action='store_true')


def run(args):
    # get isochrone
    logging.info("Loading isochrone from %s...", args.isochrone)
    isochrone = Isochrone.load(args.isochrone)

    # get filters in isochrone
    iso_filter1 = args.filter1.upper() if args.filter1_iso is None else args.filter1_iso.upper()
    iso_filter2 = args.filter2.upper() if args.filter2_iso is None else args.filter2_iso.upper()

    # load photometry
    logging.info("Loading photometry from %s...", args.photometry)
    photometry = pd.read_csv(args.photometry, index_col=False)

    # uppercase filters
    cols = []
    for c in photometry.columns:
        if c.endswith('_Id') or c == 'SourceNumber':
            cols.append(c)
        elif c.endswith('_err'):
            cols.append(c[:-4].upper() + '_err')
        else:
            cols.append(c.upper())
    photometry.columns = cols

    # photometry filters
    photo_filters = sorted([f for f in photometry.columns if f != 'Star_Id'])
    logging.info('Found filters in photometry: ' + ', '.join(photo_filters))
    logging.info('Using filters %s, %s in photometry.', args.filter1.upper(), args.filter2.upper())
    logging.info('Using filters %s, %s in isochrone.', iso_filter1, iso_filter2)

    # check
    if args.filter1.upper() not in photometry.columns or args.filter2.upper() not in photometry.columns:
        logging.error("Could not find given filters in photometry.")
        return

    # get interpolators
    if args.nearest:
        ip_nearest = isochrone.nearest(iso_filter1, iso_filter2)
    else:
        ip_teff = isochrone.interpolator('Teff', iso_filter1, iso_filter2)
        ip_logg = isochrone.interpolator('logg', iso_filter1, iso_filter2)
        ip_mact = isochrone.interpolator('M_act', iso_filter1, iso_filter2)
        ip_mini = isochrone.interpolator('M_ini', iso_filter1, iso_filter2)

    # loop all photometry
    logging.info('Applying isochrone to all stars in photometry...')
    with open(args.output, 'w') as f:
        if args.id:
            f.write(','.join(args.id) + ',')
        f.write('Teff_iso,logg_iso,Mini_iso,Mact_iso\n')

        for row in range(len(photometry)):
            # get requested ids
            ids = [photometry[i].iloc[row] for i in args.id] if args.id else []

            # get photometry
            v = photometry[args.filter1.upper()].iloc[row]
            i = photometry[args.filter2.upper()].iloc[row]
            if np.isnan(v) or np.isnan(i):
                logging.error('Magnitude is NaN for ' +
                              ', '.join([args.id[i] + '=' + str(ids[i]) for i in range(len(ids))]))
                continue

            # get values
            if args.nearest:
                tmp = ip_nearest(v - i, v)
                Teff = (tmp['teff'], None)
                logg = (tmp['logg'], None)
                Mini = (tmp['mini'], None)
                Mact = (tmp['mact'], None)
            else:
                Teff = (ip_teff(v - i, v), None)
                logg = (ip_logg(v - i, v), None)
                Mini = (ip_mini(v - i, v), None)
                Mact = (ip_mact(v - i, v), None)

            # write results to file
            if args.id:
                f.write(','.join(['{0:d}'.format(int(i)) for i in ids]) + ',')
            f.write('{0:.4f},{1:.4f},{2:.4f},{3:.4f}\n'.format(Teff[0], logg[0], Mini[0], Mact[0]))
            f.flush()
