from com.port8.core.environment import Environment
from com.port8.core.singleton import Singleton

import traceback,sys,os,json, logging, logging.config

@Singleton
class Infrastructure(object):

  def __init__(self):

    # setting the environment
    try:
      self.env = Environment.Instance()
      self.__appCfgKey= 'APP_CONFIG'
      self.configLoc = self.getConfigLocation()

      #print(self.env._Environment__initData)
      #print(self.env._Environment__envDetails)

      print("Starting infrastructure...........................".ljust(50),end='')

      # read bootstrap cnfig file
      self.bootStrapFile = self.getBootStrapFile()
      #print(self.bootStrapFile)
      try:
        self.__bootStrapData = json.load(open(self.bootStrapFile))

        if not self.__bootStrapData:
          print("Empty bootstrap data, terminating !!!")
          sys.exit(-1) 

      except Exception as err:
        print("Error [{err}] loading bootstrap config data".format(err=err.message))

      # configuring logging

      myLogFile = self.buildLoggingInfra()
      print(myLogFile)

      myLogger = logging.getLogger('Port8')
      print(dir(myLogger))
      self.myModuleLogger = logging.getLogger(__name__ + '.' + self.__class__.__name__)
      print(dir(self.myModuleLogger))
      self.myModuleLogger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
      self.myModuleLogger.info('Startig up {app} infrastructure .....'.format(app=self.getAppName()))
      self.myModuleLogger.info('Initializing ....')

      # configuring schedule

      # ensuring all needed lib is available
      self.myModuleLogger.info('Validating all required libraries')
      self.validateAllLib()

      # ensure db is up and repository is abvailable
      self.validateDb()

      print("[OK - OS pid {pid}]".format(pid=os.getpid()))

      print("logFile...........................".ljust(50) + "[{logfile}]".format(logfile=myLogFile))

      self.myModuleLogger.info ('Infrastructure started with os pid [{pid}]'.format(pid=os.getpid()))

    except Exception as err:
      
      exc_type, exc_value, exc_traceback = sys.exc_info()
      myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

      if self.isValidLogger():
        self.myModuleLogger.info('An error {error} occurred, terminating'.format(error=myErrorMessage))

      print ('Error [{error}], terminating !!!'.format(error=myErrorMessage))
      sys.exit(-1)

  def getAppName(self):
    return os.environ['APP_NAME']

  def validateDb(self):
    pass

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

  def validateAllLib(self):
    for lib in self.__bootStrapData['Libraries']:
      if not self.isModuleInstalled(lib):
        self.myModuleLogger.error('Lib {frmtLib} is not installed, Pls install it using <pip install {frmtLib}>'.format(frmtLib=lib))
        print("[missing library {frmtLib}]".format(frmtLib=lib))
        sys.exit(-1)

  def isModuleInstalled(self,  argLib):
    try:
      __import__('imp').find_module(argLib)
      return True
    except ImportError:
      #print('Missing library {lib}'.format(lib=argLib))
      return False

  def getBootStrapFile(self):
    #print(self.env._Environment__bootStrapFileKey)
    return os.getenv(self.env._Environment__bootStrapFileKey)
    #mybootStrapFile = os.getenv[self.env._Environment__bootStrapKey]

  def getConfigLocation(self):
    return os.getenv(''.join([os.environ['APP_NAME'],'_CONFIG']))

  def getLoggingConfigFile(self):
    return os.path.join(self.configLoc, self.__bootStrapData['LoggingCfg'])

  def buildLoggingInfra(self):

    # Logging utility, constructing dictionary object to be used by native logging module

    #print ("Constructing logging foundation")
    try:
      myLoggingCfgFileWPath = self.getLoggingConfigFile()
      myLogPath = os.environ['LOG_LOC']
      myAbsLogFile = os.path.basename(self.__bootStrapData['LogFile'])
      myLogFileWPath = os.path.join(myLogPath, myAbsLogFile)

      # check if logging config file is available
      if not self.env.isFileExists(myLoggingCfgFileWPath):
        print("could not locate Logging Config file, terminating !!!")
        sys.exit(-1)

      # reading current config file
      myLoggingConfig = json.load(open(myLoggingCfgFileWPath))
      myLoggingConfig['handlers']['file']['filename'] = myLogFileWPath

      # Loading current configuration to logger's config file
      logging.config.dictConfig(myLoggingConfig)
      print(myLoggingConfig)
      myLogger = logging.getLogger('Port8')
      return myLogFileWPath

    except Exception as err:
      print ("\n")
      print ("Error builidn logging infra, terminating !!!")
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