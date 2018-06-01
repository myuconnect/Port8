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

class error(Exception, metaclass=Singleton):

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


class InvalidArguments(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.errors = message

class MissingFile(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class MissingLibrarries(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class InvalidContainer(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class InvalidTemplate(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class UndefinedInfra(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class InfraInitializationError(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class InfraInitializationError(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class ArgValidationError(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class UndefinedMethod(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class ValidationError(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class callDynaFuncError(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

class processJobError(error, metaclass=Singleton):
    def __init__(self, message, logger = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message, logger)
        self.error = message

# we need to clean this up