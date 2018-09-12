import os,json,sys, logging, time, datetime, random

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler import events
from jsonschema import validate

from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utils import Utility
from com.port8.core.infrautils import InfraUtility
from com.port8.db.dbmysql import DBMySql
from com.port8.core.validation import Validation
from com.port8.core.error import *
from com.port8.core.schedutility import SchedUtility

class BaseCls(object, metaclass = Singleton):

    def __init__(self, infraTypeArg):

        self.Global = Global()
        self.Utility = Utility()
        self.InfraUtil = InfraUtility()
        self.Validation = Validation()
        self.shcedUtil = SchedUtility()

        if not self.InfraUtil.isValidInfra(infraTypeArg):
            raise UndefinedInfra('Infra {infra} is undefined, terminating  '.format(infra=infraTypeArg))
        #fi
        self.Infra = self.InfraUtil.setInfra(infraTypeArg)

        self.db = DBMySql(infraTypeArg)
        self.logger = self.Infra.logger
