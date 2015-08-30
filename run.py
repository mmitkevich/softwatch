#!/usr/bin/python2
import collections
import argparse
from softwatch import timelog
from softwatch import timenode
import sys
import time
import os
import glob
import traceback
import codecs
import locale
def run1(args):
	run(args[0])


def run(args):
  try:
    #sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);
    if sys.platform == "win32":
        class UniStream(object):
            __slots__= ("fobj", "softspace",)

            def __init__(self, fileobject):
                self.fobj = fileobject
                #self.fileno = fileobject.fileno()
                self.softspace = False

            def write(self, text):
                try:
                    fno = self.fobj.fileno()
                    os.write(fno, text.encode("cp866") if isinstance(text, unicode) else text)
                except BaseException as e:
                    traceback.print_exc()
                    #self.fobj.write(text)

        sys.stdout = UniStream(sys.stdout)
        sys.stderr = UniStream(sys.stderr)

    print "run "+str(args)
    if args.action=='log':
        aw = timelog.TimeLog(args)
        aw.monitor_active_window()
        return 0

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
        print "directory:"+str(args.dir)+", file:"+args.file
       	logfiles = [ f for f in glob.glob(os.path.join(args.dir,args.file)) if os.path.isfile(os.path.join(args.file,f)) ]
        logfiles = sorted(logfiles)
        for f in logfiles:
            if (os.path.getmtime(f)*1000-opts.min_start>=0):
                print "processing "+f
                opts.process_file(f)
#            else:
#                print "skipped "+f
        taglist = args.pattern #[0].split(' ')
        print taglist
        opts.total.query(set(taglist),opts)
        return 0
  except BaseException as e:
      traceback.print_exc()
      var = traceback.format_exc()
      f=open("err","w")
      f.write(str(e)+"\n"+var)
      f.close()
      print var
      return 1
