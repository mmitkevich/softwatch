import actmon
import time
import os
from subprocess import Popen, PIPE
import re

class TimeLog:



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

    def escape(self, str):
        #Surround the string in double quotes and escape any pre-existing double quotes
        return '"%s"' % str.replace("\"", "\\\"")

    def unescape(self, str):
        #Remove surrounding double quotes and replace escaped double quotes
        m = re.match("^\"(.*)\"$", a)
        if m != None:
            str = m.group(1)

        return str.replace("\"", "\\\"")

    def get_current_time(self):
        return "%d" % (time.time() * 1000)

    @staticmethod
    def log_window(logfile, currentcommand, currentwindow):
        with open(logfile, "aF+") as f:
            moreinfo = ""
            if re.search("chrom",currentcommand):
                (moreinfo,err) =  Popen(['chromix', 'url'], stdout=PIPE).communicate()

            logstring = "%s %s %s %s\n" % (self.get_current_time(), self.escape(currentcommand), self.escape(currentwindow), self.escape(moreinfo))
            f.write(logstring)
            f.flush()
            print logstring

    def monitor_active_window(self):
        max_idle_timeout = 3
        cur_idle = False
        lastwindow = None

        try:
            while True:
                curpid, currentwindow = self.get_active_window()
                if currentwindow != lastwindow:
                    currentcommand = self.get_process_command_from_id(curpid)
                    self.log_window(self.logfile, currentcommand, currentwindow)
                    lastwindow = currentwindow
                idle = actmon.get_idle_time() > max_idle_timeout*1000
                if idle!=cur_idle:
                    cur_idle=idle
                    if idle:
                        self.log_window(f, "<idle>", "idle for %d"%max_idle_timeout )
                    else:
                        self.log_window(f, currentcommand, currentwindow)
                time.sleep(1)
        except KeyboardInterrupt:
            self.log_window(f, 'activewindow', 'ActiveWindow terminated')
            print ""
