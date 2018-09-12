from com.port8.core.environment import Environment
from com.port8.core.singleton import Singleton
#from com.port8.core.loggingP8 import Logging
from com.port8.core.globals import Global
from com.port8.core.utility import Utility

from apscheduler.schedulers.background import BackgroundScheduler
from jsonref import JsonRef

import traceback,sys,os,json, importlib,traceback,logging, logging.config

class Infra(object, metaclass=Singleton):

    def __init__(self):

        try:
            #print('initializing env 1')
            self.env = Environment()
            self.globals = Global()
            self.util = Utility()
            #self.logging = Logging()

            self.configLoc = self.env.appCfgLoc
            self.bootStrapFile = os.path.join(self.configLoc, self.globals.bootStrapFile)

            if not self.bootStrapFile:
                print('error: port8-infra10001, bootstrap error !!!')
                sys.exit(-1)

            self.dbConfigData = {}
            self.daemonConfifData = {}
            self.schedulerConfigData = {}
            self.restApiConfigData = {}
            self.agentConfigData = {}

            print("Loading bootstrap config....................".ljust(50),end='')
            self.__loadBootStrapConfig()
            #self.jsonSchema = JsonRef.replace_refs(self.__bootStrapData['Main'])
            #self.__loadSchema()
            #self.jsonSchemaConfigData

            # ensuring all needed lib is available
            print("Checking all required libraries................".ljust(50),end='')
            self.__validateAllLib()

            print("[infra started with OS pid {pid}]".format(pid=self.util.getMyOsPid()))

        except Exception as err:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

            print ('Error [{error}], terminating !!!'.format(error=myErrorMessage))
            sys.exit(-1)

    def __loadBootStrapConfig(self):
        '''
        Descrption: called internally, loads bootstrap config file in memory
        '''
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
            #print(self.env.environment, self.__bootStrapData['Main']['Modules']['DB']['REPOSITORY'])
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
            self.jsonSchemaConfigData  = self.__bootStrapData['Main']['JsonSchema']

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
        configFile = self.util.buildFileWPath(self.configLoc, self.jsonSchemaConfigData['ConfigFile'])
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
        
        self.dbSchema = self.jsonSchemaConfigData.get('Main').get('db_schema').get(self.__bootStrapData['Main']['Modules']['DB']['REPOSITORY'][self.env.environment])

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

    def __closeConnection(self, conn):
        if conn:
            conn.close()

    def isConnectionOpen(self, conn):
        try:
            dbCur = conn.cursor()
            dbCur.execute('select now()')
            return True
        except Exception as err:
            return False

class RestInfra(Infra, metaclass=Singleton):
    def __init__(self):
        # calling super (Infra) class init method
        #print('before calling infra init')
        super().__init__()

        print("Validating database............................".ljust(50),end='')
        super()._Infra__validateDb(self.globals.RestInfra)

        #self.db = self._Infra__getNewConnection()
        myLoggingConfig = self.util.getACopy(self.loggingConfigData)
        myLoggerInfo = self.globals.LoggerName[self.globals.RestInfra]

        if 'LogFile' in myLoggerInfo:
            logFileWPath = os.path.join(self.env.appLogLoc, myLoggerInfo['LogFile'])
            myLoggingConfig['handlers']['file']['filename'] = logFileWPath

        logging.config.dictConfig(myLoggingConfig)
        self.logger = logging.getLogger(myLoggerInfo['Name'])

        print("Loading factory method metadata................".ljust(50),end='')
        # need to load factory metadata somewhere else. this is callingg mysql and ,mysql is callin infra going in loop
        self.factoryMetadata = self.loadFactoryMetadata()
        print("[OK]")
        #print('Factory metadata ',self.factoryMetadata)
        self.logger.debug('this is test from Rest Infrastructure')
        print("\n")
        print("Infrastructure is ready ")

    def loadFactoryMetadata(self):
        #from com.port8.core.mysqlutils import MysqlUtil
        try:
            conn = super()._Infra__getNewConnection()
            dbCur = conn.cursor()
            dbResult = dbCur.execute(self.globals.buildFactoryDataSql)
            myAllColumns = dbCur.column_names
            myRawData = dbCur.fetchall()

            #building dict data
            myData = [dict(zip(myAllColumns, row)) for row in myRawData]
            dbCur.close()
            conn = super()._Infra__closeConnection(conn)
            #print('Factory metadata (raw)', myData)
            myFactoryData = list() 
            #print('myData count', len(myData))
            for pageAction in myData:
                #print('in loop')
                #checking if this page exists 
                pageIdx = [idx for idx, val in enumerate(myFactoryData) if myFactoryData[idx]['PAGE_ID'] == pageAction['PAGE_ID']]
                #print('pageIdx',pageIdx)
                if pageIdx: pageIdx = pageIdx[0]
                #print('index', pageIdx)
                if not pageIdx:
                    # page doesnt exist, adding new page and its 1st action
                    #print('page not found', pageAction['PAGE_ID'], myFactoryData)
                    myFactoryData.append(
                        {'PAGE_ID': pageAction['PAGE_ID'], 'PAGE_STATUS' : pageAction['PAGE_STATUS'],
                            "ACTIONS" : [
                                {'ACTION_ID' : pageAction['ACTION_ID'], 'ACTION_STATUS' : pageAction['ACTION_STATUS'],
                                'BPM_CALL_JSON': eval(pageAction['BPM_CALL_JSON']) }
                            ] 
                        }
                    )
                else:
                    # page exist, adding action
                    #print('page found',pageIdx, pageAction['PAGE_ID'], myFactoryData[pageIdx])
                    myFactoryData[pageIdx]["ACTIONS"].append(
                        {'ACTION_ID' : pageAction['ACTION_ID'], 
                         'ACTION_STATUS' : pageAction['ACTION_STATUS'],
                         'BPM_CALL_JSON': eval(pageAction['BPM_CALL_JSON']) 
                        }
                    )

            #print('Factory metadata', myFactoryData)
            return myFactoryData

        except Exception as err:
            raise err
        # we need to build factory metadata which will be used by factotu method to navigate method name

