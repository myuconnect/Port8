import os,sys,traceback,datetime,copy,random, importlib,time, ast
from jsonschema import *

from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.error import *

# Python 3:
#Removed dict.iteritems(), dict.iterkeys(), and dict.itervalues().
#Instead: use dict.items(), dict.keys(), and dict.values() respectively.@Singleton

class Utility(object, metaclass=Singleton):

    def __init__(self):
        self.globals = Global()
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

    def isValidRestRequest(self, reqDict):
        '''
        Description: Checks if request passed as dict had all the structure of Request template
        '''
        #print(reqDict, type(reqDict))
        if not isinstance(reqDict, dict):
            print("Request is not dict type")
            return False

        myRequestTemplate = self.getACopy(self.globals.Template['Request'])
        print('Request template >>>', str(myRequestTemplate))
        myReqStru = self.getDictStru(myRequestTemplate)
        myReqTemplateStru = self.getDictStru(reqDict)
        print('Request structure (passed) >>>', myReqStru)
        print('Request template structure (passed) >>>', myReqTemplateStru) 
        return myReqStru == myReqTemplateStru 

    def getDictStru(self, argDict):
        if self.isDict(argDict):
            return argDict.keys()

    def getNestedDictStru(self, argDict):
        if self.isDict(argDict):
            return {key:self.getNestedDictStru(argDict[key]) for key in argDict}

    def joinListContents(self, listArg, listSep):
        return listSep.join(listArg)

    def removeEmptyValueKeyFromDict(self, argDict):
        # removes key if it has empty or 0 value
        myMainArgData = self.getACopy(argDict)
        return dict([(key,value) for key,value in myMainArgData.items() if (value)])

    def removeEmptyValueFromList(self, argList):
        # removes key if it has empty or 0 value
        myMainArgData = self.getACopy(argList)
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

    def removeEmptyKeyFromDict(self, argDict):
        myArgDict = self.getACopy(argDict)
        myAllEmptykeys = self.getEmptyKeyFromDict(myArgDict)
        myArgDict = self.removeKeyFromDict(myAllEmptykeys, myArgDict)
        return myArgDict

    # List/Array util

    def isList(self, argValue):
        try:
            if isinstance(argValue,list): 
                return True
            else:
                return False
        except Exception as error:
            return False

    # return all ocurrence index of matched value in list
    def getIndxValInList(self, argList, argValue):
        try:
            if isinstance(argList, list):
                return  [indx for indx, val in enumerate(argList) if val == argValue]

        except Exception as error:
            return None

    # return index of 1st occurrence of matched value
    def getValCntInList(self, argList, argValue):
        try:
            if isinstance(argList, list):
                return argList.count(argValue)
                
        except Exception as error:
            return None

    # return all ocurrence index of matched value
    def get1stIndxValInList(self, argList, argValue):
        try:
            if isinstance(argList, list):
                #print('argument is list, proceeding')
                allMatchedIndex = self.getIndxValInList(argList, argValue)
                #print('toal match >>', allMatchedIndex)
                if allMatchedIndex:
                    return allMatchedIndex[0]

        except Exception as error:
            return None

    def valRequiredArg(self, argumentDictArg, keyListArg, ignoreListArgs = None): 
        ''' 
            Description:    
                Validate argument, all argument listed in argKeyList must have a value in argRequest. This method is called internally
                Returns tuple(Result, missingArg, message)
            argReuest:      
                Dictionary object
            usage:          
                valRequiredArg(<dictionary object>, <keyList>)
            Example:
                Validate argument (arg1 and arg2) and ignore arg2 to be validated
                valRequiredArg({'arg1':'val1','arg2':'val2'},['arg1','arg2'],['arg2'])
                
        '''

        myValResult = self.globals.UnSuccess
        myMissingArgs = []
        myValMessage = ''

        if not isinstance(argumentDictArg, dict):
            myValMessage = 'Argument must be type of dict'
            return myValResult, myMissingArgs, myValMessage

        mykeyListArg = copy.deepcopy(keyListArg)
        myignoreListArgs = copy.deepcopy(ignoreListArgs)
        myargumentDictArg = copy.deepcopy(argumentDictArg)

        ''' lets remove the ignore key from argKeyList, if ignore list is passed '''
        # we need to remove all the argument which is not part of validation and if its passed
        myRemoveKey = list(set(myargumentDictArg.keys()) - set(mykeyListArg))
        self.removeKeyFromDict(myRemoveKey, myargumentDictArg)
        
        # we need to remove ignored keys from argRequestDict
        if not(myignoreListArgs == None):
            #print('IgnoredKeyList is not empty',mykeyListArg, myignoreListArgs)
            self.removeKeyFromList(myignoreListArgs, mykeyListArg)
            self.removeKeyFromDict(myignoreListArgs, myargumentDictArg)
            #print('IgnoredKeyList removed',mykeyListArg)
        #fi

        # check if all key in dictionary
        if all(key in myargumentDictArg for key in mykeyListArg):

            # check if any key in dict has None or empty value
            if myargumentDictArg == dict ((key, values) for key, values in myargumentDictArg.items() if values):
                myValResult = self.globals.Success
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
            return argResponseMode in self.globals._Global__ValidResponseModeLsit
        else:
            return False

    def buildResponse(self, statusArg, messageArg, dataArg = None):
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
        myResponse = self.getACopy(self.globals.Template['Response'])
        if statusArg:
            myResponse['Status'] = statusArg
        if messageArg:
            myResponse['Message'] = messageArg
        if dataArg:
            myResponse['Data'] = dataArg

        return myResponse

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
        return self.getACopy(self.globals.Template[self.globals.ResponseTemplate])

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
            myStatus = self.globals._Global__Success
            myScreenId = argRequestDict['Request']['Header']['ScreenId']
            myActionId = argRequestDict['Request']['Header']['ActionId']
            myRequestData = argRequestDict['Request']['MainArg']
        else:
            myStatus = self.globals._Global__Error

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
        myRequestData = self.getTemplateCopy(self.globals._Global__RequestTemplate)
        #print ('Request:', myRequestData)
        #print ('Internal Scr:', self.Globals._Global__InternalScreenId)
        myRequestData["Request"]["Header"]["ScreenId"] = self.globals._Global__InternalScreenId
        myRequestData["Request"]["Header"]["ActionId"] = self.globals._Global__InternalActionId 
        myRequestData["Request"]["Header"]["Page"] = self.globals._Global__InternalPage
        myRequestData["Request"]["MainArg"] = argRequestDict["Data"]

        return myRequestData

    def buildInitHistData(self):
        ''' building initial history data for a given collection '''
        #myHistoryData = self.envInstance.defaultsData["History"]
        myHistoryData = self.getTemplateCopy(self.globals._Global__HistoryTemplate)

        myHistoryData["InitChange"]["When"]=datetime.datetime.utcnow()
        myHistoryData["InitChange"]["Message"]="Initial creation"            
        myHistoryData["LastChange"]["When"]=datetime.datetime.utcnow()
        myHistoryData["LastChange"]["Message"]="Initial creation"            
        
        return myHistoryData

    def buildActivityArg(self,argEntityId, argEntityType, argActivityType, argActivity, argAuth=None):

        myActivityLogData = self.getTemplateCopy(self.globals._Global__activityLogColl)

        myActivityLogData["EntityType"]=argEntityType
        myActivityLogData["EntityId"]=argEntityId            
        myActivityLogData["ActivityType"]=argActivityType
        myActivityLogData["Activity"]=argActivity
        myActivityLogData["Auth"]=argAuth            
        self.removeKeyFromDict(myActivityLogData, ['Acknowledged','ActivityDate'])
        return myActivityLogData

    def getRequestStatus(self, argStatus, argStatusMessage = None, argData = None, argTraceBack = None):
        myRequestStatus = self.getACopy(self.globals.RequestStatus)
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

    def buildResponseData(self, resultStatusArg, resultDataArg = {}):
       
        myResponse = self.getTemplateCopy(self.globals.ResponseTemplate)
        #print("Response",myResponseData)
        myData = resultDataArg

        try:
            myResponse['Status'] = resultStatusArg
            myResponse['Data'] = myData
        except TypeError:
            pass

        return myResponse

    def extrAllDocFromResultSets(self, argResultSets):
        if (self.globals._Global__DataKey in argResultSets) and (argResultSets[self.globals._Global__DataKey]):
            return argResultSets[self.globals._Global__DataKey]
        else:
            return None

    def extr1stDocFromResultSets(self, argResultSets):
        if (self.globals._Global__DataKey in argResultSets) and (argResultSets[self.globals._Global__DataKey]):
            return argResultSets[self.globals._Global__DataKey][0]
        else:
            return None

    def extrSummFromResultSets(self, argResultSets):
        if self.globals._Global__SummaryKey in argResultSets:
            return argResultSets[self.globals._Global__SummaryKey]
        else:
            return None

    def extrStatusFromResultSets(self, argResultSets):
        if (self.globals._Global__StatusKey in argResultSets[self.globals._Global__SummaryKey]):
            return argResultSets[self.globals._Global__SummaryKey][self.globals._Global__StatusKey]
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

    def getNonEmptyKeyFromDict(self, argDict):
        ''' return all non empty key from dictionary, passed argument is not changed'''
        #return dict ((k,v) for k, v in argRequestDict.iteritems() if v) ### Iteritems has been changed to items
        return dict ((key,value) for key, value in argDict.items() if value)

    def getEmptyKeyFromDict(self, argDict):
        ''' return all non empty key from dictionary, passed argument is not changed'''
        #return dict ((k,v) for k, v in argRequestDict.iteritems() if v) ### Iteritems has been changed to items
        return dict ((key,value) for key, value in argDict.items() if not value)

    def isAnyKeyInDict(self, argKeyList, argDict):
        # check if any of the key value from List present in keys in dictionnary
        return any(key in argKeyList for key in argDict.keys())

    def isAllKeyInDict(self, argKeyList, argDict):
        # check if all key listed in argKeyList present in argDict
        return all(key in argDict.keys() for key in argKeyList)

    def getDictKeysNotinList(self, argKeyList, argDict):
        # return all keys not present in argKeyList
        return list(set(argDict) - set(argKeyList))

    def getKeysNotinDict(self, argKeyList, argDict):
        return list(set(argKeyList) - set(argDict))

    def removeKeyFromList(self, argRemoveKeyList, argRequestList):
        ''' remove key(s) from list '''
        for myKey in argRemoveKeyList:
            if myKey in argRequestList: 
                argRequestList.remove(myKey)

        return argRequestList

    def removeKeyFromDict(self, argRemoveKeyList, argRequestDict):
        ''' remove key(s) from Dict '''
        for myKey in argRemoveKeyList:
            if myKey in argRequestDict:
                del argRequestDict[myKey]

        return argRequestDict

    # Argument validation


    def valArguments(self, argKeyList, argDict):
        '''
        Description: Validate arguments
                        1. Remove Empty keys from dict 
                        2. ensure all argKeyList are present in argDict
                        #3. remove orphaned (keys not in keylist) keys from dict
        Usage: valArguments(<arg keylist>, <arg dict>)
        Return: Arg valdiation template >> {"Status" : '', "Message" : '', "Arguments" : {}, "MissingArg" : []} 
        '''
        #print(argDict)
        myArgValResult = self.getACopy(self.globals.Template['ArgValResult'])
        #myArgDict = self.getACopy(argDict)
        myArgDict = argDict
        myAllEmptykeys = self.getEmptyKeyFromDict(myArgDict)
        myArgDict = self.removeKeyFromDict(myAllEmptykeys, myArgDict)

        if self.isAllKeyInDict(argKeyList, myArgDict):
            myOrphanKeys = self.getDictKeysNotinList(argKeyList, myArgDict)
            #myDict = self.getACopy(argDict)
            #myPrunedDict = self.removeKeyFromDict(myDict, myOrphanKeys)

            myArgValResult['Status'] = self.globals.Success
            myArgValResult['Message'] = self.globals.Success

        else:
            # building arg validation template
            myMissingKeyList = self.getKeysNotinDict(argKeyList, argDict) 
            myArgValResult['Status'] = self.globals.UnSuccess
            myArgValResult['Message'] = 'Argument(s) missing >>> {args}'.format(args = argKeyList)
            myArgValResult['MissingArgs'] = myMissingKeyList

        return myArgValResult
        #raise InvalidArguments('Argument(s) missing >>> {args}'.format(args = myReqdKeyList))

    ''' Member Utility '''

    def getTemplateCopy(self, argTemplate):
        ''' Returns a copy of a template for an entity defined in template.json; For e.g. Member/Group/Vendor/History '''

        try:

          if argTemplate in self.globals.Template:
            return copy.deepcopy(self.globals.Template[argTemplate])
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

    ###################################
    # OS Utility - DIR and File utility

    def isFileExist(self, fileNamewPath):
        if os.path.isfile(fileNamewPath):
            return True
        else:
            return False

    def isDirExist(self, dirName):
        if os.path.isdir(dirName):
            return True
        else:
            return False

    def makeDir(self, dirName):
        if not self.isDirExist(dirName):
            os.makedirs(dirName)

    def getFileStat(self, fileName):
        '''
        Returns file/dir stats as tuple with following key:
            st_mode − protection bits.
            st_ino − inode number.
            st_dev − device.
            st_nlink − number of hard links.
            st_uid − user id of owner.
            st_gid − group id of owner.
            st_size − size of file, in bytes.
            st_atime − time of most recent access.
            st_mtime − time of most recent content modification.
            st_ctime − time of most recent metadata change.
        '''

        return os.stat(fileName)

    def buildFileWPath(self, dirName, fileName):
        return os.path.join(dirName, fileName)             

    def readTextFileAsGen(self, fileName):
        '''
        Description: Read text files line as generator
        '''
        if self.isFileExist(fileName):
            with open(fileName, 'r') as file:
                while True:
                    line = file.readline()
                    if not line:
                        break
                    yield line

    def getLineForPattern(self, fileName, keyPattern, matchCnt = 1, keyPos = 'STARTWITH'):
        '''
        Description: Return matched line from a text file for a given key pattern (either STARTSWITH or ANYWHERE in Line)
                    will return list/array
        '''
        matchedData = list()
        #matchedCnt = 0
        if matchCnt != self.globals.matchAll and matchCnt <= 0:
            return

        if keyPos not in [self.globals.keyPosSTARTWITH, self.globals.keyPosANYWHERE]:
            raise ValueError('KeyPos argumnet must be either {start} or {any}'.format(start = self.globals.keyPosSTARTWITH, any = self.globals.keyPosANYWHERE))

        for line in self.readTextFileAsGen(fileName):
            if keyPos == self.globals.keyPosSTARTWITH and line.startswith(keyPattern):
                matchedData.append(line)
                if matchCnt != self.globals.matchAll: matchCnt = matchCnt - 1
                #break
            elif keyPos == self.globals.keyPosANYWHERE and keyPattern in line:
                matchedData.append(line)
                if matchCnt != 'ALL': matchCnt = matchCnt - 1
                #break
            if matchCnt != self.globals.matchAll and matchCnt == 0 : break

        return matchedData

    def loadTextFile(self, fileName, outputType = 'str'):
        if self.isFileExist(fileName):
            if outputType not in ('str', 'lst'):
                raise ValueError('Output type must be either String or Array')

            outData = str() 
            if outputType ==  'list':
                outData = list()

            with open(fileName, 'r') as file:
                #line = file.readlines()
                line = file.readline()

                while line:
                    if not line.startswith('#'):
                        if isinstance(outData, str):
                            outData = outData + line
                        else:
                            outData.append(line)
                    line = file.readline()

            return outData


    ###################################
    # OS Utility - Environment

    def isEnvSet(self, envKey):
        return envKey in os.environ

    def getEnv(self, envKey):
        return os.getenv(envKey)

    def setEnv(self, envKey, envValue):
        os.environ[envKey] = envValue

    ###################################
    # OS Utility - OS Info

    def getUname(self):
        return os.uname()[:]
    
    ###################################
    # OS Utility - Run os command

    def runOsCmd(self, osCmdList):
        if isinstance(osCmdList, list):
            from subprocess import Popen, PIPE
            try:
                process = Popen(osCmdList, stdout = PIPE, stderr = PIPE, shell=True)
                result = process.communicate()
                process.stdout.close()
                process.stderr.close()
                # result is tuple, 1st value is stdout and 2nd value is stderror
                return result
            except Exception as e:
                raise e

    ###################################
    # Encryption

    def __encryptText(self, text):
        import base64
        return base64.b64encode(text.encode('utf8'))

    def __decrypt2Text(self, text):
        import base64
        return base64.b64decode(text).decode('utf8')

    def encrypt(self, secretKey, clearText):
        '''
        Description: Encrypt clear text with Secret key
        '''
        import base64
        encryptText = []
        for i in range(len(clearText)):
            key_c = secretKey[i % len(secretKey)]
            enc_c = chr((ord(clearText[i]) + ord(key_c)) % 256)
            encryptText.append(enc_c)
        return base64.urlsafe_b64encode("".join(encryptText).encode('utf-8')).decode('utf-8')

    def decrypt(self, secretKey, encryptText):
        '''
        Description: Descrypt encrypted text to clear text with Secret key
        '''
        import base64
        decryptText = []
        #enc = base64.urlsafe_b64decode(encryptText).decode('utf-8')
        enc = base64.urlsafe_b64decode(encryptText).decode()

        for i in range(len(enc)):
            key_c = secretKey[i % len(secretKey)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            decryptText.append(dec_c)
        return "".join(decryptText)

    def buildDBResponse(self, status, data, rows, message = None):
        myDBResponse = self.getACopy(self.globals.Template['DBResponse'])
        myDBResponse['Status'] = status
        myDBResponse['Data'] = data
        myDBResponse['Rows'] = rows
        myDBResponse['Message'] = message

        return myDBResponse

    ###################################
    # Python: package validation etc.

    def isPackageInstalled(self, packageName):
        if packageName:
            spec = importlib.util.find_spec(packageName)
            if spec is None:
                return False
            else:
                return True

    def logError(self, logger = None):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_text = (repr(traceback.format_exception(exc_type, exc_value,exc_traceback, limit=8)))
        if logger:
            logger.ERROR(error_text)
        return error_text

    ########################################################
    #
if __name__ == "__main__":
    util = Utility()
    # all argument must not have additional white space before and after the command
    #cmd = ['ls -ltr | wc -l']
    #data = util.runOsCmd(cmd)
    #print('output >>>' ,data)
    '''
    mydata = ''
    data = util.loadTextFile('temp.txt','str')
    print(data, type(data))
    data = util.getLineForPattern('temp.txt','ne','ALL','ANYWHERE')
    print(data)
    '''
    key = self.env.environment
    text = 'This is my text'
    etext = util.encrypt(key,text)
    dtext = util.decrypt(key,etext)
    print('enc',etext)
    print('dec',text)