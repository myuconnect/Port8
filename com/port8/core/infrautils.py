from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utils import Utility
from com.port8.core.infrastructure import Infra
from com.port8.core.validation import Validation
from com.port8.core.error import *

import os,sys,importlib



# Python 3:
#Removed dict.iteritems(), dict.iterkeys(), and dict.itervalues().
#Instead: use dict.items(), dict.keys(), and dict.values() respectively.@Singleton

class InfraUtility(object, metaclass=Singleton):

    def __init__(self):
        
        self.Global = Global()
        self.Utility = Utility()
        self.Infra = Infra()
        self.Validation = Validation()

        self.myClass = self.__class__.__name__
        self.mySourceFile = os.path.basename(__file__)
        self.initClassArguments = ['moduleArg','classArg']

        # loading json schema for validation 
        self.sched_dyna_schema = self.Infra.jsonSchema['Main']['sched_dyna_call']
        #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

        #self.logger = self.Infra.logger

    def setInfra(self, infraArg):

        if infraArg and infraArg in self.Global.Infrastructure.keys():
            return self.__initClass(module = self.Global.InfraLib, cls = self.Global.Infrastructure[infraArg])
        else:
            print('Invald Infra')
            return None

    def isValidInfra(self, infraArg):
        '''
        Description: Checks if valid infrastructure is passed, returns True/False
        '''
        return infraArg in self.Global.Infrastructure.keys()

    def isValidModule(self, argModule):
        '''
        Checks whether module is a valid module
        '''
        if importlib.util.find_spec(argModule):
            return True
        else:
            return False
        #fi

    def isValidClass(self, argModuleHandler, argClass):
        return hasattr(argModuleHandler, argClass)

    def isValidMethod(self, argModuleHandler, argClass, argMethod):
        return hasattr(argModuleHandler, argClass)

    def importModule(self, argModule):

        if self.isValidModule(argModule):
            return importlib.import_module(argModule)
        #fi
    
    def __initClass(self, **keyWordArgs):
        '''
        Description: Import the module and instantiate the class with argument (tuple) passed, return the class handler to caller
            Arguments:
                module: this is module from which class need to be imported
                cls:  Class need to be imported and initialized
                clsArg: Argument need to be passed to class for initialization, this is tuple 

        Usage: initClass(module=<module>, cls=<cls> clsArg<initTple>)
        Example: initClass('com.port8.core.environment', 'Environment', ['Arg1','Arg2'])
        Return: retruns handler of class being initialized (would not use response, since this will be always an internal call)
        '''

        try:
            # initializing          
            myKeyWordArgs = self.Utility.getACopy(keyWordArgs)

            # validating argument received
            #self.Validation.validateArguments(myKeyWordArgs, self.dbSchema['dyna_call'] ) 
            #self.logger.debug('arguments {args} validated'.format(args = myKeyWordArgs ))

            # load the module as passed
            myImportedModule = importlib.import_module(myKeyWordArgs['module'])

            # import the class from module
            myCallableClass = getattr(myImportedModule, myKeyWordArgs['cls'])

            # initialize the class with cls arguments (clsArg) passed (will convert the arg to tuple)
            if 'clsArg' in myKeyWordArgs:

                # would not convert to tuple if only one argument is passed for class initialization
                if len(myKeyWordArgs['clsArg']) > 1:
                    return myCallableClass(tuple(myKeyWordArgs['clsArg']))
                elif len(myKeyWordArgs['clsArg']) == 1:
                    return myCallableClass(''.join(myKeyWordArgs['clsArg']))
            else:
                return myCallableClass()

        except Exception as err:
            raise

    def callFunc(self, **keyWordArgs):
        '''
        Description:
            will call method of a class from a module
        '''
        try:

            # initializing
            
            myResponse = self.Utility.getResponseTemplate()
            myKeyWordArgs = self.Utility.getACopy(keyWordArgs)
            #self.logger.debug('arg [{arg}] received'.format(arg=myKeyWordArgs))
            #print('arg [{arg}] received'.format(arg=myKeyWordArgs))

            # validating argument received
            self.Validation.validateArguments(myKeyWordArgs, self.sched_dyna_schema ) 

            myCallableClass = self.__initClass(**myKeyWordArgs)

            myResult = self.__callFunc(myCallableClass, myKeyWordArgs['method'], myKeyWordArgs['methodArgType'], myKeyWordArgs['arguments'])

            self.Utility.buildResponse(myResponse, self.Global.Success, self.Global.Success, myResult)
            return myResponse

        except Exception as err:
            myErrorMsg = sys.exc_info()[1:],traceback.format_exc(limit=1)
            self.Utility.buildResponse(myResponse, self.Global.UnSuccess,myErrorMsg[0])
            #self.logger.error('Error occurred during dyna call of func >> {error}'.format(error=myErrorMsg))
            return myResponse

    def __callFunc(self, callableClassArg, methodArg, methodArgType, arguments = None):

        
        try:
            myCallableMethod = getattr(callableClassArg, methodArg)
            
            if methodArgType == 'keyword':
                if arguments:
                    #print('keyword arg with argument')
                    myResult = myCallableMethod(**arguments)
                else:
                    #print('keyword arg without argument')
                    myResult = myCallableMethod()                    
            elif methodArgType == 'argument' :
                if arguments:
                    #print('argument without argument')                    
                    myResult = myCallableMethod(arguments)
                else:
                    #print('argument arg without argument')
                    myResult = myCallableMethod()

            #print(myResult)
            return myResult

        except Exception as err:
            myErrorMsg = sys.exc_info()[1:],traceback.format_exc(limit=1)
            #self.logger.error('Error occurred during (internal) __dyna call of func >> {error}'.format(error=myErrorMsg))
            raise callDynaFuncError(myErrorMsg[0])
