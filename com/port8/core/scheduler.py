import os, json, sys

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


class Scheduler(object, metaclass=Singleton):
    '''
    Description: Port8 scheduler process, this class is gateway to interact Port8 scheduler
    Steps:
        1. Instantiate this class
        2. Call startScheduler to start the scheduler (sync scheduler data from db will internally called to ensure the job stored in repositoy is in-sync
            with scheduler job store)
        3. call stopScheduler to stop the scheduler
        4. call addIntervalJob/addCronjob to schedule the job
    '''

    def __init__(self, argSchedulerType = 'Blocking', argSchedulerMode = 'Run'):

        try:
            # initializing
            self.Global = Global()
            self.Utility = Utility()
            self.InfraUtil = InfraUtility()
            self.db = DBMySql('Scheduler')
            self.Validation = Validation()
            self.ShcedUtil = SchedUtility()

            self.myModulePyFile = os.path.abspath(__file__)
            self.myClass = self.__class__.__name__
            self.mySchedulerType = argSchedulerType
            self.mySchedulerMode = argSchedulerMode

            #validating arguments
            self.Validation.validateSchedulerInitArg(self.mySchedulerType, self.mySchedulerMode,  InvalidArguments)

            #Setting the infrastructure
            self.Infra = self.InfraUtil.setInfra(self.Global.SchedulerInfraKey)

            if not self.Infra:
                raise InfraInitializationError('Could not initialize {cls}'.format(cls=(self.myModulePyFile,self.myClass)))

            #self.logger = self.Infra.SchedLogger
            self.logger = self.Infra.getInfraLogger(self.Global.SchedulerInfraKey)

            #self.__loadNStartcheduler__()

        except Exception as err:
            print(sys.exc_info()[1:],traceback.format_exc(limit=5))
            sys.exit(-1)

    def startScheduler(self):
        try:
            self.scheduleSchema = self.Utility.getACopy(self.Infra.scheduleSchema)
            self.intervalSchema = self.Utility.getACopy(self.Infra.intervalSchema)
            self.cronSchema = self.Utility.getACopy(self.Infra.cronSchema)
            self.processJobSchema = self.Utility.getACopy(self.Infra.processJobSchema)

            if self.mySchedulerMode == 'Run':
                argPaused = False
            else:
                argPaused = True
            #fi

            mySchedulerConfig = self.Utility.getACopy(self.Infra.schedulerConfigData)

            if self.mySchedulerType == 'Background':
                self.Scheduler = BackgroundScheduler(mySchedulerConfig)
            else:
                self.Scheduler = BlockingScheduler(mySchedulerConfig)

            self.Scheduler.start(paused=argPaused)
            
            # adding listener for scheduler/job
            self.Scheduler.add_listener(self.schedulerListener, events.EVENT_ALL)

        except Exception as err:
            raise err

    def stopScheduler(self):

        if self.Scheduler.running:
            self.logger.info('stopping scheduler')
            self.Scheduler.shutdown()
        else:
            self.logger.warning('scheduler is not running')


    def processJob(**keyWordArgs):
        '''
            1. Validating the argument using schema
            2. Update job "Executing"
            3. Execute Job
            4. Update Job Status "Completed"
        '''
        from com.port8.core.globals import Global
        from com.port8.core.utils import Utility
        from com.port8.core.infrautils import InfraUtility
        from com.port8.core.validation import Validation
        from com.port8.core.schedutility import SchedUtility

        import os, json, sys, time, inspect

        try:
            Global = Global()
            InfraUtil = InfraUtility()
            Utility = Utility()
            Validation = Validation()
            ShcedUtil = SchedUtility()

            Infra = ShcedUtil.InfraUtil.setInfra('Scheduler')

            logger = Infra.getInfraLogger('Scheduler')
            myProcessJobSchema = Infra.jsonSchema['Main']['process_job_schema']
            logger.debug('Job Schema will be used for validation >> {schema}'.format(schema= myProcessJobSchema))  

            myKeyWordArgs = Utility.getACopy(keyWordArgs)
            myCurrentTime = time.time()
            myResponse = Utility.getResponseTemplate()
            logger.debug('argument received >> {args}'.format(args=myKeyWordArgs))

            #validating argumnet (using json schema validator)
            Validation.validateArguments(myKeyWordArgs, myProcessJobSchema)
            logger.debug('arguments validated >>'.format(args = myKeyWordArgs ))

            # building data for this run & persisiting data
            myJobCriteria = ' JobId = ' + repr(myKeyWordArgs['jobid'])

            myStartEventResult = ShcedUtil.processJobStartEvent(myKeyWordArgs['jobid'])

            #executing job
            logger.info('Executing .... : {arg}'.format(arg = myKeyWordArgs))
            
            myResult = InfraUtil.callFunc(**myKeyWordArgs['func_call'])
            myResult['Data'].update({'ElapsedSecs' : round(time.time() - myCurrentTime,5)})
            
            logger.info('jobid {jobid} execution results: {result}'.format(jobid = myKeyWordArgs['jobid'], result=myResult))

            myFinishEventResult = ShcedUtil.processJobFinishEvent(myKeyWordArgs['jobid'], myResult)
            
            if myResult['Status'] == Global.Success:
                # calling job completed event
                if myFinishEventResult['Status'] == Global.Success:
                    Utility.buildResponse(myResponse, Global.Success, Global.Success, {'result':myFinishEventResult} )
                else:
                    raise processJobError('Error returned from calling job finish event {error}'.format(error=myFinishEventResult['Message']))
            else:
                raise processJobError('Error returned from job processing {error}'.format(error=myResult['Message']))

            #building response

            return myResponse

        except Exception as err:
            # log the error and let the error to be raised to scheduler to ensure we have error being reported back to scheduler

            myErrorMsg, myTraceback = Utility.getErrorTraceback()
            logger.error(Global.DefPrefix4Error * Global.DefPrefixCount , myErrorMsg)
            logger.error(Global.DefPrefix4Error * Global.DefPrefixCount , myTraceback)
            Utility.buildResponse(myResponse, Global.UnSuccess,myErrorMsg)

            if 'myCurrentTime' in locals():
                myElapsedSecs = round(time.time() - myCurrentTime,5)
            else:
                myElapsedSecs = round(time.time() - myCurrentTime,5)

            myResponse['Data'].update({'ElapsedSecs' : myElapsedSecs})
            myDbResult = ShcedUtil.processJobFinishEvent(myKeyWordArgs['jobid'], myResponse)

            raise err

    def scheduleIntervalJob(self):
        pass

    def buildCronTrigger(self, scheduleArg):
        try:
            return CronTrigger(**scheduleArg)
        except Exception as err:
            myErrorMessage = sys.exc_info()[1:]
            self.logger.error('Error {error} in building CronTrigger using {data} '.format(error= myErrorMessage, data=scheduleArg))
            raise err

    def buildCoalesce(self, coalesceArg):
        if coalesceArg == None:
            return True
        else:
            return coalesceArg
        #fi

    def scheduleJob(self, **keyWordArgs):
        '''
        This is for cron based scheduler
        '''
        try:
            #initializing
            myKeyWordArgs = self.Utility.getACopy(keyWordArgs)
            myResponse = self.Utility.getResponseTemplate()
            myProcessKeyWordArg = {}
            myData = ''
            myJobId = shcedUtil.getNewJob(self.Global.JobIdPrefixValue)

            #validating argumnet (using json schema validator)
            self.Validation.validateArguments(myKeyWordArgs, self.scheduleSchema)
            self.logger.debug('arguments {args} validated'.format(args = myKeyWordArgs ))

            # building job arguments
            myCoalesce = self.buildCoalesce(myKeyWordArgs['coalesce'])

            myProcessJobKeyArg = {
                'func_call': {
                    'module': myKeyWordArgs['func_call']['module'],
                    'cls':myKeyWordArgs['func_call']['cls'],
                    'clsArg':myKeyWordArgs['func_call']['clsArg'],
                    'method': myKeyWordArgs['func_call']['method'],
                    'methodArgType' : myKeyWordArgs['func_call']['methodArgType'],
                    'arguments': myKeyWordArgs['func_call']['arguments']
                }
            }

            myProcessJobKeyArg.update({'jobid':myJobId})
            myCronTrigger = self.buildCronTrigger(myKeyWordArgs['schedule'])            

            myJob = self.Scheduler.add_job(self.processJob, trigger = myCronTrigger, replace_existing=True, id = myJobId, jobstore = 'default', coalesce = myKeyWordArgs['coalesce'], kwargs=myProcessJobKeyArg)

            myJobDetails = {
                'id':str(myJob.id), 'name':str(myJob.name), 'kwargs':myJob.kwargs, 'trigger' : str(myJob.trigger.fields), 'func_ref':str(myJob.func_ref)
            }

            myCurrentTime = self.Utility.getCurrentTime()
            myResult = self.db.processDbRequest(operation = 'create', container = 'ScheduledJobs',\
                 dataDict = {
                    'JobId':myJob.id, 'JobName':myJob.name, 'JobTrigger': str(myJob.trigger), 'NextRun' : myJob.next_run_time,
                    'JobFunction' : myJob.func_ref, 'SubmittedBy':'test', 'SubmitDate':self.Utility.getCurrentTime(), 'Status':'Submitted',
                    'JobDetails':json.dumps(myJobDetails)}, commitWork = True)

            print('job persist result',myResult)

            if self.Utility.extractStatusFromResult(myResult) == self.Global.Success:
                self.Utility.buildResponse(myResponse, self.Global.Success,self.Global.Success, {'Job':myJobDetails} )
            else:
                self.Utility.buildResponse(myResponse, self.Global.UnSuccess,'Job has been submitted but could not persist data in database', {'Job':myJobDetails} )
            #fi                

        except Exception as err:
            myMessage = sys.exc_info()[1:],traceback.format_exc(limit=1)
            self.Utility.buildResponse(myResponse, self.Global.UnSuccess,myMessage)
            raise err

    def schedulerListener(self, eventArg):
        '''
        Description:
            This is internal method to handle all the event associated to scheduler via listener, will persist the event details in db. 
            This will be called internally
        '''
        if eventArg.code == events.EVENT_SCHEDULER_STARTED:
            #self.logger.info('EVENT: Scheduler statrted, event code {code}'.format(code=eventArg.code))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'SCHEDULER_STARTED'}, commitWork = True)
        elif eventArg.code == events.EVENT_SCHEDULER_SHUTDOWN:
            #self.logger.info('EVENT: Scheduler shutdown, event code {code}'.format(code=eventArg.code))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'SCHEDULER_SHUTDOWN'}, commitWork = True)
        elif eventArg.code == events.EVENT_SCHEDULER_PAUSED:
            #self.logger.info('EVENT: Scheduler paused, event code {code}'.format(code=eventArg.code))
            self.db.persistData(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'SCHEDULER_PAUSED'}, commitWork = True)
        elif eventArg.code == events.EVENT_SCHEDULER_RESUMED:
            #self.logger.info('EVENT: Scheduler resumed, event code {code}'.format(code=eventArg.code))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'SCHEDULER_RESUMED'}, commitWork = True)
        elif eventArg.code == events.EVENT_EXECUTOR_ADDED:
            self.logger.info('EVENT: Executor added, event code {code}'.format(code=eventArg.code))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'EXECUTOR_ADDED'}, commitWork = True)
        elif eventArg.code == events.EVENT_EXECUTOR_REMOVED:
            self.logger.info('EVENT: Executor removed, event code {code}'.format(code=eventArg.code))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'EXECUTOR_REMOVED'}, commitWork = True)
        elif eventArg.code == events.EVENT_JOBSTORE_ADDED:
            self.logger.info('EVENT: JobStore Added, event code {code}'.format(code=eventArg.code))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'JOBSTORE_ADDED'}, commitWork = True)
        elif eventArg.code == events.EVENT_JOBSTORE_REMOVED:
            self.logger.info('EVENT: Jobstore removed, event code {code}'.format(code=eventArg.code))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'JOBSTORE_REMOVED'}, commitWork = True)
        elif eventArg.code == events.EVENT_ALL_JOBS_REMOVED:
            self.logger.info('EVENT: All jobs removed, event code {code}'.format(code=eventArg.code))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', dataDict = {'EventName':'ALL_JOBS_REMOVED'}, commitWork = True)
        elif eventArg.code == events.EVENT_JOB_ADDED:
            #myJobId = eventArg.job_id
            #self.logger.info('EVENT: Job added, job detail >>> {job}, {jobstore}'.format(job=eventArg.job_id, jobstore = eventArg.jobstore))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', \
                dataDict = {'EventName':'JOB_ADDED', 'EventDetails':json.dumps({'JobId':eventArg.job_id}) }, commitWork = True)
        elif eventArg.code == events.EVENT_JOB_REMOVED:
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', \
                dataDict = {'EventName':'JOB_REMOVED', 'EventDetails':json.dumps({'JobId':eventArg.job_id}) }, commitWork = True)
        elif eventArg.code == events.EVENT_JOB_MODIFIED:
            #self.logger.info('EVENT: Job modified, job detail >>> {job}, {jobstore}'.format(job=eventArg.job_id, jobstore = eventArg.jobstore))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', \
                dataDict = {'EventName':'JOB_MODIFIED', 'EventDetails':json.dumps({'JobId':eventArg.job_id}) }, commitWork = True)
        elif eventArg.code == events.EVENT_JOB_EXECUTED:
            self.logger.info('EVENT: Job executed {event_code}, {job_id}, {job_store}, {sched_run_time}, {job_retval}, {error}, {traceback}'.\
                format(event_code=eventArg.code, job_id = eventArg.job_id, job_store = eventArg.jobstore, sched_run_time = eventArg.scheduled_run_time,\
                       job_retval = eventArg.retval, traceback = eventArg.traceback))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', \
                dataDict = {'EventName':'JOB EXECUTED', 'EventDetails': json.dumps({'job_id':eventArg.job_id,'sched_run_time':str(eventArg.scheduled_run_time),\
                            'job_retval': str(eventArg.retval),'traceback' : str(eventArg.traceback) })}, commitWork=True)
        elif eventArg.code == events.EVENT_JOB_ERROR:
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog', \
                dataDict = {'EventName':'JOB ERROR', 'EventDetails': json.dumps({'job_id':eventArg.job_id,'sched_run_time':str(eventArg.scheduled_run_time),\
                            'job_retval': str(eventArg.retval),'traceback' : str(eventArg.traceback)})}, commitWork=True)
        elif eventArg.code == events.EVENT_JOB_MISSED:
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog',\
                dataDict = {'EventName':'JOB MISSED', 'EventDetails': json.dumps({'job_id':eventArg.job_id})}, commitWork=True)
        elif eventArg.code == events.EVENT_JOB_SUBMITTED:
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog',\
                dataDict = {'EventName':'JOB_SUBMITTED', 'EventDetails': json.dumps({'job_id':eventArg.job_id})})
        elif eventArg.code == events.EVENT_JOB_MAX_INSTANCES:
            #self.logger.info('EVENT: Job maxinstance, job detail >>> {job}, {jobstore}'.format(job=eventArg.job_id, jobstore = eventArg.jobstore))
            self.db.processDbRequest(operation = 'create', container = 'SchedulerEventLog',\
                dataDict = {'EventName':'JOB_MAX_INSTANCES', 'EventDetails': json.dumps({'job_id':eventArg.job_id})})
        #fi

    def syncJobFromRepository():
        pass

