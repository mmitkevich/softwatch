#!/usr/bin/python
import sys
import re
import time
import shlex
from sortedcontainers import SortedSet
import re

class TimeQuery:
    def __init__(self, min_time=60*1000,max_time=100*3600*1000,limit=1000000,max_depth=1000,samples=False,tree=True):
        self.min_time = min_time        # minimum aggregated time for class per day
        self.max_time = max_time        # maximum aggregated time for class per day
        self.limit = limit              # output not more than limit of subcategories
        self.max_depth = max_depth
        self.samples = samples          # show raw samples in each class
        self.tree = tree
        self.rating = TimeNode("*RATING*")
        self.printnode = None
        self.printsample = None
        self.other = TimeNode("*OTHER*")
        self.min_start = 0
        self.max_start = sys.maxint

class TimeSample:
    def __init__(self, start = time.time(), time = 0, tags = []):
        self.time = time
        self.start = start
        self.tags = tags

class TimeNode:
    def __init__(self, tag, parent = None, time = 0, count = 0):
        self.tag = tag
        self.count = count
        self.time = time
        self.children = SortedSet(key=lambda node:-node.time)
        self.samples = []
        self.parent = parent

    def path(self):
        pth = []
        n = self
        while n.parent:
            n=n.parent
            pth.insert(0,n)
        pth.append(self)
        return pth

    def strpath(self, notext=True):
        if notext:
            return '-'*(len(self.path())-1)+self.tag
        else:
            return '-'.join(map(lambda n:n.tag,(self.path()[1:])))


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.tag == other.tag
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.tag)

    #def __cmp__(self, other):
    #    return -(self.time-other.time)

    def put(self, taglist, sample, maxlevel=-1):
        if sample.time<0:
            print "negative time!"

        if len(taglist)==0 or maxlevel==0:
            self.samples.append(sample)
            self.count += 1
            self.time += sample.time
            return [1, sample.time]

        best_child = None
        for child in self.children:
            if child.tag in taglist:
                best_child = child
                break

        if not best_child:
            best_child = TimeNode(taglist[0],self)
        else:
            self.children.remove(best_child)

        [dc, dtime] = best_child.put([t for t in taglist if t!=best_child.tag], sample, maxlevel-1)
        self.children.add(best_child)
        self.count += dc
        self.time += dtime
        return [dc, dtime]

    def fmt_delta_time(self,time):
        time=int(time/1000)
        days, remainder = divmod(time,3600*24)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        s1 = '     ' if days<1 else "%3dd "%days
        s1 = s1+'%02d:%02d:%02d' % (hours, minutes, seconds)
        return s1

    def fmt_time(self, start):
        #return time.ctime(int(start/1000))
        return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(int(start/1000)))

    def checkremove(self,tag,tagfilters):
        for filt in tagfilters:
            if re.compile(filt).search(tag):
                tagfilters.remove(filt)
                return True
        return False

    def query(self, tagset, options, indent=0):
        next = self
        tagset = set(tagset)
        printnode = options.printnode if options.printnode else self.printnode

        self.checkremove(next.tag, tagset)

        pathstr = next.strpath(options.tree)

        while len(next.children)>0 and (next.time-next.children[0].time)<=options.min_time:
              options.other.time+=next.time-next.children[0].time
              options.other.count+=next.count-next.children[0].count
              next = next.children[0]
              pathstr = pathstr+'-'+next.tag
              self.checkremove(next.tag, tagset)

        if len(tagset)==0 and options.tree:
            printnode(next, pathstr,options)

        limit = options.limit
        for child in next.children:
          if indent<options.max_depth and limit>0 and (child.time>options.min_time):
            child.query(tagset, options, indent+1)
            limit-=1
          else:
            options.other.time+=child.time
            options.other.count+=child.count

        if len(tagset)==0  and not options.tree and limit==options.limit:
           options.rating.children.add(TimeNode(pathstr, None, next.time,next.count))

        if indent==0:
            for n in options.rating.children:
                printnode(n,n.tag,options)
            printnode(options.other, "*OTHER*", options)
            printnode(self,"*TOTAL*",options)

    def sample(self,start,time,taglist):
        return TimeSample(start, time, taglist)

    def printsample(self,samp, text):
        print("%s | %s | %s"%(self.fmt_delta_time(samp.time),next.fmt_time(samp.start), ' '.join(samp.tags)))

    def printnode(self, node, text, options = None):
        print('%s | %5d | %s' % (self.fmt_delta_time(node.time), node.count, text))

        printsample = options.printsample if options.printsample else self.printsample
        if options.samples:
            for samp in node.samples:
                printsample(samp, ' '.join(samp.tags))

    def read(self, in_file, options):
        iline = 0
        file = open(in_file,'r')
        ptime = 0
        pitems = []
        pidle=0
        for line in file.readlines():
           iline += 1
           try:
            items = shlex.split(line)
            time = int(items[0])
            if time<options.min_start:
                continue
            if time>=options.max_start:
                break
            if ptime==0:
                ptime=time
                pitems=items
            else:
                if pitems[2].startswith("idle"):
                    pidle = time
                else:
                    if pidle!=0:
                        if time-pidle<5*60*1000:
                            continue
                        pidle=0
                awords = re.compile('[ /:?&|=\\,@#\]\[\(\)]+').split((pitems[2]+" "+pitems[3]).lower())
                words = filter(lambda w: re.compile('[a-zA-Z]').search(w),awords)
                #if len(awords)!=len(words):
                #    print "1"
                dt = time-ptime
                away_timeout=15*60*1000 # 15min max work per single program. rest time is 'away'
                if dt>away_timeout:
                    self.put(words, self.sample(ptime,away_timeout,words))
                    self.put(['*AWAY*'],self.sample(ptime+away_timeout,dt-away_timeout,words)) #,str(int(dt/away_timeout))+'x'
                else:
                    self.put(words, self.sample(ptime,dt,words),10)

                ptime = time
                pitems = items

           except BaseException as e:
               print("%s(%d): syntax error %s "%(in_file,iline,e))

