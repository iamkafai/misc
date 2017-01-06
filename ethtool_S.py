#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import subprocess
import argparse
import time
import sys
import os

def update(s, k, v):
    if k in s:
        s[k] = int(v) - s[k]
    else:
        s[k] = int(v)

def ethtool_S(ethtool_bin, iface, t):
    s = {}

    for i in range(2):
        p = subprocess.Popen([ethtool_bin, '-S', iface], stdout=subprocess.PIPE)

        for l in p.stdout:
            k, v = l.split(':')
            if not v:
                continue
            k = k.strip()
            v = v.strip()
            if not (k and v.isdigit()):
                continue
            update(s, k, v)

        p.stdout.close()
        del p
        time.sleep(t)

    return s

def print_rate(k, v, t, no_unit):
    r = v / t
    u = ''

    if not no_unit:
        if r >= 1000000:
            u = 'M'
            r = r / 1000000
        elif r >= 1000:
            u = 'K'
            r = r / 1000

    print('%s: %.03f %s/s' % (k, r, u))

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--ethtool_bin', default='ethtool',
                            help='Full path to ethtool binary')
    arg_parser.add_argument('-i', '--iface', default='eth0',
                            help='Ethernet interface')
    arg_parser.add_argument('-t', '--time', default=10, type=int,
                            help='Sleep time between two consecutive ethtool runs')
    arg_parser.add_argument('-s', '--sort', action='store_true',
                            help='Sort in decending order')
    arg_parser.add_argument('-z', '--zero', action='store_true',
                            help='Show zero counters')
    arg_parser.add_argument('-U', '--no-unit', action='store_true',
                            help='Do not use unit to shorten the numbers');
    args = arg_parser.parse_args(sys.argv[1:])

    s = ethtool_S(args.ethtool_bin, args.iface, args.time)
    s = s.items();
    if args.sort:
        s = sorted(s, key=lambda e: e[1])
    for k, v in s:
        if args.zero or v != 0:
            print_rate(k, v, args.time, args.no_unit)
