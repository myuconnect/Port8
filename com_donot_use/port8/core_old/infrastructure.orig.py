from com.port8.core.environment import Environment
from com.port8.core.singleton import Singleton

import traceback,sys,os,json, importlib, logging, logging.config

class Infra(object, metaclass=Singleton):

  def __init__(self):

    # setting the environment
    try:
      self.env = Environment()
      self.__appCfgKey= 'APP_CONFIG'
      self.configLoc = self.getConfigLocation()
      self.bootStrapFile = self.getBootStrapFile()
      self.dbConfigData = {}
      self.schedulerConfigData = {}
      self.restApiConfigData = {}
      self.agentConfigData = {}

      #print(self.env._Environment__initData)
      #print(self.env._Environment__envDetails)

      print("Validating bootstrap config....................".ljust(50),end='')
      self.validateBootStrapConfig()

      # ensuring all needed lib is available
      print("Checking all required libraries................".ljust(50),end='')
      self.validateAllLib()

      # ensure db is up and repository is abvailable
      print("Validating database............................".ljust(50),end='')      
      self.validateDb()

      # vaidating scheduler config
      print("Validating scheduler config file...............".ljust(50),end='')      
      self.validaterScheduleCfgFile()

      print("[OK - OS pid {pid}]".format(pid=os.getpid()))

      #self.myModuleLogger.info ('Infrastructure started with os pid [{pid}]'.format(pid=os.getpid()))

    except Exception as err:
      
      exc_type, exc_value, exc_traceback = sys.exc_info()
      myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

      print ('Error [{error}], terminating !!!'.format(error=myErrorMessage))
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
    return os.getenv(self.env._Environment__bootStrapFileKey)
    #mybootStrapFile = os.getenv[self.env._Environment__bootStrapKey]

  def getConfigLocation(self):
    #print(os.getenv(''.join([os.environ['APP_NAME'],'_CONFIG'])))
    return os.getenv(''.join([os.environ['APP_NAME'],'_CONFIG']))
  #end 

  def getLoggingConfigFile(self):
    return os.path.join(self.configLoc, self.__bootStrapData['LoggingCfg'])
  # end getLoggingConfigFile

  def getAppName(self):
    return os.environ['APP_NAME']

  def validateBootStrapConfig(self):

      # read bootstrap cnfig file
      #print(self.bootStrapFile)
      try:
        self.__bootStrapData = json.load(open(self.bootStrapFile))
        print("[OK]")
        if not self.__bootStrapData:
          print("Empty bootstrap data, terminating !!!")
          sys.exit(-1) 

      except Exception as err:
        print("Error [{err}] loading bootstrap config data".format(err=err.message))
        sys.exit(-1)
        
  #end validateBootStrapConfig

  def isModuleInstalled(self,  argLib):

    # returns existence of a library passed as an argument

    try:
      __import__('imp').find_module(argLib)
      return True
    except ImportError:
      #print('Missing library {lib}'.format(lib=argLib))
      return False

  #end isModuleInstalled

  def validateAllLib(self):
    
    # Ensuring all required library as specified in bootStrap.json is installed
    try:

      for lib in self.__bootStrapData['Libraries']:
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

  def validateMySqlDB(self):

    mySqlLib = importlib.import_module('pymysql')

    # validate the db config file
    try:

      self.dbConfigFile = self.__bootStrapData['DBConfigFile']
      self.dbConfigFileWPath = os.path.join(self.getConfigLocation(), self.dbConfigFile) 

      if not self.env.isFileExists(self.dbConfigFileWPath):
        print ("missing config file {cfgFile}, terminating !!!".format(cfgFile=self.dbConfigFileWPath))
        sys.exit(-1)
      # fi  

      self.dbConfigData = json.load(open(self.dbConfigFileWPath))
  
      # checking if loading the file was successful
      if not self.dbConfigData:
        print ("[Empty db config file]")
        sys.exit(-1)
      #fi

      # constructing config data
      myDbConfig = \
        {
          'user': self.dbConfigData[self.__bootStrapData['RepositoryDb']]['DbUser'],
          'password': self.dbConfigData[self.__bootStrapData['RepositoryDb']]['DbPasswd'],
          'host': self.dbConfigData[self.__bootStrapData['RepositoryDb']]['DbHost'],
          'db':self.dbConfigData[self.__bootStrapData['RepositoryDb']]['DbName'],
        }

      mySqlConnection = mySqlLib.connect(**myDbConfig)
      # connection is successful

      print('[OK]')    

    except Exception as err:
      exc_type, exc_value, exc_traceback = sys.exc_info()
      myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

      print('[Failed {err}]'.format(err=myErrorMessage))      
      sys.exit(-1)
  
  # end validateMySqlDB

  def validateDb(self):
    if self.__bootStrapData['RepositoryDb'] == "MySql" :
      self.validateMySqlDB()
  
  #end validateDb

  def validaterScheduleCfgFile(self):
    
    # validating schduler config file
    try:

      self.schdulerConfigFile = self.__bootStrapData['SchedulerCfg']
      self.schdulerConfigFileWPath = os.path.join(self.getConfigLocation(), self.schdulerConfigFile) 

      if not self.env.isFileExists(self.schdulerConfigFileWPath):
        print ("missing config file {cfgFile}, terminating !!!".format(cfgFile=self.schdulerConfigFileWPath))
        sys.exit(-1)
      # fi  

      self.schedulerConfigData = json.load(open(self.schdulerConfigFileWPath))
      if not self.schedulerConfigData: 
        print('[Empty Scheduler config file]')
      #fi
      print('[OK]')
    except Exception as err:

      exc_type, exc_value, exc_traceback = sys.exc_info()
      myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

      print('[Failed {err}]'.format(err=myErrorMessage))      
      sys.exit(-1)
  
  def buildLoggingInfra(self, argLogCfgFile):

    # Logging utility, constructing dictionary object to be used by native logging module

    #print ("Constructing logging foundation")
    try:
      myLogPath = os.environ['LOG_LOC']
      myAbsLogFile = os.path.basename(self.__bootStrapData['LogFile'])
      myLogFileWPath = os.path.join(myLogPath, myAbsLogFile)

      # check if logging config file is available
      if not self.env.isFileExists(argLogCfgFile):
        print("could not locate Logging Config file {cfgFile}, terminating !!!".format(cfgFile=argLogCdfgFile))
        sys.exit(-1)
      #fi

      # reading current config file
      myLoggingConfig = json.load(open(argLogCdfgFile))

      # Loading current configuration to logger's config file
      logging.config.dictConfig(myLoggingConfig)
      #print(myLoggingConfig)
      #myLogger = logging.getLogger('Port8')

    except Exception as err:
      print ("\n")
      print ("Error builidng logging infra using file {cfgFile}, terminating !!!".format(cfgFile=argLogCfgFile))
      sys.exit(-1)
    '''

    Follwoing format can be used in logging.config

       %(name)s            Name of the logger (logging channel)
       %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                           WARNING, ERROR, CRITICAL)
       %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                           "WARNING", "ERROR", "CRITICAL")
       %(pathname)s        Full pathname of the source file where the logging
                           call was issued (if available)
       %(filename)s        Filename portion of pathname
       %(module)s          Module (name portion of filename)
       %(lineno)d          Source line number where the logging call was issued
                           (if available)
       %(funcName)s        Function name
       %(created)f         Time when the LogRecord was created (time.time()
                           return value)
       %(asctime)s         Textual time when the LogRecord was created
       %(msecs)d           Millisecond portion of the creation time
       %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                           relative to the time the logging module was loaded
                           (typically at application startup time)
       %(thread)d          Thread ID (if available)
       %(threadName)s      Thread name (if available)
       %(process)d         Process ID (if available)
       %(message)s         The result of record.getMessage(), computed just as
                           the record is emitted
    '''
  #end buildLoggingInfra

class RestInfra(Infra, metaclass=Singleton):
  def __init__(self):
    self.buildLoggingInfra()

class SchedInfra(Infra, metaclass=Singleton):
  def __init__(self):
    pass

if __name__ == "__main__":
  infra = Infra()
  #print(dir())