class SchedInfra(Infra, metaclass=Singleton):
    def __init__(self):

        super(SchedInfra, self).__init__()

        myLoggingConfig = self.util.getACopy(self.loggingConfigData)
        myLoggerInfo = self.globals.LoggerName[self.globals.SchedInfra]

        if 'LogFile' in myLoggerInfo:
            logFileWPath = os.path.join(self.env.appLogLoc, myLoggerInfo['LogFile'])
            myLoggingConfig['handlers']['file']['filename'] = logFileWPath

        logging.config.dictConfig(myLoggingConfig)
        self.logger = logging.getLogger(myLoggerInfo['Name'])

        '''
        self.Logger = \
            self.logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.globals.LoggerName[self.globals.SchedInfra]['LogFile'],
                self.globals.LoggerName[self.globals.SchedInfra]['Name']
                )
        '''
        self.logger.info('instantiating scheduler, current os pid [{pid}'.format(pid=os.getpid()))
        self.logger.info('current os is [{os}]'.format(os=os.uname()))
        self.logger.info('Scheduler configuration .... \n')
        self.logger.info('Config Data ---> {data}'.format(data=self.schedulerConfigData))

        self.logger.debug('this is test from Sched Infrastructure')

        # populating json schema for scheduler
        self.scheduleSchema = self.jsonSchemaConfigData.get('Main').get('schedule_schema')
        self.intervalSchema = self.jsonSchemaConfigData.get('Main').get('interval_schema')
        self.cronSchema = self.jsonSchemaConfigData.get('Main').get('cron_schema')
        self.processJobSchema = self.jsonSchemaConfigData.get('Main').get('process_job_schema')

        # Load json schema
        self.db = self.getNewConnection()

class DaemonInfra(Infra, metaclass=Singleton):
    def __init__(self):

        #inheriting Super class variables
        super(DaemonInfra, self).__init__()

        # creating logger for Daemon infrastructure
        myLoggingConfig = self.util.getACopy(self.loggingConfigData)
        myLoggerInfo = self.globals.LoggerName[self.globals.DaemonInfra]

        if 'LogFile' in myLoggerInfo:
            logFileWPath = os.path.join(self.env.appLogLoc, myLoggerInfo['LogFile'])
            myLoggingConfig['handlers']['file']['filename'] = logFileWPath

        logging.config.dictConfig(myLoggingConfig)
        self.logger = logging.getLogger(myLoggerInfo['Name'])
        '''
        self.Logger = \
            self.logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.globals.LoggerName[self.globals.DaemonInfra]['LogFile'],
                self.globals.LoggerName[self.globals.DaemonInfra]['Name']
                )
        '''
        self.logger.info('instantiating Daemon, current os pid [{pid}'.format(pid=os.getpid()))
        self.logger.info('current os is [{os}]'.format(os=os.uname()))
        self.logger.info('Daemon configuration .... \n')
        self.DaemonLogger.info('Config Data ---> {data}'.format(data=self.daemonConfigData))

        self.Logger.debug('this is test from Daemon Infrastructure')

class DBInfra(Infra, metaclass=Singleton):
    def __init__(self):

        super(DBInfra,self).__init__()

        myLoggingConfig = self.util.getACopy(self.loggingConfigData)
        myLoggerInfo = self.globals.LoggerName[self.globals.DaemonInfra]

        if 'LogFile' in myLoggerInfo:
            logFileWPath = os.path.join(self.env.appLogLoc, myLoggerInfo['LogFile'])
            myLoggingConfig['handlers']['file']['filename'] = logFileWPath

        logging.config.dictConfig(myLoggingConfig)
        self.logger = logging.getLogger(myLoggerInfo['Name'])
        '''
        self.Logger = \
            self.Logging.buildLoggingInfra(\
                self.loggingConfigData,\
                self.globals.LoggerName[self.globals.DBLoggerNameKey]['LogFile'],
                self.globals.LoggerName[self.globals.DBLoggerNameKey]['Name']
                )
        '''
        self.logger.info('instantiating DB, current os pid [{pid}'.format(pid=os.getpid()))
        self.logger.info('current os is [{os}]'.format(os=os.uname()))
        self.logger.info('DB configuration .... \n')
        self.logger.info('Config Data ---> {data}'.format(data=self.dbConfigData))

        self.logger.debug('this is test from Sched Infrastructure')

if __name__ == "__main__":
    #infra = Infra()
    rest = RestInfra()
