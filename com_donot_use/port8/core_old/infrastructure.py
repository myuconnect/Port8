from com.port8.core.environment import Environment
from com.port8.core.singleton import Singleton
from com.port8.core.loggingP8 import Logging
from com.port8.core.globals import Global
from com.port8.core.utils import Utility

from apscheduler.schedulers.background import BackgroundScheduler
from jsonref import JsonRef

import traceback,sys,os,json, importlib

class Infra(object, metaclass=Singleton):

    def __init__(self):

        # setting the Environment
        try:
            self.Env = Environment()
            self.Logging = Logging() 
            self.Global = Global()
            self.Utility = Utility()

            self.initInfra = False
            self.configLoc = self.Env.getConfigLocation()
            self.bootStrapFile = self.getBootStrapFile()
            self.dbConfigData = {}
            self.daemonConfifData = {}
            self.schedulerConfigData = {}
            self.restApiConfigData = {}
            self.agentConfigData = {}

            #print(self.Env._Env__initData)
            #print(self.Env._Env__EnvDetails)

            print("Loading bootstrap config....................".ljust(50),end='')
            self.__loadBootStrapConfig()
            self.__loadSchema()

            # ensuring all needed lib is available
            print("Checking all required libraries................".ljust(50),end='')
            self.__validateAllLib()

            # ensure db is up and repository is abvailable
            print("Validating database............................".ljust(50),end='')      
            self.__validateDb()

            # loading DB schema
            # populating json schema for database
            self.__loadDbJsonSchema()        

            print("[OK - OS pid {pid}]".format(pid=self.getMyOsPid()))

            #self.db_dyna_sql = self.jsonSchema.get('Main').get('db_dyna_sql_call')

            #self.myModuleLogger.info ('Infrastructure started with os pid [{pid}]'.format(pid=os.getpid()))

        except Exception as err:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

            print ('Error [{error}], terminating !!!'.format(error=myErrorMessage))
            sys.exit(-1)

    def __loadBootStrapConfig(self):

        # read bootstrap cnfig file
        try:
            self.__bootStrapData = json.load(open(self.bootStrapFile))

            if not self.__bootStrapData:
                print("Empty bootstrap data, terminating !!!")
                sys.exit(-1) 
            #fi

            # validating if all modules config data is available
            myMissingModule = self.Utility.findMissingKeyInDict(self.__bootStrapData['Main']['Modules'], list(self.__bootStrapData['Main']['ModulesConfig'].keys()))
            if myMissingModule:
                print('Missing config information for module {0}'.format(myMissingModule))
                sys.exit(-1)

            #extracting module config information    
            self.dbConfigData = self.__bootStrapData['Main']['ModulesConfig']['DB'][self.__bootStrapData['Main']['RepositoryDb']]
            self.schedulerConfigData = self.__bootStrapData['Main']['ModulesConfig']['Scheduler']
            self.loggingConfigData = self.__bootStrapData['Main']['ModulesConfig']['Logging']
            self.restApiConfigData = self.__bootStrapData['Main']['ModulesConfig']['RestApi']
            self.daemonConfigData  = self.__bootStrapData['Main']['ModulesConfig']['Daemon']
            self.jsonSchemaConfigData  = self.__bootStrapData['Main']['ModulesConfig']['JsonSchema']

            if (not self.dbConfigData):
                print('DB Configuration is empty')
                sys.exit(-1)

            if (not self.schedulerConfigData):
                print('Scheduler Configuration is empty')
                sys.exit(-1)

            if (not self.loggingConfigData):
                print('Loggine Configuration is empty')
                sys.exit(-1)

            if (not self.restApiConfigData):
                print('RestApi Configuration is empty')
                sys.exit(-1)

            if (not self.restApiConfigData):
                print('Daemon Configuration is empty')
                sys.exit(-1)

            if (not self.jsonSchemaConfigData):
                print('Json Schema Configuration is empty')
                sys.exit(-1)

            print("[OK]")

        except Exception as err:
            myErrorMessage = sys.exc_info()[1:],traceback.format_exc(limit=2)            
            #myErrorMessage = self.Utility.extractError()
            print(myErrorMessage)
            #print("Error [{err}] loading bootstrap config data".format(err=err.message))
            sys.exit(-1)
    #end validateBootStrapConfig

    def __loadSchema(self):
        
        # load json schema data and resolve the reference if used, this will be needed to validate user data

        if not self.Env.isFileExists(os.path.join(self.configLoc,self.jsonSchemaConfigData['configFile'])):
            print('Json Schema Configuration file {file} is missing !!!'.format(file=os.path.join(self.configLoc,self.jsonSchemaConfigData['configFile'])))
            sys.exit(-1)
        #fi
        
        #loading json schema file and resolving references if used in schema
        try:
            self.jsonSchema = JsonRef.replace_refs(json.load(open('/home/anil/app/src/com/port8/config/schema.json')))
        except Exception as err:
            myErrorMessage = sys.exc_info()[1:],traceback.format_exc(limit=2)            
            print (myErrorMessage)
            sys.exit(-1)
        #end 

    def __validateAllLib(self):

        # Ensuring all required library as specified in bootStrap.json is installed
        try:
            for lib in self.__bootStrapData['Main']['Libraries']:
                if not self.isModuleInstalled(lib):
                    #self.myModuleLogger.error('Lib {frmtLib} is not installed, Pls install it using <pip install {frmtLib}>'.format(frmtLib=lib))
                    print("[missing library {frmtLib}]".format(frmtLib=lib))
                    sys.exit(-1)
                #fi
            #end for
            print("[OK]")

        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

            print('[Failed {err}]'.format(err=myErrorMessage))      
            sys.exit(-1)
    # end validateAllLib

    def isValidBootStrapData(self):
        if self.__bootStrapData:
            return True
        else:
            return False
    # end isValidBootStrapData

    def isValidLogger(self):
        if self.myModuleLogger:
            return True
        else:
            return False

    def getBootStrapFile(self):
        
        #print(self.Env._Env__bootStrapFileKey)
        return os.getenv(self.Env._Environment__bootStrapFileKey)
        #mybootStrapFile = os.getEnv[self.Env._Environment__bootStrapKey]

    def getAppName(self):
        return os.Environ['APP_NAME']

    def getMyOsPid(self):
        # returns current OS pid
        return os.getpid()

    def getInfraLogger(self, infraArg):
        if infraArg == 'Scheduler':
            return self.SchedLogger
        elif infraArg == 'Daemon':
            return self.DaemonLogger
        elif infraArg == 'Rest':
            return self.RestLogger

    def isModuleInstalled(self,  argLib):

        # returns existence of a library passed as an argument

        try:
            __import__('imp').find_module(argLib)
            return True
        except ImportError:
            #print('Missing library {lib}'.format(lib=argLib))
            return False
    #end isModuleInstalled

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                  method for DB
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    

    def __validateMySqlDB(self):

        self.dbLib = importlib.import_module('mysql.connector')

        # validate the db config file
        try:
            # connecting to database to ensure db is up
            db = self.dbLib.connect(**self.dbConfigData)

            # connection is successful, closing the connection
            db.close()
            # connection is successful
            print('[OK]')    
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        '''
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

            print('[Failed {err}]'.format(err=myErrorMessage))      
            sys.exit(-1)
        '''
    # end validateMySqlDB

    def __validateDb(self):
        if self.__bootStrapData['Main']['RepositoryDb'] == "MySql" :
            self.__validateMySqlDB()
    #end validateDb

    def __loadDbJsonSchema(self):
        self.dbSchema = self.jsonSchema.get('Main').get('db_schema').get(self.__bootStrapData['Main']['RepositoryDb'])

    def getNewConnection(self):
        try:
            db = self.dbLib.connect(**self.dbConfigData)
            dbCursor = db.cursor(dictionary=True, buffered=True)
            #dbCursor = db.cursor(buffered=True)
            return db, dbCursor
        except Exception as err:
            self.logger.critical('Error obtaining db connection using {}'.format(self.dbConfigData))
            raise err

    def closeConnection(self, dbArg):
        if dbArg:
            dbArg.close()

    def isConnectionOpen(self, dbCursorArg):
        try:
            dbCursorArg.execute('select now()')
            return True
        except Exception as err:
            return False

