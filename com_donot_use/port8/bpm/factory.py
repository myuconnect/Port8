import importlib,logging, com.port8.core.error 
from com.port8.core.utility import Utility
from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.infrastructure import RestInfra

#from com.uconnect.bps.scheduleBPS import Schedule

#myLogger = logging.getLogger('Port8')

class Factory(object, metaclass=Singleton):
    '''
    This is Factory class, this will execute a BO process as mapped in config/FactoryMetadata.json
    '''
    def __init__(self):
        #self.util = Utility.Instance()
        self.globals = Global()
        self.util = Utility()
        self.infra = RestInfra()
        self.Logger = self.infra.Logger
        #self.myClass = self.__class__.__name__

    def processRequest(self, argRequestDict):
        ''' 
            Description:    Update key in dictDocument for a given collection, this is a private method
            argCollection:  Collection name
            argDictDocument:Dict documents
            usage:          <processRequest(argRequestDict)
        '''
        try:

            self.Logger.debug("arg received [{args}]".format(args=argRequestDict))
            myMainArgData = self.util.getACopy(argRequestDict)

            ''' Validating argumemt received '''
            isValidRequest = self.util.isValidRestRequest(myMainArgData)

            if not (isValidRequest):
                raise com.port8.core.error.InvalidArguments("Arg validation error {arg}".format(arg=myMainArgData))
            else:
                self.Logger.debug('validated request, its a valid request >>> {req}'.format(req= str(argRequestDict)))
            #fi

            myPageId = myMainArgData['Page']
            myActionId = myMainArgData['Action']
            myArguments = myMainArgData['Arguments']

            myResult = self.__findBPSProcess (myPageId, myActionId)
            if myResult['Status'] == self.globals.Success:
                myBPMProcess = myResult['Data']
            else:
                # we did not find BPM process, returing result
                return myResult

            # extracting tuple value returned from above method

            #myLibrary, myClass, myMethod = bpsProcessVal
            if myBPMProcess:
                self.Logger.debug("found, bpm process [{bpmproc}]".format(bpmproc=myBPMProcess))
                myResponse = self.__executeBPSPRocess(myBPMProcess['lib'], myBPMProcess['cls'], myBPMProcess['method'], myArguments) 
                #myRquestStatus = self.util.getRequestStatus(self.globals.Success)            
            else:
                self.Logger.debug("did not find mapped bpm process")
                myRquestStatus = self.util.getRequestStatus(\
                    self.globals.UnSuccess,'Invalid Page [{page}] Action [{action}]'.format(page=myPageId, action=myActionId))
                myResponse = self.util.buildResponseData(myRquestStatus,'Error')

            self.Logger.debug('myResponse data >>> {response}'.format(response = myResponse))
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.logError()
            myResponse = self.util.buildResponseData(myRequestStatus, 'Error')
            return myResponse

    def __findBPSProcess(self, argPageId, argActionId):
        ''' 
            Description:This is private methd called internally in Factry class; Find BMP method call for a given request (pageid, actionid) 
            Arguments:  pageid and action id (pageid, actionid)
            Usage:      <__findBPSProcess(<pageid>,<actionid>)>
            Return:     BPM_CALL_JSON dict {'cls': <class>, lib : <library>, method : <mehtod>, args : <arguments needed>} 
        '''
        try:

            self.Logger.debug("arg received [{page},{action}]".format(page=argPageId, action=argActionId))

            page = [page for page in self.infra.factoryMetadata if page['PAGE_ID'] == argPageId and page['PAGE_STATUS'] == 'ACTIVE'] 
            # if we found multiple page, will log the details
            if len(page) > 1:
                self.Logger.ERROR('Expecting 1 entry per page, found {found}, Factory metadata >> {factoryData}'.
                    format(found = len(page), factoryData = self.infra.factoryData))

                myResponse = self.util.buildResponse(\
                    self.globals.UnSuccess, 
                    'Metadata is corrupted (found [{cnt}] occurrance of page [{page}]'\
                        .format(cnt = len(page), page=argPageId))
                return myResponse
            
            if len(page) == 0:
                # we did not find page
                self.Logger.debug('did not find requested page >>> {page}'.format(page=argPageId))

                myResponse = self.util.buildResponse(\
                    self.globals.UnSuccess, 
                    'Missing requested page in metadata >>> {page}'.format(page=argPageId))
                return myResponse

            # we found one page, get the 1st item from list
            self.Logger.debug('found matching page [{page}] in factory metdata'.format(page = argPageId))
            page = page[0]
            pageActions = page['ACTIONS']

            if pageActions:
                actionIndx = [indx for indx, val in enumerate(pageActions) if pageActions[indx]['ACTION_ID'] == argActionId ]
                 #print("found ??? >>>",actionIndx, pageActions)
                if actionIndx:
                    self.Logger.debug('found matching action [{action}] on page [{page}] in factory metdata'.format(action = argActionId, page = argPageId))
                    if isinstance(actionIndx, list):
                        actionIndx = actionIndx[0]
                    #myBPMCallJson = self.infra.factoryMetadata[argPageId][actionIndx][argActionId]
                    #print("found action >>>",actionIndx, pageActions, pageActions[actionIndx] )
                    myBPMCallJson = pageActions[actionIndx]['BPM_CALL_JSON']
                    self.Logger.debug('BPM Json call found >>> {bpm}'.format(bpm = str(myBPMCallJson)))
                    myResponse = self.util.buildResponse(\
                        self.globals.Success, self.globals.Success,myBPMCallJson)
                    return myResponse
                    #return myBPMCallJson
                else:
                    self.Logger.debug('action [{action}] not found for page [{page}] in factory metdata'.format(action = argActionId, page = argPageId))
                    myResponse = self.util.buildResponse(\
                        self.globals.UnSuccess, 
                        'Missing requested action [{action}] for page >>> {page}'.format(action = argActionId, page=argPageId))
                    return myResponse
            else:
                myResponse = self.util.buildResponse(\
                    self.globals.UnSuccess, 
                    'Empty actions for page in metadata >>> {page}'.format(page=argPageId))
                return myResponse

        except Exception as err:
            #myRequestStatus = self.util.extractLogError()
            raise

    def __executeBPSPRocess(self, argLib, argCls, argMethod, arguments):
        ''' 
            Description:Private method, internally called in Factory method, execute Factory bpm process
            Arguments:  lib, class, method, arguments
            usage:      <__executeBPSPRocess(<lib>,<cls>,<method>,<arguments>) >
            Return:     Return results in array
        '''  
        try:

            self.Logger.debug("arg received [{lib},{cls},{method},{args}]".format(lib=argLib,cls=argCls,method=argMethod,args=arguments))

            myModule = importlib.import_module(argLib)
            myClass = getattr(myModule, argCls)
            # if singleton, get an instance else instantiate the class
            if hasattr(myModule,'Singleton') and hasattr(myClass,'Instance') :
                myCallableClass = myClass.Instance()
            else:
                myCallableClass = myClass()

            # get the method from this class
            myMethod = getattr(myCallableClass,argMethod)
            ''' Only MainArg need to be passed  '''
            #myMainArg = {'MainArg':self.util.extMainArgFromReq(argReqJsonDict)}
            ''' need to mark that this response is external '''
            #myMainArg['MainArg'].update({'ResponseMode':self.globalInstance._Global__ExternalRequest})

            # execute the method
            if arguments:
                self.Logger.info("executing method with arguments >>>[{lib}.{cls}.{method} {args}]".format(lib=argLib,cls=argCls,method=argMethod,args=arguments))
                myResults = myMethod(arguments)
            else:
                self.Logger.info("executing method w/o arguments >>>[{lib}.{cls}.{method}]".format(lib=argLib,cls=argCls,method=argMethod))
                myResults = myMethod()

            self.Logger.debug('results after execution >>> {data}'.format(data=str(myResults)))
            return (myResults)

        except Exception as err:
            #myRequestStatus = self.util.extractLogError()
            #myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            raise