from com.port8.core.environment import Environment
from com.port8.core.singleton import Singleton
from com.port8.core.loggingP8 import Logging
from com.port8.core.globals import Global
from com.port8.core.utility import Utility

from apscheduler.schedulers.background import BackgroundScheduler
from jsonref import JsonRef

import traceback,sys,os,json, importlib

class Infra(object, metaclass=Singleton):

    def __init__(self):

        # setting the Environment
        try:
            '''
            if not infraType or infraType not in ['REST','SCHEDULE','DAEMON']:
                print('expectig valid infra type REST/SCHEDULE/DAMEON got {got}, exiting !!!'.format(got = infraType))
                sys.exit(-1)
            '''
            self.env = Environment()
            self.globals = Global()
            self.util = Utility()
            self.logging = Logging()

            self.configLoc = self.env.appCfgLoc
            #print(self.configLoc)
            self.bootStrapFile = self.getBootStrapFile()
            if not self.bootStrapFile:
                raise ValueError('expecting valid bootstrap file, found NONE')

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

            '''
            self.Logger = \
                self.logging.buildLoggingInfra(\
                    self.loggingConfigData,\
                    self.globals.LoggerName[infraType]['LogFile'],
                    self.globals.LoggerName[infraType]['Name']
                    )
            '''
            #self.Logger.debug('this is test from Infrastructure')

            # ensure db is up and repository is abvailable
            #print("Validating database............................".ljust(50),end='')
            #self.__validateDb(infraType)
            #self.db = self.__getNewConnection()

            # loading DB schema
            # populating json schema for database
            '''
            commenting follwoing line, will revisit later to implement jsonref for db
            self.__loadDbJsonSchema()        
            '''
            #print("Loading logging config.........................".ljust(50),end='')
            #self.logger = Logging(self.loggingConfigData)
            #logger 
            print("[infra started with OS pid {pid}]".format(pid=self.getMyOsPid()))

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

            # validating if all modules config data is available
            myMissingModule = self.util.findMissingKeyInDict(self.__bootStrapData['Main']['Modules'], list(self.__bootStrapData['Main']['Modules'].keys()))
            if myMissingModule:
                print('Missing config information for module {0}'.format(myMissingModule))
                sys.exit(-1)

            #extracting module config information
            if self.env.environment not in self.__bootStrapData['Main']['Modules']['DB']['REPOSITORY']:
                print('[Error]\n     unable to find repository information for environment >> {env}'.format(env = self.env.environment))
                sys.exit(-1)

            if not self.env.environment in self.__bootStrapData['Main']['Modules']['DB']['REPOSITORY']:
                print('invalid environment >>> {env}'.format(env=self.env.Environment))
                sys.exit(-1)

            self.repConfigData = self.__bootStrapData['Main']['Modules']['DB']['REPOSITORY'][self.env.environment]
            self.dbConfigData = {
                'user' : self.repConfigData['User'], 
                'password' : self.repConfigData['enc'], 
                'host' : self.repConfigData['Host'], 
                'port' : self.repConfigData['Port'],
                'database' : self.repConfigData['Name']
            }
            self.schedulerConfigData = self.__bootStrapData['Main']['Modules']['Scheduler']
            self.loggingConfigData = self.__bootStrapData['Main']['Modules']['Logging']
            self.restApiConfigData = self.__bootStrapData['Main']['Modules']['RestAPI']
            self.daemonConfigData  = self.__bootStrapData['Main']['Modules']['Daemon']
            self.jsonSchemaConfigData  = self.__bootStrapData['Main']['Modules']['JsonSchema']

            if (not self.repConfigData):
                print('Repository DB Configuration is empty')
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
            #print("Error [{err}] loading bootstrap config data".format(err=err))
            sys.exit(-1)
    
    def __loadSchema(self):
        
        # load json schema data and resolve the reference if used, this will be needed to validate user data
        #print(self.configLoc)
        configFile = self.util.buildFileWPath(self.configLoc,self.jsonSchemaConfigData['ConfigFile'])
        if not self.util.isFileExist(configFile):
            print('Json Schema Configuration file {file} is missing !!!'.format(file=os.path.join(self.configLoc,self.jsonSchemaConfigData['ConfigFile'])))
            sys.exit(-1)
        
        #loading json schema file and resolving references if used in schema
        try:
            self.jsonSchema = JsonRef.replace_refs(json.load(open(configFile)))
            #print(self.jsonSchema)
        except Exception as err:
            myErrorMessage = sys.exc_info()[1:],traceback.format_exc(limit=2)            
            print (myErrorMessage)
            sys.exit(-1)

    def __validateAllLib(self):

        # Ensuring all required library as specified in bootStrap.json is installed
        try:
            for lib in self.__bootStrapData['Main']['libraries']:
                if not self.util.isPackageInstalled(lib):
                    #self.myModuleLogger.error('Lib {frmtLib} is not installed, Pls install it using <pip install {frmtLib}>'.format(frmtLib=lib))
                    print("[missing library {frmtLib}]".format(frmtLib=lib))
                    sys.exit(-1)

            print("[OK]")

        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

            print('[Failed {err}]'.format(err=myErrorMessage))      
            sys.exit(-1)

    def isValidBootStrapData(self):
        if self.__bootStrapData:
            return True
        else:
            return False

    def isValidLogger(self):
        if self.myModuleLogger:
            return True
        else:
            return False

    def getBootStrapFile(self):
        
        #print(self.env._Environment__bootStrapFileKey)
        #print (self.env._Environment__initData)
        return self.env._Environment__initData[self.env._Environment__bootStrapFileKey]
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

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                  method for DB
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    

    def __validateMySqlDB(self):

        self.dbLib = importlib.import_module('mysql.connector')

        # validate the db config file
        try:
            # connecting to database to ensure db is up
            db = self.dbLib.connect(host = self.dbConfigData['host'], port = self.dbConfigData['port'], user = self.dbConfigData['user'], password = self.util.decrypt(self.repConfigData['key'], self.dbConfigData['password']), database = self.dbConfigData['database'])

            # connection is successful, closing the connection
            db.close()
            # connection is successful
        except self.dbLib.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("something is wrong with your user name or password, exiting !!!")
                sys.exit(-1)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist, exiting !!!")
                sys.exit(-1)
            else:
                print(err)
        '''
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

            print('[Failed {err}]'.format(err=myErrorMessage))      
            sys.exit(-1)
        '''

    def __validateDb(self,infraType):
        #print(self.repConfigData)
        if infraType == 'REST':
            if self.repConfigData['Vendor'] == "mysql" :
                self.__validateMySqlDB()
            else:
                print('unsuported database for repository')
                sys.exit(-1)
        else:
            pass
        print("[OK]")

    def __loadDbJsonSchema(self):
        #self.dbSchema = self.jsonSchema.get('Main').get('db_schema').get(self.__bootStrapData['Main']['Modules']['DB']['REPOSITORY'])
        
        self.dbSchema = self.jsonSchema.get('Main').get('db_schema').get(self.__bootStrapData['Main']['Modules']['DB']['REPOSITORY'][self.env.environment])

    def __getNewConnection(self):
        try:
            #print('db config',self.dbConfigData)
            db = self.dbLib.connect(host = self.dbConfigData['host'], port = self.dbConfigData['port'], user = self.dbConfigData['user'], password = self.util.decrypt(self.repConfigData['key'], self.dbConfigData['password']), database = self.dbConfigData['database'])
            #dbCursor = db.cursor(dictionary=True, buffered=True)
            #dbCursor = db.cursor(buffered=True)
            return db
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

        super().__init__()

        print("Validating database............................".ljust(50),end='')
        super()._Infra__validateDb(self.globals.RestInfra)
        #self.db = self._Infra__getNewConnection()
        self.Logger = \
            self.logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.globals.LoggerName[self.globals.RestInfra]['LogFile'],
                self.globals.LoggerName[self.globals.RestInfra]['Name']
                )
        self.Logger.debug('this is test from Rest Infrastructure')

