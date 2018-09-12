import os, platform, json, sys
from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global

"""
1. Check all the libraries needed
2. Check all the environment needed
3. Check all the config file needed
"""


class Environment(object, metaclass=Singleton):

    def __init__(self):

        self.Global = Global()
        self.lPad = 50
        self.rPad = 1
        self.__initFile = self.Global.InitFile
        self.__initKeys = self.Global.InitKeys
        self.__bootStrapKey = self.Global.BootStrapKey
        self.__bootStrapFileKey = self.Global.BootStrapFileKey
        self.__logLocKey = self.Global.LogLocKey
        self.__envDetails={}


        if 'PYTHONPATH' not in os.environ:
            print('missing PYTHONPATH environment variable, terminating !!!')
            sys.exit(-1)
        else:
            self.__envDetails.update({'PYTHONPATH'  : os.environ['PYTHONPATH']})
        #fi

        print('Current OS : [{os}]'.format(os=self.getOsInfo()))
        print ("Initializing ...")

        # searching init file
        # 1. search in current directory, 2. search in pythonpath, 3. search in APP_CONFIG dir
        print('searching init file')
        if not self.isFileExists(self.__initFile):
            if not(self.isFileExists(os.path.join(self.__envDetails['PYTHONPATH'],self.__initFile))):
                if not(self.isFileExists(os.path.join(self.__envDetails['APP_CONFIG'],self.__initFile))):
                    print("Bootstrap error; missing init.json, terminating !!!")
                    sys.exit(-1)
                else:
                    self.__initFile = os.path.join(self.__envDetails['APP_CONFIG'],self.__initFile)
                    print('init file [{file}] found'.format(file=self.__initFile))
            else:
                self.__initFile = os.path.join(self.__envDetails['PYTHONPATH'],self.__initFile)
                print('init file [{file}] found'.format(file=self.__initFile))

        # Loading init file
        #print('bootstraping init file')
        self.__initData = json.load(open(self.__initFile))

        # ensure all required key found in int file
        if not all (key in self.__initData.keys() for key in self.__initKeys):
            print("Missing required keys in init file, terminating !!!")
            sys.exit(-1)
        #fi

        # building environment key details (APP_NAME, {APP}_HOME, {APP}_CONFIG)
        self.__envDetails.update({'APP_NAME'  : self.__initData['AppName']})        
        self.__envDetails.update({''.join([self.__initData['AppName'],'_HOME']) : self.__initData['AppHome']})
        if 'CONFIG_LOC' in self.__initData:
            self.__envDetails.update({''.join([self.__initData['AppName'],'_CONFIG']) : ''.join([self.__initData['AppHome'],'/config'])})

        self.__envDetails.update({''.join([self.__initData['AppName'],'_CONFIG']) : ''.join([self.__initData['AppHome'],'/config'])})
        self.__envDetails.update({'ENVIRONMENT' : self.__initData['Environment'].upper()})

        self.__envDetails.update({'APP_CONFIG_KEY': ''.join([self.__initData['AppName'],'_CONFIG'])})
        self.__envDetails.update({'APP_HOME_KEY': ''.join([self.__initData['AppName'],'_HOME'])})
        self.__envDetails.update({self.__logLocKey: self.__initData[self.__logLocKey]})

        # Set all environment variable if not set
        if not all (env in os.environ for env in self.__envDetails.keys()):
            print("app environment key is not set, building ...")
            #print("Setting environment...........................".ljust(self.lPad),end='')
            # app home
            self.setInitEnv()
        #fi

        #validating LOG file location
        self.validateLogDir()

        # Validating bootstrap
        try:
            # validating if bootstrap key/file exists
            if self.__bootStrapKey in self.__initData and \
                self.isFileExists( \
                    os.path.join( \
                     self.getEnv(''.join([self.__initData['AppName'],'_CONFIG'])), self.__initData[self.__bootStrapKey])):

                # will update the __envDetials and update the environment variable as well
                bootStrapFile = os.path.join( self.getEnv(''.join([self.__initData['AppName'],'_CONFIG'])), self.__initData[self.__bootStrapKey]) 

                self.__envDetails.update({self.__bootStrapFileKey:bootStrapFile})
                os.environ[self.__bootStrapFileKey] = self.__envDetails[self.__bootStrapFileKey]

                print("[OK]")
            else: 
                print("[unable to locate bootstrap file]")
                sys.exit(-1)

        except Exception as err:
            print("bootstrap error, terminating !!!")
            raise
            sys.exit(-1)


    def setInitEnv(self):
        # set all missing env key
        for envKey in self.__envDetails:
            if not self.isEnvSet(envKey):
                self.setEnv(envKey,self.__envDetails[envKey])
            #fi
        #end for

    def validateLogDir(self):
        if not os.path.isdir(os.environ[self.__logLocKey]):
            os.makedirs(os.environ[self.__logLocKey])

    def getEnv(self,argEnvName):
        return os.getenv(argEnvName)

    def setEnv(self,argEnvName, argEnvVal):
        try:
            os.environ[argEnvName] = argEnvVal
        except Exception as err:
            sys.exit(-1)

    def isEnvSet(self,argEnvName):
        if self.getEnv(argEnvName):
            return True
        else:
            return False
        #fi

    def getConfigLocation(self):
        #print(os.getenv(''.join([os.environ['APP_NAME'],'_CONFIG'])))
        return os.getenv(''.join([os.environ['APP_NAME'],'_CONFIG']))
    #end getConfigLocation

    def getLogLocation(self):
        return os.getenv(self.Global.LogLocKey)
    #end getLogLocation

    def isFileExists(self,  argFileName):
        return os.path.isfile(argFileName)
    
    def isDirExists(self,  argDirName):
        return os.path.isdir(argDirName)

    def getOsInfo(self):
        return os.uname()[:]


if __name__ == "__main__":
    settings = Settings()
    settings.isModuleInstalled('temp')
    print(settings.isFileExists('/tmp/a.log'))