class RestInfra(Infra, metaclass=Singleton):
    def __init__(self):

        #inheriting Super class variables
        super(RestInfra, self).__init__()

        # creating logger for RestApi infrastructure
        self.RestLogger = \
            self.Logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.Global.LoggerName[self.Global.RestLoggerNameKey]['LogFile'],
                self.Global.LoggerName[self.Global.RestLoggerNameKey]['Name']
                )
        self.RestLogger.debug('this is test from Rest Infrastructure')

        # initalize db
        self.db, self.cursor = self.getNewConnection()

class SchedInfra(Infra, metaclass=Singleton):
    def __init__(self):

        #inheriting Super class variables
        super(SchedInfra, self).__init__()

        # creating logger for Scheduler infrastructure
        self.SchedLogger = \
            self.Logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.Global.LoggerName[self.Global.SchedLoggerNameKey]['LogFile'],
                self.Global.LoggerName[self.Global.SchedLoggerNameKey]['Name']
                )

        self.SchedLogger.info('instantiating scheduler, current os pid [{pid}'.format(pid=os.getpid()))
        self.SchedLogger.info('current os is [{os}]'.format(os=os.uname()))
        self.SchedLogger.info('Scheduler configuration .... \n')
        self.SchedLogger.info('Config Data ---> {data}'.format(data=self.schedulerConfigData))

        self.SchedLogger.debug('this is test from Sched Infrastructure')

        # populating json schema for scheduler
        self.scheduleSchema = self.jsonSchema.get('Main').get('schedule_schema')
        self.intervalSchema = self.jsonSchema.get('Main').get('interval_schema')
        self.cronSchema = self.jsonSchema.get('Main').get('cron_schema')
        self.processJobSchema = self.jsonSchema.get('Main').get('process_job_schema')

        # Load json schema
        self.db, self.cursor = self.getNewConnection()

