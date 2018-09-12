import os, platform, json, sys
from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utility import Utility
"""
1. Check all the libraries needed
2. Check all the environment needed
3. Check all the config file needed
"""


class Environment(object, metaclass=Singleton):

    def __init__(self):

        self.Global = Global()
        self.util = Utility()

        if not self.util.isEnvSet('ENVIRONMENT'):
            raise ValueError('ENVIORNMENT key is not set')

        if not self.util.isEnvSet('ENVIRONMENT'):
            print('environment is not set, exiting !!!')
            sys.exit(-1)

        self.environment = self.util.getEnv('ENVIRONMENT')

        print('setting environment >> {env}'.format(env=self.environment))
        # need to set environments specific variables dev, test and production
        self.lPad = 50
        self.rPad = 1
        self.__initFile = self.Global.InitFile
        self.__initKeys = self.Global.InitKeys
        self.__bootStrapKey = self.Global.BootStrapKey
        self.__bootStrapFileKey = self.Global.BootStrapFileKey
        self.__logLocKey = self.Global.LogLocKey
        self.__envDetails={}
        self.invalidAppDir = list()
        self.invalidAppFile = list()


        if not self.util.isEnvSet('PYTHONPATH'):
            print('missing PYTHONPATH environment variable, terminating !!!')
            sys.exit(-1)
        else:
            self.__envDetails.update({'PYTHONPATH'  : self.util.getEnv('PYTHONPATH')})
        #fi

        print('Current OS : [{os}]'.format(os=self.util.getUname()))
        print ("Initializing ...")

        # searching init file
        # 1. search in current directory, 2. search in pythonpath, 3. search in APP_CONFIG dir

        print('searching init file')
        # searching file in current dir
        if not self.util.isFileExist(self.__initFile):
            # searching file in PYTHONPATH
            if not(self.util.isFileExist(self.util.buildFileWPath(self.__envDetails['PYTHONPATH'],self.__initFile))):
                if self.util.isEnvSet('APP_CONFIG'):
                    # searching file in APP_CONFIG dir
                    if not(self.util.isFileExist(self.util.buildFileWPath(self.util.getEnv('APP_CONFIG'),self.__initFile))):
                        print("Bootstrap error; missing init.json, terminating !!!")
                        sys.exit(-1)
                    else:
                        self.__initFile = self.util.buildFileWPath(self.util.getEnv('APP_CONFIG'),self.__initFile)
                        print('init file [{file}] found'.format(file=self.__initFile))
                else:
                    print("Bootstrap error; Exhasuted searching couldn\'t find init file, terminating !!!")
                    sys.exit(-1)
            else:
                self.__initFile = self.util.buildFileWPath(self.__envDetails['PYTHONPATH'],self.__initFile)
                print('init file [{file}] found'.format(file=self.__initFile))

        # Loading init file
        self.__initData = json.load(open(self.__initFile))
        if not self.__initData:
            print('Bootstra error, could not load init file >>> {file}'.format(file = self.__initFile))
            sys.exit(-1)

        # ensure all required key found in int file
        if not all (key in self.__initData.keys() for key in self.__initKeys):
            print("Missing required keys in init file, terminating !!!")
            sys.exit(-1)

        # Set all environment variable if not set
        if not all (self.util.isEnvSet(env) for env in self.__envDetails.keys()):
            print("app environment key is not set, building ...")
            #print("Setting environment...........................".ljust(self.lPad),end='')
            # app home
            self.setInitEnv()

        # validating required app directories/files >>> allAppDir = [dir[key] for index, key in enumerate(self.__initData)]
        #print(self.__initData)
        self.validateAppDir(self.__initData['VALIDATE_DIR_LIST'])
        self.validateAppFile(self.__initData['VALIDATE_FILE_LIST'])
        self.validateLogDir(self.__initData['APP_LOG']) # validating app log, create if we are missing

        self.appCfgLoc = self.__initData['APP_CONFIG']
        self.appLogLoc = self.__initData['APP_LOG']

    def setInitEnv(self):
        # set all missing env key
        for envKey in self.__envDetails:
            if not self.util.isEnvSet(envKey):
                self.util.setEnv(envKey,self.__envDetails[envKey])
            #fi
        #end for

    def validateAppDir(self, dirList):
        '''
        Description: Validate all system dir stored in init.json, if dir name not found will exit
        '''

        isMissing = False
        missingAppDir = list()
        for dirKeyVal in (dirList):
            # we are expecting dict stored in list, will check the 1st key from dict to get the dir key name 
            if not self.util.isDirExist(dirKeyVal[next(iter(dirKeyVal))]):
                missingAppDir.append(dirKeyVal)
                if not isMissing: isMissing = True 

        if isMissing:
            print('system dir is missing >>> {missing}'.format(missing = str(missingAppDir)))
            sys.exit(-1)

    def validateAppFile(self, fileList):
        '''
        Description: Validate all system file stored in init.json, if file name not found will exit
        '''

        isMissing = False
        missingAppFile = list()        
        for fileKeyVal in fileList:
            # we are expecting dict stored in list, will check the 1st key from dict to get the dir key name
            #print(fileKeyVal)
            if not self.util.isFileExist(fileKeyVal[next(iter(fileKeyVal))]):
                missingAppFile.append(fileKeyVal)
                if not isMissing: isMissing = True 

        if isMissing:
            print('system file(s) is missing >>> {missing}'.format(missing = str(missingAppFile)))
            sys.exit(-1)

    def validateLogDir(self, logDir):
        #if not os.path.isdir(os.environ[self.__logLocKey]):
        if not self.util.isDirExist(logDir):
            print('creating app log dir >>> {log}'.format(log = logDir))
            self.util.makeDir(self.util.getEnv(self.logDir))

    '''
    def getEnv(self,argEnvName):
        return os.getenv(argEnvName)

    def setEnv(self,argEnvName, argEnvVal):
        try:
            os.environ[argEnvName] = argEnvVal
        except Exception as err:
            sys.exit(-1)
    def isEnvSet(self,argEnvName):
        if self.util.getEnv(argEnvName):
            return True
        else:
            return False
        #fi
    '''

    #def getConfigLocation(self):
    #    #print(os.getenv(''.join([self.util.getEnv('APP_NAME'),'_CONFIG'])))
    #    return self.util.getEnv('APP_CONFIG')

    #def getLogLocation(self):
    #    return self.util.getEnv(self.Global.LogLocKey)

    #end getLogLocation
    '''
    def isFileExists(self,  argFileName):
        return os.path.isfile(argFileName)
    
    def isDirExists(self,  argDirName):
        return os.path.isdir(argDirName)
    def getOsInfo(self):
        return os.uname()[:]
    '''

if __name__ == "__main__":
    #settings = Settings()
    #settings.isModuleInstalled('temp')
    #print(settings.isFileExists('/tmp/a.log'))
    env = Environment('Dev')
