from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utils import Utility
from com.port8.core.error import *
from com.port8.core.infrautils import InfraUtility
from com.port8.db.dbmysql import DBMySql

import os, sys, time, random, datetime, json

class SchedUtility(object, metaclass=Singleton):
    
    def __init__(self):
        try:
            self.Global = Global()
            self.Utility = Utility()
            self.InfraUtil = InfraUtility()
            self.db = DBMySql('Scheduler')

            self.myModulePyFile = os.path.abspath(__file__)
            self.myClass = self.__class__.__name__

            #Setting the infrastructure
            self.Infra = self.InfraUtil.setInfra(self.Global.SchedulerInfraKey)
            if not self.Infra:
                raise InfraInitializationError('Could not initialize {cls}'.format(cls=(self.myModulePyFile,self.myClass)))

            # we need to get the proper logger for a given module
            self.logger = self.Infra.getInfraLogger(self.Global.SchedulerInfraKey)

            # loading Schduler config and starting scheduler
            self.__startScheduler__()

        except Exception as err:
            raise err

    def __startScheduler__(self):

        try:
            mySchedulerType = self.Global.DefaultSchedulerType
            mySchedulerMode = self.Global.DefaultSchedulerMode

            if mySchedulerMode == 'Run':
                myArgPaused = False
            else:
                myArgPaused = True
            #fi

            mySchedulerConfig = self.Utility.getACopy(self.Infra.schedulerConfigData)

            if mySchedulerType == 'Background':
                self.Scheduler = BackgroundScheduler(mySchedulerConfig)
            else:
                self.Scheduler = BlockingScheduler(mySchedulerConfig)
            #fi

            if not self.Scheduler.running:
                self.Scheduler.start(paused = myArgPaused)

        except Exception as err:
            raise err

    def getAllJobDetail(self):
        '''
        Description: Returns all jobs as stored in scheduler
        '''
        myJobDetail = []
        
        for job in self.Scheduler.get_jobs():
            myJobDetail.append(self.getAJobDetail(job.id))

        return myJobDetail

    def getAJobDetail(self, jobIdArg):
        '''
        Description: Print all jobs as stored in scheduler
        '''
        myJobId = jobIdArg
        job = self.Scheduler.get_job(myJobId)
        myJobDetail = job.__getstate__()

        return myJobDetail

    def suspendJob(self, jobIdArg):
        myJobId = jobIdArg
        job = self.Scheduler.get_job(myJobId)
        job.pause()

    def resumeJob(self, jobIdArg):
        myJobId = jobIdArg
        job = self.Scheduler.get_job(myJobId)
        job.resume()

    def getCurrentlyExecutingJob(self):
        return len(self.Scheduler.get_jobs())

    def removeJob(self, jobId):
        try:
            self.Scheduler.remove_job(jobId)
        except JobLookupError as err:
            print('Invalid Job !!')

    def removeAllJobs(self):
        try:
            self.Scheduler.remove_all_jobs()
        except Exception as err:
            raise err

    def getAllJobsFromRep(self):
        for job in self.Scheduler.get_jobs():
            myJobDetail = self.Scheduler.get_job(job.id)    
            print(job,myJobDetail)

    def getNewJob(self,prefixArg):
        # random number between 10 and 99 to ensure we always get 2 digit
        if isinstance(prefixArg,str) and prefixArg is not None:
            return prefixArg + '_' + str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%-H%M%S_') + str(random.randrange(10,99)))
        else:
            return datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%-H%M%S_') + str(random.randrange(10,99))

    def getJobInfoFromDb(self, jobIdArg):
        try:
            myResponse = self.Utility.getResponseTemplate()
            myJobId = self.Utility.getACopy(jobIdArg)
            self.logger.debug('arg [{arg}] received'.format(arg = myJobId))

            myJobCriteria = 'JobId = %s ' %repr(myJobId)
            return self.db.processDbRequest(operation = self.Global.fetch, container = 'ScheduledJobs', contents = ['*'], criteria = myJobCriteria)

        except Exception as err:
            myErrorMsg, myTraceback = self.Utility.getErrorTraceback()
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myErrorMsg)
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myTraceback)
            self.Utility.buildResponse(myResponse, self.Global.UnSuccess,myErrorMsg)
            return myResponse

    def getNextSeqForJob(self, jobIdArg):
        try:
            myResponse = self.Utility.getResponseTemplate()
            myJobId = self.Utility.getACopy(jobIdArg)
            self.logger.debug('arg [{arg}] received'.format(arg = myJobId))

            myJobCriteria = 'JobId = %s ' %repr(myJobId)
            return self.db.getTotalRowCount(container = 'ScheduledJobsRunLog', criteria = myJobCriteria) + 1

        except Exception as err:
            myErrorMsg, myTraceback = self.Utility.getErrorTraceback()
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myErrorMsg)
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myTraceback)
            return myErrorMsg

    def getCurrentSeqForJob(self, jobIdArg):
        try:
            myResponse = self.Utility.getResponseTemplate()
            myJobId = self.Utility.getACopy(jobIdArg)
            self.logger.debug('arg [{arg}] received'.format(arg = myJobId))

            myJobCriteria = 'JobId = %s ' %repr(myJobId)
            return self.db.getTotalRowCount(container = 'ScheduledJobsRunLog', criteria = myJobCriteria)

        except Exception as err:
            myErrorMsg, myTraceback = self.Utility.getErrorTraceback()
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myErrorMsg)
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myTraceback)
            return myErrorMsg

    def getElapsedStatsForJob(self, jobIdArg):
        try:
            myResponse = self.Utility.getResponseTemplate()
            myJobId = self.Utility.getACopy(jobIdArg)
            self.logger.debug('arg [{arg}] received'.format(arg = myJobId))

            myJobCriteria = 'JobId = %s ' %repr(myJobId)
            return self.db.getTotalRowCount(container = 'ScheduledJobsRunLog', criteria = myJobCriteria)

        except Exception as err:
            myErrorMsg, myTraceback = self.Utility.getErrorTraceback()
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myErrorMsg)
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myTraceback)
            return myErrorMsg

    def processJobStartEvent(self, jobIdArg):
        '''
        1. Mark job started in ScheduledJobs
        2. Create new entry for this job in ScheduledJobsRunLog
        '''
        try:
            # initializing
            myResponse = self.Utility.getResponseTemplate()
            myJobId = self.Utility.getACopy(jobIdArg)
            self.logger.debug('arg [{arg}] received'.format(arg=myJobId))

            myJobDetailsFromDb = self.getJobInfoFromDb(myJobId)['Data']

            if myJobDetailsFromDb:

                # building data for SchedulerJobsRunLog
                myJobCriteria = ' JobId = %s' %repr(myJobId)
                myNextSeqForJob = self.getNextSeqForJob(myJobId)

                # will mark the job started and creat the run log for this run
                self.db.processDbRequest(operation='change', container='ScheduledJobs', \
                    dataDict={'Status': 'Executing'}, criteria = myJobCriteria, commitWork=True )
                
                # creating run information
                self.db.processDbRequest(operation='create', container='ScheduledJobsRunLog', \
                        dataDict={'JobId':myJobId, 'Seq' : myNextSeqForJob,  'ExecutionStarted': self.Utility.getCurrentTime()}, commitWork=True )

                self.Utility.buildResponse(myResponse, self.Global.Success, self.Global.Success, {'Seq':myNextSeqForJob})
            else:
                self.Utility.buildResponse(myResponse, self.Global.UnSuccess, 'Cound not find job details for job {job}'.format(job = myJobId))

            return myResponse

        except Exception as err:
            myErrorMsg, myTraceback = self.Utility.getErrorTraceback()
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myErrorMsg)
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myTraceback)
            self.Utility.buildResponse(myResponse, self.Global.UnSuccess,myErrorMsg)
            #raise err # will raise the error so this can be logged by scheduler as an error occurred in processing job
            return myResponse

    def processJobFinishEvent(self, jobIdArg, execDetailsArg):
        '''
        1. Mark job completed (update failure cnt and total count and consc fail count, lastrunstatus) in ScheduledJobs
        2. Update ScheduledJobsRunlog container
        '''
        try:
            # initializing
            myResponse = self.Utility.getResponseTemplate()
            myJobId = self.Utility.getACopy(jobIdArg)
            myExecDetails = execDetailsArg
            myJobStatus = self.Global.NextJobRun
            
            self.logger.debug('arg [{arg}] received'.format(arg=myJobId))

            myJobDetailsFromDb = self.getJobInfoFromDb(myJobId)['Data']

            if myJobDetailsFromDb:

                self.logger.debug('Job details found, proceeding with finish event')
                myJobCriteria = 'JobId = %s' %repr(myJobId)
                myCurrentSeqForJob = self.getCurrentSeqForJob(myJobId)
                myJobRunCriteria = ' JobId = %s and Seq = %s ' %(repr(myJobId), myCurrentSeqForJob)

                self.logger.debug('Job criteria {criteria}'.format(criteria = myJobCriteria))
                self.logger.debug('Job criteria with seq {criteria}'.format(criteria = myJobRunCriteria))

                myJobDetailsFromSched = self.getAJobDetail(myJobId)

                # Updating execution details in ScheduledJobsRunLog
                self.logger.debug('udating statistics of this run')

                myDbResult = self.db.processDbRequest(operation = 'change', container = 'ScheduledJobsRunLog', \
                    dataDict={
                        'Status': myExecDetails['Status'], 'ElapsedSeconds':myExecDetails['Data']['ElapsedSecs'],
                        'ExecutionCompleted': self.Utility.getCurrentTime(), 'ExecutionDetail': json.dumps(myExecDetails['Data']) 
                    }, criteria = myJobRunCriteria, commitWork=True )

                self.logger.debug('ScheduledJobsRunLog: db results >> {results}'.format(results = myDbResult))

                # Updating execution details in ScheduledJobs
                #if myExecDetails['Status'] == self.Global.Success:
                    # if success, reset consecfailcnt to 0, increment totalrun by 1 and update next run
                myElapsedStats = self.db.executeDynamicSql(\
                    operation = 'fetch', \
                    sql_text = 'select min(ElapsedSeconds) "Min", max(ElapsedSeconds) "Max", avg(ElapsedSeconds) "Avg" from ScheduledJobsRunLog')

                self.logger.debug('Elapsed Stats: {stats}'.format(stats = myElapsedStats))

                myDbResult = self.db.processDbRequest(operation='change', container='ScheduledJobs', \
                    dataDict={
                        'Status': myJobStatus, 'LastRunStatus': myExecDetails['Status'], 'TotalRun' : myJobDetailsFromDb[0]['TotalRun'] + 1,
                        'NextRun' : myJobDetailsFromSched['next_run_time'].strftime('%Y-%m-%d% %H:%M:%S'), 'LatConsecFailCnt' : 0,
                        'MinElapsedSecs' : myElapsedStats['Data'][0]['Min'], 'MaxElapsedSecs' : myElapsedStats['Data'][0]['Min'] , 
                        'AvgElapsedSecs' : myElapsedStats['Data'][0]['Avg']  
                    }, criteria = myJobCriteria, commitWork=True )

                self.logger.debug('ScheduledJobs: last stats update >> {result}'.format(result = myDbResult))

                #self.Utility.buildResponse(myResponse, self.Global.Success,self.Global.Success)
                '''
                else:
                    # process job was unsuccessful
                    if myJobDetailsFromDb[0]['LatConsecFailCnt'] >= self.Global.SchedConsecFailCntThreshold:
                        myJobStatus = self.Global.SuspendMode
                        self.logger.info('suspending job {job}'.format(job=myJobId))
                        self.suspendJob(myJobId)

                    myDbResult = self.db.processDbRequest(operation='change', container='ScheduledJobs', \
                        dataDict={
                            'Status': myJobStatus, 'LastRunStatus': myExecDetails['Status'], 'TotalRun' : myJobDetailsFromDb[0]['TotalRun'] + 1,
                            'next_run' : myJobDetailsFromSched['next_run_time'], 'LatConsecFailCnt' : myJobDetailsFromDb[0]['LatConsecFailCnt'] + 1, 
                            'TotalFailure' :  myJobDetailsFromDb[0]['TotalFailure' + 1]
                        }, criteria = myJobCriteria, commitWork=True )
                    # will suspend the job if total failure count has been reached beyond Total consecutive failure threshold
                    self.Utility.buildResponse(myResponse, self.Global.UnSuccess,self.Global.UnSuccess)
                    raise processJobError(myExecDetails['Message'])
                '''
            self.Utility.buildResponse(myResponse, self.Global.Success,self.Global.Success)
            return myResponse
        except Exception as err:
            myErrorMsg, myTraceback = self.Utility.getErrorTraceback()
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myErrorMsg)
            self.logger.error(self.Global.DefPrefix4Error * self.Global.DefPrefixCount , myTraceback)
            self.Utility.buildResponse(myResponse, self.Global.UnSuccess, myErrorMsg)
            return myResponse