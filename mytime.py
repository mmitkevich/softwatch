#!/usr/bin/python2
import collections
import argparse
from softwatch import timelog
from softwatch import timenode
from run import run
import sys
import time
import os
import glob


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='log | report | start | stop | status')
    parser.add_argument('pattern', help="pattern+", nargs='*')
    parser.add_argument('-D', "--dir", help="log directory", type=str, default=os.path.expanduser(os.path.join("~",".mytime")))
    parser.add_argument('-f', "--file", help="log file mask", type=str)
    parser.add_argument("-t", "--tree", help="max depth of tree (default 1000), 0 for rating", type=int, default=1000)
    parser.add_argument("-s", "--samples", help="show samples",action="store_true")
    parser.add_argument("-d", "--duration", help="hide items with total duration less than d minutes (default )", type=float, default=5)
    parser.add_argument("-m", "--percent", help="hide items with total duration less than dp percent (default 0)", type=float, default=0)
    parser.add_argument("-b", "--begin", help="begin p days ago", type=float)
    parser.add_argument("-e", "--end", help="end e days ago", type=float)
    parser.add_argument("-r", "--relative", help="show time relative to 24h period", action="store_true")
    args = parser.parse_args()
    run(args)
    exit(0)