class DaemonInfra(Infra, metaclass=Singleton):
    def __init__(self):

        #inheriting Super class variables
        super(DaemonInfra, self).__init__()

        # creating logger for RestApi infrastructure
        self.DaemonLogger = \
            self.Logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.Global.LoggerName[self.Global.DaemonLoggerNameKey]['LogFile'],
                self.Global.LoggerName[self.Global.DaemonLoggerNameKey]['Name']
                )
        
        #self.db has already been initialized in super Infra class
        #self.db, self.dbCursor = self.getNewConnection()

        self.DaemonLogger.info('instantiating Daemon, current os pid [{pid}'.format(pid=os.getpid()))
        self.DaemonLogger.info('current os is [{os}]'.format(os=os.uname()))
        self.DaemonLogger.info('Daemon configuration .... \n')
        self.DaemonLogger.info('Config Data ---> {data}'.format(data=self.daemonConfigData))

        self.DaemonLogger.debug('this is test from Daemon Infrastructure')

        # initalize db
        #self.db, self.cursor = self.getNewConnection()

class DBInfra(Infra, metaclass=Singleton):
    def __init__(self):

        #inheriting Super class variables
        super(DBInfra,self).__init__()

        # creating logger for RestApi infrastructure
        self.DBlogger = \
            self.Logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.Global.LoggerName[self.Global.DBLoggerNameKey]['LogFile'],
                self.Global.LoggerName[self.Global.DBLoggerNameKey]['Name']
                )
        
        #self.db has already been initialized in super Infra class
        #self.db, self.dbCursor = self.getNewConnection()

        self.DBlogger.info('instantiating DB, current os pid [{pid}'.format(pid=os.getpid()))
        self.DBlogger.info('current os is [{os}]'.format(os=os.uname()))
        self.DBlogger.info('DB configuration .... \n')
        self.DBlogger.info('Config Data ---> {data}'.format(data=self.dbConfigData))

        self.DBlogger.debug('this is test from Sched Infrastructure')

if __name__ == "__main__":
    infra = Infra()
