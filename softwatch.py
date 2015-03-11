#!/usr/bin/python2

import argparse
from softwatch import timelog
from softwatch import timenode
import sys
import time
import os
import yaml
import glob

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='log | report | start | stop | status')
    parser.add_argument('pattern', help="pattern+", nargs='*')
    parser.add_argument('-D', "--dir", help="log directory", type=str, default=os.path.expanduser("~/.mytime"))
    parser.add_argument('-f', "--file", help="log file mask", type=str)
    parser.add_argument("-t", "--tree", help="max depth of tree (default 1000), 0 for rating", type=int, default=1000)
    parser.add_argument("-s", "--samples", help="show samples",action="store_true")
    parser.add_argument("-d", "--duration", help="hide items with total duration less than d minutes (default )", type=float, default=5)
    parser.add_argument("-m", "--percent", help="hide items with total duration less than dp percent (default 0)", type=float, default=0)
    parser.add_argument("-b", "--begin", help="begin p days ago", type=float)
    parser.add_argument("-e", "--end", help="end e days ago", type=float)
    parser.add_argument("-r", "--relative", help="show time relative to 24h period", action="store_true")
    args = parser.parse_args()

    if args.action=='log':
        aw = timelog.TimeLog(args.dir)
        aw.monitor_active_window()
        exit(0)

    if args.action=='report':
        args.file = args.file or "*.log"

        opts = timenode.TimeQuery(samples=args.samples, tree=args.tree)
        opts.tasks = timenode.loadTasks(os.path.join(args.dir,"tasks.cat"))

        opts.min_time = int(args.duration*60000)
        opts.min_percent = float(args.percent)

        opts.relative = args.relative

        if args.begin:
            opts.min_start = int((time.time()-3600*24*float(args.begin))*1000)
        if args.end:
            opts.max_start = int((time.time()-3600*24*float(args.end))*1000)

       	logfiles = [ f for f in glob.glob(os.path.join(args.dir,args.file)) if os.path.isfile(os.path.join(args.file,f)) ]
        logfiles = sorted(logfiles)
        for f in logfiles:
            if (os.path.getmtime(f)*1000-opts.min_start>=0):
#                print "processing "+f
                opts.process_file(f)
#            else:
#                print "skipped "+f
        taglist = args.pattern #[0].split(' ')
        opts.total.query(set(taglist),opts)
        exit(0)






