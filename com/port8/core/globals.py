from com.port8.core.singleton import Singleton

class Global(object, metaclass=Singleton):
    def __init__(self):
        #
        self.InitFile="init.json"
        self.InitKeys=('APP_NAME','APP_HOME','APP_LOG','APP_CONFIG','BOOTSTRAP_FILE',"VALIDATE_DIR_LIST","VALIDATE_FILE_LIST")
        self.BootStrapKey='bootStrapCfg'
        self.BootStrapFileKey='BOOTSTRAP_FILE'
        self.LogLocKey="LOG_LOC"

        #Infrastructure
        self.InfraLib = 'com.port8.core.infrastructure'
        self.Infrastructure = {'Rest':'RestInfra','Scheduler':'SchedInfra','Daemon':'DaemonInfra'}
        self.RestApiInfraKey = 'Rest'
        self.SchedulerInfraKey = 'Scheduler'
        self.DaemonInfraKey = 'Daemon'

        # error
        self.DefPrefix4Error = '  >'
        self.DefPrefixCount = 3

        #db'
        '''
        self.DBRequiredArg = \
            {'Create':['operation','container','dataDict','commitWork'],
             'Change':['operation','container','criteria','dataDict','commitWork'],
             'Remove':['operation','container','criteria','commitWork']
            }
        self.DBOperations = ['create','change','remove','get']
        '''
        self.create = 'create'
        self.change = 'change'
        self.remove = 'remove'
        self.fetch = 'fetch'
        self.allDbOperation=[self.create, self.change, self.remove, self.fetch]
        self.container = 'container'
        self.mySqlVarHolder = '%s '
        self.ChkContainerExistSql = "select table_name from information_schema.tables where table_name = %s "
        self.commitWorkDefaultValue = True
        self.defaultError4Number = '-1'
        self.defaultCriteria = ' 1 = 1 '

        #logging
        self.LoggingConfig = 'loggingConfig.json'
        self.RestInfra = 'REST'
        self.SchedInfra = 'SCHEDULER'
        self.DaemonInfra = 'DAEMON'
        self.DefaultInfra = 'DEFAULT'
        self.LoggerName = \
         {
            "REST":{"Name":"Rest","LogFile":"restApiPort8.log"},
            "SCHEDULER":{"Name":"apscheduler","LogFile":"schedulerPort8.log"},
            "DAEMON":{"Name":"Daemon","LogFile":"daemonPort8.log"},
            "DEFAULT":{"Name":"Console","LogFile":""}            
        }

        #Scheduler
        self.ScheduleConfig = 'schedulerConfig.json'
        self.Schedulers = ['Blocking','Background']
        self.CurrentScheduler = 'Blocking'
        self.SchedulerMode = ['Run','Maintenance']
        self.JobIdPrefixValue = 'port8'
        self.SchedConsecFailCntThreshold = 3
        self.NextJobRun = 'Waiting for next run'
        self.SuspendMode = 'Suspended'
        self.DefaultSchedulerType ='Background'
        self.DefaultSchedulerMode ='Maintenance'

        #template
        self.Template = \
            {
                "Response":{'Status':'','Data':{},'Message':''},
                "DBResponse" : {"Status" : '', "Rows" : 0, "Message" : "", "Data" : "" },
                "ArgValResult" : {"Status" : '', "Message" : '', "Arguments" : {}, "MissingArg" : []},
                "ScanSummaryData" : {
                    "AvgScore" : 0, 
                    "LocAvgScore" : [], 
                    "HostScore" : [], 
                    "HostTenantScore" : [], 
                    "TenantScore" : {}, 
                    "LocTenAvgScore" : {}}
            }
        self.ResponseTemplate = 'Response'
        self.Success = 'Success'
        self.UnSuccess = 'UnSuccess'        
        self.Error = 'Error'
        self.SqlOutput = {'Default' : 'Tuple', 'Dict' : 'Dict','All':['Tuple','Dict']}
        self.Response = {'Status':'','Data': {},'Message':''}

        #misc
        self.ResponseModeList = ['I','E']        
        self.keyword = 'keyword'
        self.positional = 'positional'

        self.matchAll = 'ALL'
        self.keyPosSTARTWITH = 'STARTWITH'
        self.keyPosANYWHERE = 'ANYWHERE'

        ## MYSQL Sql
        self.avgScoreSql = 'select avg(last_scan_score) "AVG_SCORE" \
            from p$ht_info '

        self.locAvgScoreSql = 'select IFNULL(dc_info,\'UNDEFINED\') "LOCATION", avg(last_scan_score) "AVG_SCORE" \
            from p$ht_info \
            group by dc_info '

        self.hostScoreSql = 'select host_name "HOST", dc_info "LOCATION", last_scan_score "AVG_SCORE", last_scan_id "LAST_SCAN", last_scan_time "LAST_SCAN_TIME" \
            from p$ht_info '

        self.vendorProdAvgScoreSql = 'select tenant_vendor "VENDOR", vendor_prod_name "PRODUCT", avg(last_scan_score) "AVG_SCORE" \
            from p$ht_tenant \
            group by tenant_vendor, vendor_prod_name \
            order by tenant_vendor, vendor_prod_name'

        self.hostTenantScoreSql = 'select host_name "HOST", tenant_type "TENANT_TYPE", tenant_name "TENANT_NAME", last_scan_score "AVG_SCORE", last_scan_id "LAST_SCAN", last_scan_time "LAST_ScAN_TIME" \
            from p$ht_tenant \
            order by host_name,tenant_type, tenant_name '

        self.locVendorAvgScoreSql = 'select host.dc_info "LOCATION", tenant.tenant_vendor "VENDOR", tenant.vendor_prod_name "PRODUCT", avg(tenant.last_scan_score) "AVG_SCORE" \
            from p$ht_tenant tenant, p$ht_info host \
            where host.host_id = tenant.host_id \
            group by host.dc_info, tenant.tenant_vendor, tenant.vendor_prod_name \
            order by host.dc_info, tenant.tenant_vendor, tenant.vendor_prod_name '

        self.getLastTenantScanSql = 'select last_scan_id "SCAN_ID", last_scan_seq_id "SEQ_ID" from p$ht_tenant where tenant_id = %(TenantId)s'
        self.getTenantScanSummarySql = 'select * from p$ht_tenant_scan where tenant_id = %(TenantId)s and scan_id = %(ScanId)s and scan_seq_id = %(ScanSeqId)s'
        self.getTenantScanDetailSql = 'select * from p$ht_tenant_scan_detail where tenant_id = %(TenantId)s and scan_id = %(ScanId)s and scan_seq_id = %(ScanSeqId)s'

        self.allTenantAvgScore4HostSql = 'select tenant_vendor "VENDOR", vendor_prod_name "PRODUCT", avg(last_scan_score) "AVG_SCORE" \
            from p$ht_tenant \
            where host_id = %(HostId)s \
            group by tenant_vendor, vendor_prod_name'

        self.allTenantScore4VendorSql = 'select host_id "HOST_ID", vendor_prod_name "VENDOR_PRODUCT", tenant_type "TENANT_TYPE", tenant_name "TENANT", last_scan_score "SCORE" \
            from p$ht_tenant \
            where tenant_vendor = %(TenantVendor)s'

        self.allVedorProdTenantScoreSql = 'select host_id "HOST_ID", tenant_type "TENANT_TYPE", tenant_name "TENANT", last_scan_score "SCORE" \
            from p$ht_tenant \
            where tenant_vendor = %(TenantVendor)s and vendor_prod_name = %(VendorProduct)s'

    #def __call__(self):
    #    print('Call is prohibited')