'''
if __name__ == "__main__":
    
    schedule = Scheduler()
    #schedule.scheduleCronJob()
    schedule.scheduler.add_job(schedule.processJob, 'interval', seconds=10, replace_existing=True)
    schedule.scheduler.print_jobs()
 |  add_job(self, func, trigger=None, args=None, kwargs=None, id=None, name=None, misfire_grace_time=<undefined>, coalesce=<undefined>, max_instances=<undefined>, next_run_time=<undefined>, jobstore='default', executor='default', replace_existing=False, **trigger_args)
 |      add_job(func, trigger=None, args=None, kwargs=None, id=None,             name=None, misfire_grace_time=undefined, coalesce=undefined,             max_instances=undefined, next_run_time=undefined,             jobstore='default', executor='default',             replace_existing=False, **trigger_args)

'''

# format schedule argument (when this process to be run)
'''
run immediately, omit trigger
trigger: 
    date:  run_date=datetime(2009, 11, 6, 16, 30, 5) # (YYYY, MM, DD, HH, MI, SS)
    interval: (if start_date is in past, next scheduler will be caluclated from current time)
        Args:
            weeks/days/hours/minutes/seconds: (number of weeks/days/hours/minutes/seconds to wait)
            start_date
            end_date
            time_zone: to use for datetime calculation
        Example:
            sched.add_job(job_function, 'interval', hours=2, start_date='2010-10-10 09:30:00', end_date='2014-06-15 11:00:00') # every 2 hours
    cron:
        Parameters: 

            year        (int|str)               – 4-digit year
            month       (int|str)               – month (1-12)
            day         (int|str)               – day of the (1-31)
            week        (int|str)               – ISO week (1-53)
            day_of_week (int|str)               – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
            hour        (int|str)               – hour (0-23)
            minute      (int|str)               – minute (0-59)
            second      (int|str)               – second (0-59)
            start_date  (datetime|str)          – earliest possible date/time to trigger on (inclusive)
            end_date    (datetime|str)          – latest possible date/time to trigger on (inclusive)
            timezone    (datetime.tzinfo|str)   – time zone to use for the date/time calculations (defaults to scheduler timezone)

        Expression  Field   Description
        *       any     Fire on every value
        */a     any     Fire every a values, starting from the minimum
        a-b     any     Fire on any value within the a-b range (a must be smaller than b)
        a-b/c   any     Fire every c values within the a-b range
        xth y   day     Fire on the x -th occurrence of weekday y within the month
        last x  day     Fire on the last occurrence of weekday x within the month
        last    day     Fire on the last day within the month
        x,y,z   any     Fire on any matching expression; can combine any number of any of the above expressions

        sched.add_job(job_function, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')

        # Schedules job_function to be run on the third Friday of June, July, August, November and December at 00:00, 01:00, 02:00 and 03:00
        sched.add_job(job_function, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')                    
        sched.add_job(job_function, 'cron', month='6-8,11-12', day='last sun', hour='0-3')                    

        # Runs from Monday to Friday at 5:30 (am) until 2014-05-30 00:00:00
        sched.add_job(job_function, 'cron', day_of_week='mon-fri', hour=5, minute=30, end_date='2014-05-30')

        scheduler.add_job(self.refresh_registered, CronTrigger(second='*/5'))
        scheduler.add_job(self.refresh_unregistered, CronTrigger(second='*/60'))
        scheduler.add_job(self.connect, CronTrigger(second='*/5'))
        scheduler.start()
        
        https://programtalk.com/vs2/python/4353/Flexget/flexget/plugins/daemon/scheduler.py/
'''
