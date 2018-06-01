class Singleton(object):
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.
    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.
    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.
    """
    def __init__(self, decorated):
        self._decorated = decorated
    #def Instance(self):
        #myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Singleton')
        #myModuleLogger.debug("Initializing, current request for class {cls} to be singletong".format(cls=cls))
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
    #    try:
    #        return self._instance
    #    except AttributeError:
    #        self._instance = self._decorated()
    #        return self._instance
    def __call__(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance
    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

'''
class Singleton(object):
    _instances = { }

    def __new__(cls, *args, **kwargs):
        if cls._instances.get( cls, None ) is None:
            cls._instances[ cls ] = super(Singleton, cls).__new__(cls, *args, **kwargs)

        return Singleton._instances[ cls ]
'''