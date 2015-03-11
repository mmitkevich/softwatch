import actmon
import time
import os
from subprocess import Popen, PIPE
import re
import timenode



class TimeLog:


    def __init__(self, dir, logfilename=None):
        self.dir = dir
        self.logfilename = logfilename or time.strftime("%Y-%m-%d.log")
        self.curfilename = "active"
        self.load_tasks()

#33    #Taken from: http://stackoverflow.com/questions/3983946/get-active-window-title-in-x
    def get_active_window(self):
        (id_w, err) = Popen(['xdotool', 'getwindowfocus'], stdout=PIPE).communicate()

        pid = 0
        name = "Unknown"

        if id_w != None:
            (res, err) = Popen(['xdotool','getwindowname',id_w], stdout=PIPE).communicate()
            if res: name=res.rstrip();
            (res, err) = Popen(['xdotool','getwindowpid',id_w], stdout=PIPE).communicate()
            if res: pid=res.rstrip();

        return (pid, name)

    def get_process_command_from_id(self, processid):
        if processid == 0:
            return ""

        command="<unknown>"
        try:
            command = os.readlink("/proc/%s/exe" % processid)
        except OSError as e:
            print e

        return command

    @staticmethod
    def escape(str):
        #Surround the string in double quotes and escape any pre-existing double quotes
        return '"%s"' % str.replace("\"", "\\\"")

    @staticmethod
    def unescape(str):
        #Remove surrounding double quotes and replace escaped double quotes
        m = re.match("^\"(.*)\"$", a)
        if m != None:
            str = m.group(1)

        return str.replace("\"", "\\\"")

    @staticmethod
    def get_current_time():
        return "%d" % (time.time() * 1000)

    def logtime(self,command = None,window=None):
        command = command or self.currentcommand
        window = window or self.currentwindow
        f = open(os.path.join(self.dir,self.logfilename), 'aF+')

        moreinfo = ""
        if re.search("chrom",command):
            (moreinfo,err) =  Popen(['chromix', 'url'], stdout=PIPE).communicate()

        tsk = self.query.find_task([TimeLog.get_current_time(),command,window,moreinfo],int(time.time() * 1000),10000000)

        self.query.process([TimeLog.get_current_time(),command,window,moreinfo],int(time.time() * 1000),10000000)
        self.logtask(tsk)
        logstring = "%s %s %s %s\n" % (TimeLog.get_current_time(), TimeLog.escape(command), TimeLog.escape(window), TimeLog.escape(moreinfo))
        if f:
            f.write(logstring)
            f.flush()
            f.close()
        print logstring+"-->"+(tsk.tag if tsk else "n/a")

    @staticmethod
    def fmt_delta_time(time):
        time=int(time/1000)
        days, remainder = divmod(time,3600*24)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        #s1 = '     ' if days<1 else "%3dd "%days
        s1=""
        s1 = s1+'%02d:%02d:%02d' % (hours, minutes,seconds)
        return s1

    def load_tasks(self):
        self.query = timenode.TimeQuery(False,False)
        self.query.tasks = timenode.loadTasks(os.path.join(self.dir,"tasks.cat"))
        self.query.tasks.children.add(timenode.TimeNode("*OTHER*",expr=["*OTHER*"]))
        self.query.tasks.children.add(timenode.TimeNode("*AWAY*",expr=["*OTHER*"]))

    @staticmethod
    def fmt_delta_time_mins(time):
        time=int(time/1000)
        days, remainder = divmod(time,3600*24)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        s1 = '%02d:%02d' % (minutes, seconds)
        return s1


    def logtask(self,tsk):
        fname=os.path.join(self.dir, self.curfilename)
        if not os.path.exists(fname):
            self.load_tasks()

        print "logtask ",tsk
        self.query.sort_tasks()
        s="["+(tsk.tag if tsk else "n/a")+"]:"
        n=0
        for t in sorted(self.query.tasks.children,key=lambda t:t.tqueue.sum(),reverse=True):
            if t.time>0 and t.tag!="*OTHER*":
                pct = 100*t.time/self.query.tasks.tqueue.sum()
                s=s+"%2.0f%%%s:" %(pct,t.tag)
                n+=1
                if n>=3:
                    break

        if len(s)>0:
            print "SNAPSHOT: "+s
            f = open(fname,"wt")
            f.write(s)
            f.close();

    def monitor_active_window(self):
        max_idle_timeout = 15
        self.cur_idle = False
        lastwindow = None
        i = 0
        try:
            while True:
                self.curpid, self.currentwindow = self.get_active_window()
                if self.currentwindow != lastwindow:
                    self.currentcommand = self.get_process_command_from_id(self.curpid)
                    self.logtime()
                    lastwindow = self.currentwindow
                idle = actmon.get_idle_time() > max_idle_timeout*1000
                if idle!=self.cur_idle:
                    self.cur_idle=idle
                    if idle:
                        self.logtime("<idle>", "idle for %d"%max_idle_timeout )
                    else:
                        self.logtime()
                time.sleep(1)

        except KeyboardInterrupt:
            TimeLog.logtime('#SIGTERM', 'TimeLog terminated')
            print ""
