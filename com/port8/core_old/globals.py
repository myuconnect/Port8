from com.port8.core.singleton import Singleton

class Global(object, metaclass=Singleton):
    def __init__(self):
        #
        self.LogPathEnvKey = 'LOG_PATH'
        self.InitFile="init.json"
        self.InitKeys=('AppName','AppHome','Environment','bootStrapCfg',"LOG_LOC")
        self.BootStrapKey='bootStrapCfg'
        self.BootStrapFileKey='BOOOTSTRAP_FILE'
        self.LogLocKey="LOG_LOC"

        #Infrastructure
        self.InfraLib = 'com.port8.core.infrastructure'
        self.Infrastructure = {'Rest':'RestInfra','Scheduler':'SchedInfra','Daemon':'DaemonInfra'}
        self.RestApiInfraKey = 'Rest'
        self.SchedulerInfraKey = 'Scheduler'
        self.DaemonInfraKey = 'Daemon'

        # error
        self.DefPrefix4Error = '  >'
        self.DefPrefixCount = 3

        #db'
        '''
        self.DBRequiredArg = \
            {'Create':['operation','container','dataDict','commitWork'],
             'Change':['operation','container','criteria','dataDict','commitWork'],
             'Remove':['operation','container','criteria','commitWork']
            }
        self.DBOperations = ['create','change','remove','get']
        '''
        self.create = 'create'
        self.change = 'change'
        self.remove = 'remove'
        self.fetch = 'fetch'
        self.allDbOperation=[self.create, self.change, self.remove, self.fetch]
        self.container = 'container'
        self.mySqlVarHolder = '%s '
        self.ChkContainerExistSql = "select table_name from information_schema.tables where table_name = %s "
        self.commitWorkDefaultValue = True
        self.defaultError4Number = '-1'
        self.defaultCriteria = ' 1 = 1 '

        #logging
        self.LoggingConfig = 'loggingConfig.json'
        self.RestLoggerNameKey = 'REST'
        self.SchedLoggerNameKey = 'SCHEDULER'
        self.DaemonLoggerNameKey = 'DAEMON'
        self.DefaultLoggerNameKey = 'DEFAULT'
        self.LoggerName = \
         {
            "REST":{"Name":"Rest","LogFile":"restApiPort8.log"},
            "SCHEDULER":{"Name":"apscheduler","LogFile":"schedulerPort8.log"},
            "DAEMON":{"Name":"Daemon","LogFile":"daemonPort8.log"},
            "DEFAULT":{"Name":"Console","LogFile":""}            
        }

        #Scheduler
        self.ScheduleConfig = 'schedulerConfig.json'
        self.Schedulers = ['Blocking','Background']
        self.CurrentScheduler = 'Blocking'
        self.SchedulerMode = ['Run','Maintenance']
        self.JobIdPrefixValue = 'port8'
        self.SchedConsecFailCntThreshold = 3
        self.NextJobRun = 'Waiting for next run'
        self.SuspendMode = 'Suspended'
        self.DefaultSchedulerType ='Background'
        self.DefaultSchedulerMode ='Maintenance'

        #template
        self.Template = \
            {
                "Response":{'Status':'','Data':{},'Message':''}
            }
        self.ResponseTemplate = 'Response'
        self.Success = 'Success'
        self.UnSuccess = 'UnSuccess'        
        self.Response = {'Status':'','Data': {},'Message':''}

        #misc
        self.ResponseModeList = ['I','E']        
        self.keyword = 'keyword'
        self.positional = 'positional'

    #def __call__(self):
    #    print('Call is prohibited')
