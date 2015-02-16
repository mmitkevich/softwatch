#!/usr/bin/python2

import argparse
from softwatch import activewindow
from softwatch import timenode
import sys
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='log | report')
    parser.add_argument('file', help="input file")
    parser.add_argument('pattern', help="pattern+", nargs='*')
    parser.add_argument("-t", "--tree", help="show as tree",action="store_true")
    parser.add_argument("-s", "--samples", help="show samples",action="store_true")
    parser.add_argument("-d", "--duration", help="minimum duration d minutes", type=float, default=0)
    parser.add_argument("-p", "--period", help="show only last p days", type=float)
    args = parser.parse_args()

    if args.action=='log':
        aw = activewindow.ActiveWindow()
        aw.logfile = args.file
        aw.monitor_active_window()
        exit(0)

    if args.action=='report':
        tr = timenode.TimeNode('*ROOT*')
        logfile = args.file
        opts = timenode.TimeQuery(samples=args.samples, tree=args.tree)
        opts.min_time = int(args.duration*60000)
        if args.period:
            opts.min_start = int((time.time()-3600*24*float(args.period))*1000)
        tr.read(logfile,opts)
        taglist = args.pattern #[0].split(' ')
        tr.query(set(taglist),opts)






