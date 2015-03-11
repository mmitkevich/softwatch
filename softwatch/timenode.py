#!/usr/bin/python
import sys
import re
import time
import shlex
from sortedcontainers import SortedSet
import re
import traceback
import math
from collections import deque

class TimeQueue:
    def __init__(self,period):
        self.q = deque()
        self.period=period

    def put(self,time,value):
        self.q.append(dict(time=time,value=value))
        if len(self.q)>0 and time<self.q[0]['time']:
            print 'negative q'
        while time-self.q[0]['time']>self.period:
            self.q.popleft()
        #if len(self.q)>0:
        #    print TimeNode.fmt_time(time), (time-self.q[0]['time'])/1000/60.

    def sum(self):
        return reduce(lambda s,e: s+e['value'],self.q,0)


    def time(self):
        return self.q[-1]['value']

    def pstart(self):
        return self.q[0]['time']

    def start(self):
        return self.q[-1]['time']

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
        self.cats = None
        self.away = TimeNode("*AWAY*")
        self.total = TimeNode('*ONLINE*')
        self.iline = 0
        self.ptime = 0
        self.pitems = []
        self.pidle = 0
        self.relative = False


    def nperiods(self):
        if not self.relative:
            return 1.
        return (self.total.time+self.away.time)*5./7./1000./3600/24

    def process_file(self, in_file):
        self.iline = 0
        file = open(in_file,'r')


        for line in file.readlines():
            try:
                items = shlex.split(line)
                time = int(items[0])
                if time<self.min_start:
                    continue
                if time>=self.max_start:
                    break
                self.process(items,time, 1000000000)

            except BaseException as e:
                print("%s(%d): syntax error %s "%(in_file,self.iline,e))
                traceback.print_exc(e,sys.stdout)
#               raise Error(e)

    @staticmethod
    def sample(start,time,taglist):
        if len(taglist)==0:
            print "empty taglist in sample"
        return TimeSample(start, time, taglist)

    def process(self, items, time, keeptime = 0):
        self.iline += 1
        if self.ptime==0:
            self.ptime=time
            self.pitems=items
            return None
        else:
            tidle=0
            if items[2].startswith("idle"):
                self.pidle = time
            else:
                if self.pidle!=0:
                    #if time-self.pidle<5*60*1000:
                    #    return None
                    tidle=time-self.pidle
                    self.pidle = 0
            awords = re.compile('[ /:?&|=\\,@#\]\[\(\)]+').split((self.pitems[2]+" "+self.pitems[3]).lower())
            words = filter(lambda w: re.compile('[a-zA-Z]').search(w),awords)
            #if len(awords)!=len(words):
            #    print "1"
            dt = time-self.ptime
            if dt<0:
                #print 'negative staart'
                return
            away_timeout=15*60*1000 # 15min max work per single program. rest time is 'away'
            mytask=None
            if tidle>0:
                if keeptime>0:
                    self.away.put([],self.sample(self.ptime,tidle,words)) #,str(int(dt/away_timeout))+'x'
            elif (dt>away_timeout):
                smpl = self.sample(self.ptime,away_timeout,words)
                if keeptime>0:
                    self.total.put(words, smpl)
                if keeptime>0:
                    self.away.put([],self.sample(self.ptime+away_timeout,dt-away_timeout,words)) #,str(int(dt/away_timeout))+'x'
                mytask = smpl.task = self.tasks.putExpr("*AWAY*", smpl)
            else:
                smpl = self.sample(self.ptime,dt,words)
                mytask = smpl.task = self.tasks.putExpr(words, smpl)
                if keeptime>0:
                    if mytask:
                        words = ["["+mytask.tag+"]"]+words
                    self.total.put(words, smpl,10)
            self.ptime = time
            self.pitems = items
            return mytask

    def sort_tasks(self):
        temp = [ x for x in self.tasks.children]
        self.tasks.children.clear()
        for t in temp:
            self.tasks.children.add(t)


