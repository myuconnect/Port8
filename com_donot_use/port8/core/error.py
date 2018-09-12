import sys, traceback
from com.port8.core.singleton import Singleton

class ErrorUtil(object):
    def __init__(self, logger):
        if logger:
            self.logger = logger
    def  lognExtractError():
        if self.logger:
            myErrorMessage, myTraceBack = sys.exc_info()[1:],traceback.format_exc(limit=2)            
            self.logger.error(myErrorMessage)

class Error(Exception, metaclass=Singleton):

    def __init__(self,errorMsgArg = None, loggerArg = None):
        #print('in Error start')
        self.errorMsg = 'Error > {msg} '.format(msg=errorMsgArg) 
        #print(self.errorMsg)
        #print('in Error end')
        #self.logger = loggerArg

        #if self.logger:
        #    self.logger.error(self.errorMsg)
        #else:
        #print(self.errorMsg)
            
        # we need to initialize the response template and assign it as unsuccess, pass it back where error occurred
        #logger.error(self.errorMsg)

    def __str__(self):
        return repr(self.errorMsg)
        #return repr(exc_value)


class InvalidArguments(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.errors = message

class MissingFile(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class MissingLibrarries(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class InvalidContainer(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class InvalidTemplate(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class UndefinedInfra(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class InfraInitializationError(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class InfraInitializationError(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class ArgValidationError(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class UndefinedMethod(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class ValidationError(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class callDynaFuncError(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class processJobError(Error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

# we need to clean this up