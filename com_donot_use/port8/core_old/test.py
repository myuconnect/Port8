import time,os,json,sys, logging

from com.port8.core.infrastructure import DaemonInfra

class Test(object, metaclass=Singleton):
    def __init__(self):
        pass
        Infra = DaemonInfra()
    def performTest(self):
        Infra.logger(time.ctime())
