#!/usr/bin/env python3.5
import sys
import os
import time
import argparse
import logging
import daemon
from daemon import pidfile

debug_p = False

def do_something(logf):
    ### This does the "work" of the daemon

    logger = logging.getLogger('eg_daemon')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(logf)
    fh.setLevel(logging.INFO)

    formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(formatstr)

    fh.setFormatter(formatter)

    logger.addHandler(fh)

    while True:
        logger.debug("this is a DEBUG message")
        logger.info("this is an INFO message")
        logger.error("this is an ERROR message")
        logger.info("Current pid is {pid}".format(pid=os.getpid()))        
        time.sleep(5)


def start_daemon(pidf, logf):
    ### This launches the daemon in its context

    ### XXX pidfile is a context
    with daemon.DaemonContext(
        working_directory='/home/anil/app/log',
        umask=0o002,
        pidfile=pidfile.TimeoutPIDLockFile(pidf),
        ) as context:
        do_something(logf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example daemon in Python")
    parser.add_argument('-p', '--pid-file', default='/home/anil/app/log/daemon.pid')
    parser.add_argument('-l', '--log-file', default='/home/anil/app/log/daemon.log')

    args = parser.parse_args()

    start_daemon(pidf=args.pid_file, logf=args.log_file)