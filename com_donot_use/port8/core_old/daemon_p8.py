import os,sys, time, daemonocle, subprocess
from com.port8.core.scheduler import Scheduler
from com.port8.core.globals import Global
from com.port8.core.infrautils import InfraUtility


class DaemonP8(object):
    def __init__(self, daemonNameArg, daemonArg):

        self.myDaemonName = daemonNameArg
        self.myDaemon = daemonArg

        self.sched = Scheduler()
        self.InfraUtil = InfraUtility()
        self.Global = Global()
        self.Infra = self.InfraUtil.setInfra(self.Global.DaemonInfraKey)

        self.DaemonLogger = self.Infra.getInfraLogger(self.Global.DaemonInfraKey)

        if not self.Infra:
            raise InfraInitializationError('Could not initialize {cls}'.format(cls=(self.myModulePyFile,self.myClass)))


        self.myAllDaemonConfig = self.Infra.daemonConfigData

        if self.myDaemonName not in self.myAllDaemonConfig:
            print ("Invalid daemon {daemon}, valid daemon lists >>> {daemonList} ".format(daemon = self.myDaemon, daemonList = self.myAllDaemonConfig.keys())) 
            sys.exit(-1)

        # loading daemon config data
        self.DaemonLogger.debug('{daemon} : loading configuration '.format(daemon = self.myDaemonName))
        self.__loadDaemonConfigData()

    def __getPidFile(self,pidPathArg, pidFileArg):

        if os.path.isdir(pidPathArg):
            return os.path.join(pidPathArg, pidFileArg)

    def __loadDaemonConfigData(self):

        self.myDaemonConfig = self.myAllDaemonConfig[self.myDaemonName] 
        self.myPidFile = self.__getPidFile(self.myDaemonConfig['PidFileLocation'], self.myDaemonConfig['PidFile'])
        self.myWorkDir = self.myDaemonConfig['WorkingDir']
        self.detach = self.myDaemonConfig['detach']
        self.prog_name = self.myDaemonConfig['prog_name']
        self.stop_timeout = self.myDaemonConfig['stop_timeout']
        self.myDaemonCmdList = self.myDaemonConfig['CommandList']

    def startDaemon(self):
        self.DaemonLogger.info('Daemon {daemon} is starting ...'.format(daemon = self.myDaemonName))

        if self.myDaemonName == 'Scheduler':
            self.sched.startScheduler()
            while True:
                self.DaemonLogger.debug('Still running')
                time.sleep(10)

    def stopDaemon(self,message,code):

        self.DaemonLogger.info('Daemon {daemon} is stoping with message {msg} and code {code} ...'.format(daemon = self.myDaemonName, msg = message, code = code))
        if self.myDaemonName == 'Scheduler':
            #self.logger.debug(message, code)
            self.sched.stopScheduler()


if __name__ == '__main__':
    
    myDaemonCmdList = ['start','stop','status','restart']
    print(sys.argv)
    myDaemonCmd = sys.argv[1]
    myDaemonName = sys.argv[2]

    if (len(sys.argv) < 3) or (myDaemonCmd not in myDaemonCmdList):
        print('usage: <python executable>(3) {file} cmd <{cmd}> <daemon_name>'.format(file = os.path.basename(__file__), cmd = myDaemonCmdList))
        sys.exit(-1)

    daemon = daemonocle.Daemon()
    myDaemon = DaemonP8(myDaemonName, daemon)

    daemon.pidfile = myDaemon.myPidFile
    daemon.detach = myDaemon.detach
    daemon.worker = myDaemon.startDaemon
    daemon.shutdwon_callback = myDaemon.stopDaemon
    daemon.prog = myDaemon.prog_name
    daemon.stop_timeout = myDaemon.stop_timeout

    print('\n')

    myDaemon.DaemonLogger.debug('executing {cmd} on daemon {daemon}'.format(cmd = sys.argv[1], daemon = sys.argv[2]))
    daemon.do_action(sys.argv[1])
    
