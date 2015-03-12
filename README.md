softwatch
=========

Tracks and reports time spent by linux desktop user on differenet applications and tasks. 
Background daemon records focused X11 window caption and timestamps when focus changes (also for chromium url is extracted). 
Each caption is split into keywords set.

Daemon could be started using
```bash
python softwatch.py log
```

Logs are recorded into $HOME/.mytime/YYYY-MM-DD.log files 

To analyze logs use the following command

```
python softwath.py report [-bN] [-eN] [-tN] [-mN] [-dN]
```

Switches:
-bN:  do not analyze files with age more than N days. Default: use all data
-eN:  do not analyze files with age less than N days. Default: use all data
-tN:  show tree of N maximum levels. If not specified, full tree is shown. -t0 means flat 'digest' mode. 
-dN:  show only items with duration more than N minutes. Default is 0
-mN:  show only items with duration more than N percent of  total time. Default is 0
-r:   scale time so the time is relative to 5 working days week (So you should see 8hrs per day if you work 5/7). Default is OFF

Examples:

- show today report (only 5%+ items)
```
mike@bukake:~/github/softwatch$ mytime report -b1 -m5
     09:22:59|36:21|  781|100.0%|*ONLINE*
     04:42:00|33:27|  200|50.1% |-softwatch
     04:41:56|33:27|  197| 50.1%|--github
     03:51:54|33:24|   98| 41.2%|---timenode.py-intellij-idea-cardea-iu-135.1019
     02:51:54|18:24|   94| 30.5%|--------[mytime]
     00:35:01|00:03|   98|  6.2%|---[mytime]
     03:36:42|00:35|  386| 38.5%|-google-chrome
     00:34:50|01:21|   44|  6.2%|---gmail
     03:56:46|00:00|  498|42.1%|*OTHER*
     14:20:53|02:48|    8|152.9%|*AWAY*
     
     03:59:05|18:27|  231|42.5%|=TASKS=
     03:29:46|18:27|  198|37.3%|mytime
     00:27:44|00:48|   15| 4.9%|JOB
     00:01:23|00:36|   17| 0.2%|TRADING
```

This report states that I've been online 9h22 mins last 24hrs. 
And used 4h42 mins (50.1%) of that time to develop [mytime] project (softwatch actually)
The rest time 3h36 mins were spent in google-chrome
All other activities (e.g. those which took less than 5% of total time) in total used 42.1% of my time.

The bottom part shows =TASKS= 

Each task is defined in ~/.mytime/tasks.cat file. Here is example
````
PROJECT1 == app1 || app2
FUN == myfavoritepornsite
JOB == person1 || person2 || person3 || person4
LOVE == my_wife_hangouts_login
mytime == softwatch
```

If -m switch is ommitted, report will become quite huge containing all your keywords combination as tree.

- show today hotspots

```python softwatch.py report -b1 -m1 -t0

```


This is experimental (pre-alpha) software. Use on your own risk.