class TimeSample:
    def __init__(self, start = time.time(), time = 0, tags = []):
        self.time = time
        self.start = start
        self.tags = tags
        self.task = None

class TimeNode:
    def __init__(self, tag, parent = None, time = 0, count = 0, tqueue = None,expr=[]):
        self.tag = tag
        self.count = count
        self.time = time
        #self.wcount = wcount
        self.children = SortedSet(key=lambda node:-node.time)
        self.samples = []
        self.parent = parent
        self.expr = expr
        self.tqueue = TimeQueue(60*60*1000)
        if tqueue:
            self.tqueue.q.extend(tqueue.q)


    #def alpha(self, tn, tp):
    #    return 1-math.exp(-(tn-tp)/self.eperiod)


    def path(self):
        pth = []
        n = self
        while n.parent:
            n=n.parent
            pth.insert(0,n)
        pth.append(self)
        return pth

    @staticmethod
    def delta(tag, a, b):
        node = TimeNode(tag, None, a.time-b.time, a.count-b.count)
        #node.wtime=[]
        #node.wcount=a.wcount-b.wcount
        return node

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

    def update_wtime(self, smpl):
        self.tqueue.put(smpl.start,smpl.time)


    def put(self, taglist, sample, maxlevel=-1):
        if sample.time<0:
            print "negative time!"

        alpha = 0.001 #self.alpha(sample.start,self.laststart)

        if len(taglist)==0 or maxlevel==0:
            self.samples.append(sample)
            self.count += 1
            self.time += sample.time

            #try:
            #    self.wcount = alpha*1+(1-alpha)*self.wcount
            #    self.wtime = alpha*sample.time+(1-alpha)*self.wtime#sample.time
            #except BaseException as e:
            #    pass
            self.update_wtime(sample)
                #self.wcount=self.count
            return [1, sample.time]

        best_child = None
        for child in self.children:
            if child.tag in taglist:
                best_child = child
                break

        if not best_child:
            best_child = TimeNode(taglist[0],self,0,0)
        else:
            self.children.remove(best_child)

        [dc, dtime] = best_child.put([t for t in taglist if t!=best_child.tag], sample, maxlevel-1)
        self.children.add(best_child)
        self.count += dc
        self.time += dtime
        #self.wcount = alpha*dc+(1-alpha)*self.wcount
        #self.wtime = alpha*dtime+(1-alpha)*self.wtime
        #print self.tag,"=",self.wtime
        self.update_wtime(sample)
        return [dc, dtime]

    def match(self, taglist):
        for alt in self.expr:
            if all(token in taglist for token in alt):
                return True
        return False

    def putExpr(self, taglist, sample, keepSamples=False):
        if sample.time<0:
            print "negative time!"
        res = None
        for child in self.children:
            if child.match(taglist):
                if keepSamples:
                    child.samples.append(sample)
                child.count += 1
                child.time += sample.time
                self.count += 1
                self.time += sample.time
                self.tqueue.put(sample.start,sample.time)
                res = child
                break
        if not res and taglist!="*OTHER*":
            res=self.putExpr("*OTHER*",sample,keepSamples)
        return res

    @staticmethod
    def fmt_delta_time(time):
        time=int(time/1000)
        days, remainder = divmod(time,3600*24)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        s1 = '     ' if days<1 else "%3dd "%days
        s1 = s1+'%02d:%02d:%02d' % (hours, minutes, seconds)
        return s1

    @staticmethod
    def fmt_time(start):
        #return time.ctime(int(start/1000))
        return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(int(start/1000)))

    def checkremove(self,tag,tagfilters):
        for filt in tagfilters:
            if re.compile(filt).search(tag):
                tagfilters.remove(filt)
                return True
        return False

    def query(self, tagset, options, indent=0, orig_parent=None):
        next = self

        if not orig_parent:orig_parent=options.total

        tagset = set(tagset)
        printnode = options.printnode if options.printnode else self.printnode

        self.checkremove(next.tag, tagset)

        pathstr = next.strpath(options.tree>0)
