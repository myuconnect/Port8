import os,sys,traceback,datetime,copy,random, importlib,time
from jsonschema import *

from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global


# Python 3:
#Removed dict.iteritems(), dict.iterkeys(), and dict.itervalues().
#Instead: use dict.items(), dict.keys(), and dict.values() respectively.@Singleton

class Utility(object, metaclass=Singleton):

    def __init__(self):
        self.Global = Global()
        self.myClass = self.__class__.__name__
        self.myPythonFile = os.path.basename(__file__)

        #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

    def getErrorTraceback(self):
        return sys.exc_info()[1:],traceback.format_exc(limit=2)            

    def getCurrentTime(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    def isDict(self, argDict):
        try:
            if isinstance(argDict,dict): 
                return True
            else:
                return False
        except Exception as error:
            return False

    def joinListContents(self, listArg, listSep):
        return listSep.join(listArg)

    def isList(self, argValue):
        try:
            if isinstance(argValue,list): 
                return True
            else:
                return False
        except Exception as error:
            return False

    def removeEmptyValueKeyFromDict(self, argDict):
        # removes key if it has empty or 0 value
        myMainArgData = self.getCopy(argDict)
        return dict([(key,value) for key,value in myMainArgData.items() if (value)])

    def removeEmptyValueFromList(self, argList):
        # removes key if it has empty or 0 value
        myMainArgData = self.getCopy(argList)
        return list([(value) for value in myMainArgData if (value)])

    def convList2Dict(self, argValueList):
        ''' Duplicate value will be removed if found in list '''
        myDict = {}
        for myList in argValueList:
            myDict.update({myList['Key'] : myList['Value']})

        return myDict

    def findKeyInListDict(self, argList, argKey, argVal):
        return [i for i, x in enumerate(argList) if (argKey in x) and ( x[argKey] == argVal ) ]

    def findMissingKeyInDict(self, argTargetList, argKeyList):
        # return missing key (passed in argKeyList) from argDict
        return set(argTargetList) - set(argKeyList)

    def valRequiredArg(self, argumentDictArg, keyListArg, ignoreListArgs = None): 
        ''' 
            Description:    
                Validate argument, all argument listed in argKeyList must have a value in argRequest. This method is called internally
                Returns tuple(Result, missingArg, message)
            argReuest:      
                Dictionary object must be in following format
            usage:          
                valRequiredArg(<dictionary object>, <keyList>)
            Example:
                Validate argument (arg1 and arg2) and ignore arg2 to be validated
                valRequiredArg({'arg1':'val1','arg2':'val2'},['arg1','arg2'],['arg2'])
                
        '''

        myValResult = self.Global.UnSuccess
        myMissingArgs = []
        myValMessage = ''

        mykeyListArg = copy.deepcopy(keyListArg)
        myignoreListArgs = copy.deepcopy(ignoreListArgs)
        myargumentDictArg = copy.deepcopy(argumentDictArg)

        ''' lets remove the ignore key from argKeyList, if ignore list is passed '''
        # we need to remove all the argument which is not part of validation and if its passed
        myRemoveKey = list(set(myargumentDictArg.keys()) - set(mykeyListArg))
        self.removeKeyFromDict(myargumentDictArg, myRemoveKey)
        
        # we need to remove ignored keys from argRequestDict
        if not(myignoreListArgs == None):
            #print('IgnoredKeyList is not empty',mykeyListArg, myignoreListArgs)
            self.removeKeyFromList(mykeyListArg, myignoreListArgs)
            self.removeKeyFromDict(myargumentDictArg, myignoreListArgs)
            #print('IgnoredKeyList removed',mykeyListArg)
        #fi

        # check if all key in dictionary
        if all(key in myargumentDictArg for key in mykeyListArg):

            # check if any key in dict has None or empty value
            if myargumentDictArg == dict ((key, values) for key, values in myargumentDictArg.items() if values):
                myValResult = self.Global.Success
            else:
                for key,val in myargumentDictArg.items():
                    if not val:
                        myMissingArgs.append(key)
                    #fi
                #end for loop
                myValMessage = 'Arg Validation; empty arg(s) ' + str(myMissingArgs)
            #fi
        else:

            #need to find out which key is missing
            for key in mykeyListArg:
                if not key in myargumentDictArg:
                    myMissingArgs.append(key)
                #fi
            #end for loop
            myValMessage = 'Arg Validation; missing arg(s) ' + str(myMissingArgs)
        #fi

        return myValResult, myMissingArgs, myValMessage 

    def valResponseMode(self, argResponseMode):
        if len(argResponseMode) == 1:
            return argResponseMode in self.Global._Global__ValidResponseModeLsit
        else:
            return False

    def buildResponse(self, responseArg, statusArg, messageArg, dataArg = {}):
        '''
        Description: 
            Build response data for a method, this should be called from each method before returnin regardless of execution status (Normal/Exception)
        Arguments:
            statusArg: Status of the executed function Global.Success/UnSuccess ('Success/UnSuccess')
            messageArg: Message, if methd encountered error, Traceback/Error message should be passed
            dataArg: Data to be returned as dict
        Usage:
            buildResponse('Success','Success',{'Key':'Value'})
            buildResponse('UnSuccess','<error message/traceback',None)

        ''' 

        if statusArg:
            responseArg['Status'] = statusArg
        if messageArg:
            responseArg['Message'] = messageArg
        if dataArg:
            responseArg['Data'] = dataArg

        return responseArg

    def getResponseTemplate(self):
        '''
        Description: 
            Returns skeleton of Response template
        Arguments:
            None
        Usage:
            getResponseTemplate()
        Returns: 
            skeleton of response template
        ''' 
        return self.getACopy(self.Global.Template[self.Global.ResponseTemplate])

    def extractStatusFromResult(self, resultArg):

        if 'Status' in resultArg:        
            return resultArg['Status']

    def extractDataFromResult(self, resultArg):
        if 'Data' in resultArg:        
            return resultArg['Data']

    def getACopy(self, argDictList):
        if self.isDict(argDictList) or self.isList(argDictList):
            return copy.deepcopy(argDictList)
        else:
            return argDictList
        
    def isAllArgValid(self,*args):
        ''' 
            Description:    Checks if any argument passed to this function has Null/None/Empty/Zero value
            *args:          All argumnet seperated by comma, any # of arguments can be passed
            usage:          ( isAllArgValid(<*args>)
        '''
        return (all (args))

    def findPagingValue(self, argTotDocuments, argPageSize, argRequestedPage = None):
        ''' 
            Description:    Build paging information needed for summary section of data being returned
            Arguments:      argTotDocuments:    Total docments
                            argPageSize:        Page size (total documents in a page)
                            argRequestedPage:   Requested Page
            usage:          ( findPagingValue(<argTotDocuments, argPageSize, argRequestedPage>)
        '''

        if argRequestedPage == None:
            argRequestedPage = 1

        if argTotDocuments <=  argPageSize:
            myTotPages = 1
        else:
            myTotPages = argTotDocuments / argPageSize 
             
        #if requested page is out of bound display message "out of bound"

        if ( argRequestedPage > myTotPages ):
            myStatus = "ERROR: Out of bound page request"
            #myDisplay = "0"
        else:
            myStatus = "OK"
            #myDisplay = str( (argRequestedPage * argPageSize) +1 ) + " to " + str(((argRequestedPage * argPageSize) + 1) + argPageSize)

        return myStatus, myTotPages

    def isKeyInDict(self, argDict, argKeyName):
        ''' 
            Description:    Find if a given key present in dictionary
            Arguments:      argDict:            Dcit in which key need to be searched for 
                                                    (if nested dict, pass the dict key value in which search need to be made)
                            argKeyName:        Key name which need to be searched in this dictionary
            usage:          ( isKeyInDict(<argDict, argKeyName>)
        '''
        return argKeyName in argDict

    def isEmptyKey(self, argDict, argKeyName):
        ''' 
            Description:    Check if a key in dict is empty
            Arguments:      argDict:            Dcit in which key need to be searched for 
                                                    (if nested dict, pass the dict key value in which search need to be made)
                            argKeyName:        Key name which need to be searched in this dictionary
            usage:          ( isKeyInDict(<argDict, argKeyName>)
        '''
        return (not argKeyName[argDict])

    def getCurrentIsoDate(self, argDict, argKeyName):
        myIsoDateString = request.GET.isoDateString
        myIsoDate = datetime.datetime.strptime(myIsoDateString, '%Y-%m-%dT%H:%M:%S.%fZ')

    def getCurrentError(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        return myErrorMessage

    def extractValFromTuple(self, argTuple, argPosition):
        if len(argTuple) >= int(argPosition):
            return argTuple[argPosition]
        else:
            return None
        #fi

    def extractAllFromReq(self, argRequestDict):
        ''' 
            Description:    Extracts all argument passed to request
            Arguments:      Request json dict data 
            usage:          ( extractRequest(<argRequestDict>)
        '''
        myStatus = myScreenId = myActionId = myRequestData = ''

        if self.isDict(argRequestDict):
            myStatus = self.Global._Global__Success
            myScreenId = argRequestDict['Request']['Header']['ScreenId']
            myActionId = argRequestDict['Request']['Header']['ActionId']
            myRequestData = argRequestDict['Request']['MainArg']
        else:
            myStatus = self.Global._Global__Error

        return myStatus, myScreenId, myActionId, myRequestData 

    def extMainArgFromReq(self, argRequestDict):
        ''' 
            Description:    Extracts Main Argument passed to request
            Arguments:      Request json dict data 
            usage:          ( extractRequest(<argRequestDict>)
        '''
        return self.extractAllFromReq(argRequestDict)[3]

    def builInternalRequestDict(self, argRequestDict):
        ''' 
            Description:    Build request data for internal purpose
            Arguments:      Request json dict data, will use screenId:99999, ActionId: 99999
            usage:          ( builRequestData(<argRequestDict>)
        '''
        myRequestData = self.getTemplateCopy(self.Global._Global__RequestTemplate)
        #print ('Request:', myRequestData)
        #print ('Internal Scr:', self.Global._Global__InternalScreenId)
        myRequestData["Request"]["Header"]["ScreenId"] = self.Global._Global__InternalScreenId
        myRequestData["Request"]["Header"]["ActionId"] = self.Global._Global__InternalActionId 
        myRequestData["Request"]["Header"]["Page"] = self.Global._Global__InternalPage
        myRequestData["Request"]["MainArg"] = argRequestDict["Data"]

        return myRequestData

    def buildInitHistData(self):
        ''' building initial history data for a given collection '''
        #myHistoryData = self.envInstance.defaultsData["History"]
        myHistoryData = self.getTemplateCopy(self.Global._Global__HistoryTemplate)

        myHistoryData["InitChange"]["When"]=datetime.datetime.utcnow()
        myHistoryData["InitChange"]["Message"]="Initial creation"            
        myHistoryData["LastChange"]["When"]=datetime.datetime.utcnow()
        myHistoryData["LastChange"]["Message"]="Initial creation"            
        
        return myHistoryData

    def buildActivityArg(self,argEntityId, argEntityType, argActivityType, argActivity, argAuth=None):

        myActivityLogData = self.getTemplateCopy(self.Global._Global__activityLogColl)

        myActivityLogData["EntityType"]=argEntityType
        myActivityLogData["EntityId"]=argEntityId            
        myActivityLogData["ActivityType"]=argActivityType
        myActivityLogData["Activity"]=argActivity
        myActivityLogData["Auth"]=argAuth            
        self.removeKeyFromDict(myActivityLogData, ['Acknowledged','ActivityDate'])
        return myActivityLogData

    def getRequestStatus(self, argStatus, argStatusMessage = None, argData = None, argTraceBack = None):
        myRequestStatus = self.getCopy(self.Global._Global__RequestStatus)
        if argStatus:
            myRequestStatus.update({'Status' :argStatus})
        if argStatusMessage:
            myRequestStatus.update({'Message' : argStatusMessage})
        else:
            myRequestStatus.update({'Message' : argStatus})
        #fi
        if argData:
            myRequestStatus.update({'Data' : argData})
        #fi
        if argTraceBack:
            myRequestStatus.update({'Traceback' : argTraceBack}) 
        #fi
        return myRequestStatus

    def buildResponseData(self, responseModeArg, resultStatusArg, resultDataArg = {}):
       
        ''' if this is internal request, we should not built the response, response will be built by mehtod whcih
        was called externally     '''

        if (argResponseMode == self.Global._Global__InternalRequest):
            if argResultData:
                return argResultData
            else:
                return argResultStatus
            #fi
        #fi

        #myResponseData = self.envInstance.getTemplateCopy(self.Global._ResponseTemplate)
        myResponseData = self.getTemplateCopy(self.Global.ResponseTemplate)
        #print("Response",myResponseData)
        myData = argResultData

        if (argResultType == 'Update'):
            myResponseStatus = self.getUpdateStatus(argResultStatus)
            myResponseData['MyResponse']['Header']['Status'] = myResponseStatus
            myResponseData['MyResponse']['Header']['Message'] = myResponseStatus
        elif (argResultType == 'Insert'):
            myResponseStatus = self.getCreateStatus(argResultStatus)
            myResponseData['MyResponse']['Header']['Status'] = myResponseStatus
            myResponseData['MyResponse']['Header']['Message'] = myResponseStatus
        elif (argResultType == 'Find'):
            myResponseData['MyResponse']['Header']['Status'] = argResultStatus['Status']
            myResponseData['MyResponse']['Header']['Message'] = argResultStatus['Message']
            myResponseData['MyResponse']['Header']['Traceback'] = argResultStatus['Traceback']
            #myData = argResult
        elif (argResultType == 'Error'):
            #print("Success",self.Global._Global__Success)
            myResponseData['MyResponse']['Header']['Status'] = argResultStatus['Status']
            myResponseData['MyResponse']['Header']['Message'] = argResultStatus['Message']
            myResponseData['MyResponse']['Header']['Traceback'] = argResultStatus['Traceback']
            myData = []

        ''' if data element passed, we will copy the "Data" to "Data" section, "Data.Summary" to "Header.Summary" secton'''
        try:
            # if myData is not iterable, exception will be raised, will ignore the exception 
            if (myData) and (self.Global._Global__DataKey in myData) and (myData[self.Global._Global__DataKey]):
                myResponseData['MyResponse'][self.Global._Global__DataKey] = myData[self.Global._Global__DataKey]
                if (self.Global._Global__SummaryKey in myData) and (myData[self.Global._Global__SummaryKey]):
                    myResponseData['MyResponse']['Header'][self.Global._Global__SummaryKey]= myData[self.Global._Global__SummaryKey]    
            elif (myData) and (self.Global._Global__DataKey not in myData):
                ''' we got data but "data" key is missing '''
                if self.isDict:
                    myResponseData['MyResponse'][self.Global._Global__DataKey] = [myData]
                else:
                    myResponseData['MyResponse'][self.Global._Global__DataKey] = myData
                #fi
            #fi                    
        except TypeError:
            pass

        return myResponseData 

    def extrAllDocFromResultSets(self, argResultSets):
        if (self.Global._Global__DataKey in argResultSets) and (argResultSets[self.Global._Global__DataKey]):
            return argResultSets[self.Global._Global__DataKey]
        else:
            return None

    def extr1stDocFromResultSets(self, argResultSets):
        if (self.Global._Global__DataKey in argResultSets) and (argResultSets[self.Global._Global__DataKey]):
            return argResultSets[self.Global._Global__DataKey][0]
        else:
            return None

    def extrSummFromResultSets(self, argResultSets):
        if self.Global._Global__SummaryKey in argResultSets:
            return argResultSets[self.Global._Global__SummaryKey]
        else:
            return None

    def extrStatusFromResultSets(self, argResultSets):
        if (self.Global._Global__StatusKey in argResultSets[self.Global._Global__SummaryKey]):
            return argResultSets[self.Global._Global__SummaryKey][self.Global._Global__StatusKey]
        else:
            return None

    def whoAmI(self):
        ''' return callers method/function anme and from line# call is made'''
        caller = sys._getframe(1).f_code.co_name
        caller_linenum = sys._getframe(1).f_lineno
        return caller

    def buildKeysFromTemplate(self, argTemplateName, argBlockName = None):
        # get a templaye copy for a given collection
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.Utility')
            myEmptyTemplate = self.getTemplateCopy(argTemplateName)
            #print(myEmptyTemplate)
            if not (argBlockName == None) and argBlockName in myEmptyTemplate:
                myEmptyTemplate = myEmptyTemplate[argBlockName]
            
            ## lets build the keys
            myAllKeys = []
            for myKey in myEmptyTemplate:
                myAllKeys.append(myKey)

            return myAllKeys

        except Exception as error:
            myModuleLogger.exception('An error [{error}] occurred'.format(error=error.message))
            raise

    def buildAuth(self, argLoginId, argLoginType, argDeviceType, argDeviceOs, argMacAddress, argSessionId, argEntityType, argEntityId,argAppVer):
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.Utility')            
            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','SessionId','EntityType','EntityId','AppVer']
            myFrame = inspect.currentframe()
            myAllArgs, _, _, myValues = inspect.getargvalues(myFrame)
            for myArg in myAllArgs:
                if self.isEmptyKey(myValues[myArg]):
                    raise com.uconnect.error.MissingArg('Argument [{arg}] is empty !!!'.format(arg=myArg))

            myAuth = {
                'LoginId':argLoginId,
                'LoginType':argLoginType,
                'DeviceType':argDeviceType,
                'DeviceOs':argDeviceOs,
                'MacAddress':argMacAddress,
                'SessionId':argSessionId,
                'EntityType':argEntityType,
                'EntityId':argEntityId,
                'AppVer':argAppVer}
            return myAuth
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise

    def getNonEmptyKeyFromDict(self, argRequestDict):
        ''' return all non empty key from dictionary, passed argument is not changed'''
        #return dict ((k,v) for k, v in argRequestDict.iteritems() if v) ### Iteritems has been changed to items
        return dict ((k,v) for k, v in argRequestDict.items() if v)
    def isAnyKeyInDict(self, argKeyList, argDict):
        # check if any of the key value from List present in keys in dictionnary
        return any(key in argKeyList for key in argDict.keys())

    def removeKeyFromList(self, argRequestList, argRemoveKeyList):
        ''' remove key(s) from list '''
        for myKey in argRemoveKeyList:
            if myKey in argRequestList: 
                argRequestList.remove(myKey)

        return argRequestList

    def removeKeyFromDict(self, argRequestDict, argRemoveKeyList):
        ''' remove key(s) from Dict '''
        for myKey in argRemoveKeyList:
            if myKey in argRequestDict:
                del argRequestDict[myKey]

        return argRequestDict

    ''' Member Utility '''

    def getTemplateCopy(self, templateArg):
        ''' Returns a copy of a template for an entity defined in template.json; For e.g. Member/Group/Vendor/History '''

        try:

          if templateArg in self.Global.template:
            return copy.deepcopy(self.Global.template[templateArg])
          else:
            raise InvalidTemplate('Template [{template}] is missing in template repository !!! '.format(template=argTemplate))

        except Exception as error:
           raise

    def getRanddomNum(self, argNumLength):
        #print(argNumLength)
        if argNumLength == None: return None
        myLowerBound = 10**(argNumLength-1)
        myUpperBound = 10**argNumLength-1
        return random.randint(myLowerBound, myUpperBound)

