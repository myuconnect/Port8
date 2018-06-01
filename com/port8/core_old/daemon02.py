import os, grp, daemon, signal, lockfile
from com.port8.core.scheduler import Scheduler

#with daemon.DaemonContext():
#    do_main_program()

#More complex example usage:
print('instantiating scheduler')
sched = Scheduler()
print('in context')
context = daemon.DaemonContext(
    working_directory='/home/anil/app/src/daemon',
    umask=0o002,
    pidfile=lockfile.FileLock('/home/anil/app/src/daemon/scheduler.pid',
    chroot='/home/anil/app/src/daemon',
    detach_process = True),
    )

context.signal_map = {
    signal.SIGTERM: sched.stopScheduler(),
    signal.SIGHUP: 'terminate'
    #signal.SIGUSR1: reload_program_config,
    }

#mail_gid = grp.getgrnam('mail').gr_gid
#context.gid = mail_gid

important_file = open('spam.data', 'w')
interesting_file = open('eggs.data', 'w')
context.files_preserve = [important_file, interesting_file]

#initial_program_setup()
#context.open(detach_process=True)

with context:
    sched.startScheduler()
