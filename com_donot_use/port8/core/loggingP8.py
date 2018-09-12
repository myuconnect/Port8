from com.port8.core.environment import Environment
from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utility import Utility

import os,sys,json,traceback,logging, logging.config

class Logging(object, metaclass=Singleton):

    def __init__(self):
        self.env = Environment()
        self.Global = Global()
        self.Utility = Utility()
        #myLogger = self.__buildLoggingInfra(logging_cfg = loggingCfgData, logger = logger)
        #return myLogger

        #return myLogger

    #def __buildLoggingInfra(self, loggingCfg, logFile = None , logger = 'Default'):
    def buildLoggingInfra(self, loggingCfgData, logFile, logger):
        ''' Logging utility, constructing dictionary object to be used by native logging module
        Arguments:
            loggingCfgData: Logging configuration
            logFile: LogFile need to be written
            logger: name of logger
        Level: 
        ++++++++++++++++++++
        CRITICAL    50
        ERROR   40
        WARNING 30
        INFO    20
        DEBUG   10
        NOTSET  0
        ++++++++++++++++++++
        '''
        try:

            #validating parameter

            if ( not loggingCfgData):
                print("missing logging configuraton data !!!")
                sys.exit(-1)
            #fi

            #myLogPath = self.env.
            #print('LogPath',myLogPath)
            #myConfigFile = os.path.join(self.env.getConfigLocation(), os.path.basename(argCfgFile))

            # check if logging config file is available
            #if not self.env.isFileExists(myConfigFile):
            #    print("could not locate Logging Config file {cfgFile}, terminating !!!".format(cfgFile=myConfigFile))
            #    sys.exit(-1)
            #fi

            # reading current config file
            myLoggingConfig = self.Utility.getACopy(loggingCfgData)


            # checking if we got valid logger name, if not will use default logger name "Console"
            if logger not in myLoggingConfig['loggers']:
                myLogger = self.Global.LoggerName[self.Global.DefaultInfra]['Name']
            else:
                myLogger = logger
            #fi

            # will override logfile if passed as an argument also, set the directory as defined in LOG_LOC env variable
            if logFile:
                # will use the path as specified in LOG_PATH environment variable, any path specified in argument will be ignored
                myLogFile = os.path.basename(logFile)
                myLogFileWPath = os.path.join(self.env.appLogLoc,myLogFile)
            else:
                myLogFileWPath = os.path.join(self.env.appLogLoc,os.path.basename(myLoggingConfig['handlers']['file']['filename']))
            #fi

            if not(myLogger == self.Global.DefaultInfra):
                myLoggingConfig['handlers']['file']['filename'] = myLogFileWPath

            # Loading current configuration to logger's config file
            logging.config.dictConfig(myLoggingConfig)
            #print('Logger',myLogger)
            return logging.getLogger(myLogger)

        except Exception as err:
            print ("\n")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

            print ("Error [{err}] builidng logging infra using config [{cfg}], terminating !!!".format(err=myErrorMessage, cfg=myLoggingConfig))
            sys.exit(-1)