#        print "QUERY:",options.min_time,next.time
        while len(next.children)>0 and ((next.time-next.children[0].time)<=0):# or (100.*next.children[0].time/options.total.time)>=100.-options.min_percent):
#              print "joining "+options.min_time
              options.other.time+=next.time-next.children[0].time
              options.other.count+=next.count-next.children[0].count
              #options.total.time+=next.time-next.children[0].time
              #options.total.count+=next.count-next.children[0].count
              next = next.children[0]
              pathstr = pathstr+'-'+next.tag
              self.checkremove(next.tag, tagset)

        skip = False
        if len(tagset)==0 and options.tree>0:
            if  (next.time>=options.min_time*options.nperiods()):
                printnode(next, pathstr,options, orig_parent)
            else:
                #printnode(next, "SKIP:"+pathstr,options, orig_parent)
                if orig_parent.tag=="*ONLINE*":
                    options.other.time=options.other.time+next.time
                    options.other.count=options.other.count+next.count
                skip=True

        if not skip:
            limit = options.limit
            p = next if options.tree>0 else options.total
            explained = 0.

            for child in next.children:
              #explained=explained + 100.*child.time/p.time
              if (options.tree==0 or indent<options.tree):# and (100.*child.time/options.total.time>options.min_percent):
                child.query(tagset, options, indent+1,next)
                limit-=1

            #if len(tagset)==0  and options.tree==0 and limit==options.limit:
            if len(tagset)==0  and options.tree==0 and (next.time>options.min_time*option.nperiods())  and limit==options.limit:
               options.rating.children.add(TimeNode(pathstr, None, next.time,next.count,next.tqueue))

        if indent==0:
            explained = 0
            for n in options.rating.children:
                explaineds=explained + 100.*n.time/options.total.time
                if explained>100.-options.min_percent:
                    break
                printnode(n,n.tag,options)
            printnode(options.other, None, options)
            if 0==options.tree:
                printnode(options.total,None,options)
            printnode(options.away, None, options)

            options.sort_tasks()
            print();
            printnode(options.tasks,None,options)
            for n in options.tasks.children:
                if n.time>0:
                    printnode(n,n.tag,options)


    @staticmethod
    def printsample(samp, text):
        tsk=""
        if samp.task:
            tsk = "["+samp.task.tag+"] "
        print("|%s|%s|%s%s"%(TimeNode.fmt_delta_time(samp.time), TimeNode.fmt_time(samp.start), tsk,' '.join(samp.tags)))


    @staticmethod
    def printnode(node, text = None, options = None, parent=None):
        if not text:
            text = node.tag
        percent = 100.
        if options and options.total.time>0: #and 0==options.tree
            percent = 100. * node.time / (options.total.time)
        #if options and options.tree>0:
        #    p = parent or options.total
            #p = node.parent if node.parent else options.total
            #while p.parent and 100.*node.time/p.time>=99-options.min_percent:
            #    p=p.parent
        #    percent = 100. * node.time / (p.time)

        nperiods = options.nperiods()
        stime=node.tqueue.sum()
        print('%s|%s|%5d|%4.1f%%|%s' % (TimeNode.fmt_delta_time(int(node.time/nperiods)), TimeNode.fmt_delta_time(stime), node.count, percent, text))

        printsample = options.printsample if options.printsample else TimeNode.printsample
        if options.samples:
            for samp in node.samples:
                printsample(samp, ' '.join(samp.tags))



def loadTasks(in_file):
    tasks = TimeNode("=TASKS=")
    try:
        file = open(in_file,'r')

        for line in file.readlines():
            if line[0]=='#':
                continue
            kv = line.split('==')
            if len(kv)<2:
                print "invalid category:\n"+line
                continue
            tag = kv[0].strip();
            tn = TimeNode(tag)
            tn.expr = [[y.strip() for y in x.split(' ') if len(y.strip())>0] for x in kv[1].split('||')]
            tasks.children.add(tn)
        file.close()
    except BaseException as e:
        print("failed to load tasks: %s"%(e))
    return tasks
