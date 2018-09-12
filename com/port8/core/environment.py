import os, platform, json, sys, getpass
from com.port8.core.singleton import Singleton

"""
1. Check all the libraries needed
2. Check all the environment needed
3. Check all the config file needed
"""


class Environment(object, metaclass=Singleton):

    def __init__(self):

        valDirList = []

        print('initializing ....')

        if not 'ENV' in os.environ:
            print('error: port8-env10001, mandatory environment is not set, exiting !!!')
            sys.exit(-1)

        # setting environment
        self.environment = os.getenv('ENV')

        print('setting environment >> {env}'.format(env=self.environment))
        # need to set environments specific variables dev, test and production
        self.lPad = 50
        self.rPad = 1
        self.__envDetails={}
        self.invalidAppDir = list()
        self.invalidAppFile = list()
        self.validationCode = ''
        allLib=['cx-Oracle','flask','flask-cors','mssql','mysql','postgress','pymongo']


        if not 'PYTHONPATH' in os.environ:
            print('error: port8-env10002, mandatory environment is not set, exiting !!!')
            sys.exit(-1)
        else:
            self.__envDetails.update({'PYTHONPATH'  : os.getenv('PYTHONPATH')})
            valDirList.append(self.__envDetails['PYTHONPATH'])

        os.environ['APP_NAME'] = "PORT8"

        self.__envDetails.update({'APP_NAME'  : os.getenv('APP_NAME')})

        if not 'APP_CONFIG' in os.environ:
            print('error: port8-env10003, mandatory environment is not set, exiting !!!')
            sys.exit(-1)
        else:
            self.__envDetails.update({'APP_CONFIG'  : os.getenv('APP_CONFIG')})
            valDirList.append(self.__envDetails['APP_CONFIG'])

        if not 'APP_LOG' in os.environ:
            print('error: port8-env10004, mandatory environment is not set, exiting !!!')
            sys.exit(-1)
        else:
            self.__envDetails.update({'APP_LOG'  : os.getenv('APP_LOG')})

        # validating code for non prod environment
        if self.environment not in ['PROD','DEV','TEST']:
            print('error: port8-env10005, invalid environment, exiting !!!') 

        self.validationCode = 'port8' # remove this from prod deployment
        
        if self.environment != "PROD" and self.validationCode != 'port8':
            while True:
                try:
                    self.validationCode = getpass.getpass("Pls enter validation code for environment : ")
                    if self.validationCode != "port8":
                        print ("Invalid validation code")
                        continue
                    else:
                        break
                except Exception as e:
                    raise e
        self.__envDetails.update({'ENV'  : os.getenv('APP_LOG')})

        print('Current OS : [{os}]'.format(os=platform.uname().system.upper()))

        print('validating system dir')
        self.validateAppDir(valDirList)
        self.validateLogDir(self.__envDetails['APP_LOG']) # validating app log, create if we are missing
        #self.validateAppFile(self.__initData['VALIDATE_FILE_LIST'])

        self.appCfgLoc = self.__envDetails['APP_CONFIG']
        self.appLogLoc = self.__envDetails['APP_LOG']


    def validateAppDir(self, dirList):
        '''
        Description: Checks if all dir in list exists
        '''
        
        #print(dirList)
        isMissing = False
        missingAppDir = list()
        
        for sysDir in (dirList):

            if not os.path.isdir(sysDir):
                missingAppDir.append(dirKeyVal)
                if not isMissing: 
                    isMissing = True 

        if isMissing:
            print('system dir is missing >>> {missing}'.format(missing = str(missingAppDir)))
            sys.exit(-1)

    def validateLogDir(self, logDir):
        if not os.path.isdir(logDir):
            print('creating app log dir >>> {log}'.format(log = logDir))
            os.mkdir(logDir)

#if __name__ == "__main__":
#    env = Environment()