class SchedInfra(Infra, metaclass=Singleton):
    def __init__(self):

        super(SchedInfra, self).__init__()

        self.Logger = \
            self.logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.globals.LoggerName[self.globals.SchedInfra]['LogFile'],
                self.globals.LoggerName[self.globals.SchedInfra]['Name']
                )

        self.Logger.info('instantiating scheduler, current os pid [{pid}'.format(pid=os.getpid()))
        self.Logger.info('current os is [{os}]'.format(os=os.uname()))
        self.Logger.info('Scheduler configuration .... \n')
        self.Logger.info('Config Data ---> {data}'.format(data=self.schedulerConfigData))

        self.Logger.debug('this is test from Sched Infrastructure')

        # populating json schema for scheduler
        self.scheduleSchema = self.jsonSchema.get('Main').get('schedule_schema')
        self.intervalSchema = self.jsonSchema.get('Main').get('interval_schema')
        self.cronSchema = self.jsonSchema.get('Main').get('cron_schema')
        self.processJobSchema = self.jsonSchema.get('Main').get('process_job_schema')

        # Load json schema
        self.db = self.getNewConnection()

class DaemonInfra(Infra, metaclass=Singleton):
    def __init__(self):

        #inheriting Super class variables
        super(DaemonInfra, self).__init__()

        # creating logger for RestApi infrastructure
        self.Logger = \
            self.logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.globals.LoggerName[self.globals.DaemonInfra]['LogFile'],
                self.globals.LoggerName[self.globals.DaemonInfra]['Name']
                )

        self.Logger.info('instantiating Daemon, current os pid [{pid}'.format(pid=os.getpid()))
        self.Logger.info('current os is [{os}]'.format(os=os.uname()))
        self.Logger.info('Daemon configuration .... \n')
        self.DaemonLogger.info('Config Data ---> {data}'.format(data=self.daemonConfigData))

        self.Logger.debug('this is test from Daemon Infrastructure')

class DBInfra(Infra, metaclass=Singleton):
    def __init__(self):

        super(DBInfra,self).__init__()

        self.Logger = \
            self.Logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.globals.LoggerName[self.globals.DBLoggerNameKey]['LogFile'],
                self.globals.LoggerName[self.globals.DBLoggerNameKey]['Name']
                )

        self.Logger.info('instantiating DB, current os pid [{pid}'.format(pid=os.getpid()))
        self.Logger.info('current os is [{os}]'.format(os=os.uname()))
        self.Logger.info('DB configuration .... \n')
        self.Logger.info('Config Data ---> {data}'.format(data=self.dbConfigData))

        self.Logger.debug('this is test from Sched Infrastructure')

if __name__ == "__main__":
    #infra = Infra()
    rest = RestInfra()
