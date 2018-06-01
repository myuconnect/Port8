import os, sys, json
from singleton import Singleton

"""
1. Check all the libraries needed
2. Check all the environment needed
3. Check all the config file needed
"""


@Singleton
class Env(object):

    def __init__(self):

        self.lPad = 20
        self.rPad = 1
        self.__initFile="init.json"
        self.__initKeys=('AppName','AppHome','Environment')

        print ("Initializing ...")

        if not self.isFileExists(self.__initFile):
            print("Bootstrap error; missing init.json, terminating !!!")
            sys.exit(-1)
        #fi
        # read init.json
        self.__init = json.load(open(self.__initFile))

        # ensure all required key is availble
        if not all (key in self.__init.keys() for key in self.__initKeys):
            print("Missing required keys in init file, terminating !!!")
            sys.exit(-1)
        #fi

        # building environment key details
        self.__envDetails={}
        self.__envDetails.update({'APP_NAME'  : self.__init['AppName']})
        self.__envDetails.update({''.join([self.__init['AppName'],'_HOME']) : self.__init['AppHome']})
        self.__envDetails.update({''.join([self.__init['AppName'],'_CONFIG']) : ''.join([self.__init['AppHome'],'/config'])})
        self.__envDetails.update({'ENVIRONMENT' : self.__init['Environment'].upper()})
        if self.__envDetails['ENVIRONMENT'] == 'PROD':
            self.__envDetails.update({'PYTHONHOME' : ''.join([self.__init['AppHome'],'/config'])})
        else:
            self.__envDetails.update({'PYTHONHOME' : ''.join([self.__init['AppHome'],'/config'])})
        #print(self.__envDetails)

        # ensure all env is set
        if not all (env in os.environ for env in self.__envDetails.keys()):
            print("Setting environment ...")
            # app home
            self.setInitEnv()
        #fi


        print('OS  {os}'.format(os=self.getOsInfo()))
        print('Starting with os pid {pid}'.format(pid=os.getpid()))

    '''
    def validateEnv(self, argAppName, argAppHomePath, argEnv):
        # setting environment

        if (self.myAppNameEnv not in os.environ):
            self.myAppNameEnvVal = argAppName.upper()
            os.environ[self.myAppNameEnv] = self.myAppNameEnvVal            
        else:
            self.myAppNameEnvVal = os.getenv(self.myAppNameEnv)
        #fi
        print (self.myAppNameEnv.rjust( len(self.myAppNameEnv) + self.rPad).ljust(self.lPad) + " : [{app}] ".format(app=self.myAppNameEnvVal))
    
        self.myAppHomeEnv = ''.join([self.myAppNameEnvVal, "_HOME"]) 

        if (self.myAppHomeEnv not in os.environ):
            self.myAppHomeEnvVal = argAppHomePath
            os.environ[self.myAppHomeEnv] = self.myAppHomeEnvVal            
        else:
            self.myAppHomeEnvVal = os.getenv(self.myAppHomeEnv)
        #fi        
        
        print (self.myAppHomeEnv.rjust( len(self.myAppHomeEnv) + self.rPad).ljust(self.lPad) + " : [{homeVal}] ".format(homeVal=self.myAppHomeEnvVal))

        self.myAppHomeCfgEnv = ''.join([self.myAppNameEnvVal, '_CONFIG']) 

        if (self.myAppHomeCfgEnv not in os.environ):
            self.myAppHomeCfgEnvVal = ''.join([self.myAppHomeEnvVal, '/config'])
            os.environ[self.myAppHomeCfgEnv] = self.myAppHomeCfgEnvVal 
            #sys.exit(-1)
        else:
            self.myAppHomeCfgEnvVal = os.getenv(self.myAppHomeCfgEnv)
            #print ("  {cfg} [{cfgVal}] enviromenment found".format(cfg=self.myAppHomeCfgEnv, cfgVal=self.myAppHomeCfgEnvVal))
        #fi        

        print (self.myAppHomeCfgEnv.rjust( len(self.myAppHomeCfgEnv) + self.rPad).ljust(self.lPad) + " : [{cfgVal}] ".format(cfgVal=self.myAppHomeCfgEnvVal))

        # setting the pythonPath for this application
        #print('  Setting PYTHONPATH ....')
        if argEnv.upper() == 'PROD':
            self.pythonPathEnvval = ''.join([self.myAppHomeEnvVal,'/src'])
        else:
            self.pythonPathEnvval = ''.join([self.myAppHomeEnvVal,'/bin'])
        #fi
        os.environ["PYTHONPATH"] = self.pythonPathEnvval
        print('PYTHONPATH'.rjust( len('PYTHONPATH') + self.rPad).ljust(self.lPad) + ' : [{pythonPath}]'.format(pythonPath=self.pythonPathEnvval))
        '''
    def isModuleInstalled(self,  argLib):
        try:
            __import__('imp').find_module(argLib)
            return True
        except ImportError:
            #print('Missing library {lib}'.format(lib=argLib))
            return False

    # end isModuleInstalled
    
    def setInitEnv(self):
        # set all missing env key
        for envKey in self.__envDetails:
            if not self.isEnvSet(envKey):
                self.setEnv(envKey,self.__envDetails[envKey])
            #fi
        #end for

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

    def isFileExists(self,  argFileName):
        return os.path.isfile(argFileName)
    
    def checkLibraries(self):
        pass

    def checkEnvVar(self):
        pass

    def validate(self):
        pass
    
    def getAppName(self):
        if ('APP_NAME' not in os.getenviron):
            print('Environment variable APP_NAME is not set')
    
    def getOsInfo(self):
        return os.uname()[:]


if __name__ == "__main__":
    settings = Settings()
    settings.isModuleInstalled('temp')
    print(settings.isFileExists('/tmp/a.log'))
