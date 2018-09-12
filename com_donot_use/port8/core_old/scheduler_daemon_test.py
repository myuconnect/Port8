#!/usr/bin/env python

import sys, time
from daemon import Daemon
from apscheduler.schedulers.blocking import BlockingScheduler
from com.port8.core.scheduler import Scheduler
class MyDaemon(Daemon):
    def run(self):
            scheduler = Schdeuler()
            scheduler.scheduler.start()
            #sched = BlockingScheduler(schedBase[SchedConfigData['])
            #sched.start()
            def some_job():
                    curt = time.ctime()
                    myfile = open("/root/yyin/mytest", "a+")
                    myfile.write(curt)
                    myfile.write("\n")
                    myfile.close()
            #sched.add_cron_job(some_job, minute="*/1")
            while True:
                time.sleep(10)

if __name__ == "__main__":
        daemon = MyDaemon('/tmp/schedule.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print ("Unknown command")
                        sys.exit(2)
                sys.exit(0)
        else:
                print ("usage: %s start|stop|restart" % sys.argv[0])
sys.exit(2)