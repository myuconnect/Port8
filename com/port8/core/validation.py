import os,json,sys, logging, time, datetime, random

from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utils import Utility
from jsonschema import validate
from com.port8.core.error import *

class Validation(object, metaclass=Singleton):

    def __init__(self):
        self.Global = Global()
        self.Utility = Utility()

    def validateArguments(self, userSchemaArg, appSchemaArg, ignoreArgs = None):
        '''
        Description:
            Validates user supplied argumenrts data in json format, returns True if valid data else raise error
        Usage:
            validateArguments(<userArgumentJsonData>, <jsonSchema>, <ignoreKeys not be validated>)
            E.g.: validateArguments(userArgData, jsonSchema, ignoreKeys)
        '''
        try:
            #print(userSchemaArg, appSchemaArg)
            myUserSchemaArg = self.Utility.getACopy(userSchemaArg)
            myAppSchemaArg = self.Utility.getACopy(appSchemaArg)

            #print('user schema',myUserSchemaArg.keys())
            #print('app schema',myAppSchemaArg.keys(), myAppSchemaArg['required'], myAppSchemaArg['properties'].keys())
            #print('app schema',myAppSchemaArg.keys())
            #print('ignore',ignoreArgs)

            # remove ignored key frm App/User schema
            if ignoreArgs:
                self.removeKeysFromAppSchema(myAppSchemaArg, ignoreArgs)
                self.removeKeysFromUserSchema(myUserSchemaArg, ignoreArgs)

            #self.validateSchema(myUserSchemaArg, myAppSchemaArg, exception)
            #print('user schema',myUserSchemaArg)
            #print('app schema',myAppSchemaArg)

            validate(myUserSchemaArg, myAppSchemaArg)
            return True

        except Exception as err:
            #myErrorMessage = sys.exc_info()[1:] # we need to substracte exact error during schema validation
            myErrorMessage = err
            #print('validation error', myErrorMessage)
            raise InvalidArguments(myErrorMessage)

    def validateSchema(self, userSchemaArg, appSchemaArg, exception):
        '''
        Validates user json data against json schema, returns True if valid date else return error message
        '''
        try:
            #print(userSchemaArg, appSchemaArg)
            validate(self.Utility.getACopy(userSchemaArg), self.Utility.getACopy(appSchemaArg))
            return True
        except Exception as err:
            #myErrorMessage = sys.exc_info()[1:] # we need to substracte exact error during schema validation
            myErrorMessage = err.message
            #print('validation error', myErrorMessage)
            raise exception(myErrorMessage)

    def validateSchedulerInitArg(self, schedulerTypeArg, schedulerModeArg, exception):
        '''
        validating scheduler argument (schedulerMode, schedulerType) passed for initialization
        '''

        if schedulerTypeArg not in self.Global.Schedulers:
            raise exception('Scheduler must be either one of the value in this list',self.Global.Schedulers)

        if schedulerModeArg not in self.Global.SchedulerMode:
            raise exception('Mode must be either of {mode}'.format(mode=self.Global.SchedulerMode))

    def removeKeysFromAppSchema(self, appSchemaArg, removeKeysArg):
        # remove key "Properties", "required" and substract from "MinProperties" from App schema
        for key in removeKeysArg:

            # removing key from properties
            if key in appSchemaArg['properties']:
                del appSchemaArg['properties'][key]

            # removing key from "required" list and substracting "minProperties count by 1"
            if key in appSchemaArg['required']:
                appSchemaArg['required'].remove(key)
                appSchemaArg['minProperties'] = appSchemaArg['minProperties'] - 1
                


    def removeKeysFromUserSchema(self, userSchemaarg, removeKeysarg):
        # remove key from User schema
        for key in removeKeysarg:
            if key in userSchemaarg: 
                del userSchemaarg[key]
