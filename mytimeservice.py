import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import logging
import collections
from run import run
  
class MyTimeSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "MyTimeService"
    _svc_display_name_ = "MyTimeService"
    
    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.stop_event = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False 
        pass
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.stop_requested = True
 
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_,'')
        )
        self.main()
 	
    def main(self):
    	dir = r"C:\Users\Administrator"
        f=open(dir+"\.mytime\svc.log","a")
        try:
         f.write("starting in dir "+dir)
         f.flush()
         MyArgs = collections.namedtuple('MyArgs', 'action dir')
         run(MyArgs(action='log', dir=dir+r'\.mytime'))
         f.write('exiting')
         f.flush()
         sys.exit(0)
        except BaseException as e:
         print e
         f.write(str(e))
        f.close()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyTimeSvc)
#	MyTimeSvc("aa").main()