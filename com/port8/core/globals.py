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

        #Rest
        self.InternalRequest='I'
        self.ExternalRequest='E'
        self.RequestStatus={'Status' : '', 'Message' : ''}
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
                "Response":{'Status':'','Message': '', 'Data':[]},
                "Request" : {"Page":"","Action" : "","Arguments" : ""},
                "DBResponse" : {"Status" : '', "Rows" : 0, "Message" : "", "Data" : [] },
                "ArgValResult" : {"Status" : '', "Message" : '', "Arguments" : {}, "MissingArg" : []},
                "LandingPage" : {
                    "AvgScore" : 0, 
                    "Location" : [],
                    "Vendor" : [],
                    "LocVendor" : [], 
                    "LocHost" : [],
                    "LocHostTenant" : []
                }                   
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

        ## Factory Call
        self.buildFactoryDataSql = \
            'select page.page_id "PAGE_ID", page.page_name "PAGE_NAME", page.page_status "PAGE_STATUS", \
                action.action_id "ACTION_ID", action.action_name "ACTION_NAME", action.action_status "ACTION_STATUS", action.bpm_status "BPM_STATUS", action.bpm_call_json "BPM_CALL_JSON"\
            from p$ui_page page, p$ui_action action  \
            where page.page_id = action.page_id \
            order by action.page_id, action.action_id'
        ##
        self.avgScoreSql = 'select avg(last_scan_score) "AVG_SCORE" \
            from p$ht_info '

        self.getAllLocAvgScoreSql = 'select IFNULL(dc_info,\'UNDEFINED\') "LOCATION", avg(last_scan_score) "AVG_SCORE" \
            from p$ht_info \
            group by dc_info '

        self.getALocAvgScoreSql = 'select IFNULL(dc_info,\'UNDEFINED\') "LOCATION", avg(last_scan_score) "AVG_SCORE" \
            from p$ht_info \
            where dc_info = %(Location)s \
            group by dc_info '

        self.getHostInfoSql = 'select host.host_id"HOST_ID", host.host_name "HOST", \
                host.location "PHYSICAL_LOC", host.dc_info "LOCATION", \
                host.os "OS", host.os_version "OSVersion", host.os_release "OS_RELEASE", host.processor "PROCESSOR", \
                host.phys_memory_mb "PHYSICAL_MEMORY_MB", host.swap_memory_mb "SWAP_MEMORY_MB", \
                host.ip_addresses "IP_ADDRESSES", \
                host.last_scan_score "AVG_SCORE", host.last_scan_id "LAST_SCAN", host.last_scan_time "LAST_SCAN_TIME" \
            from p$ht_info host'

        self.getAllHostScoreSql = 'select host.host_id"HOST_ID", host_name "HOST", dc_info "LOCATION", last_scan_score "AVG_SCORE", last_scan_id "LAST_SCAN", last_scan_time "LAST_SCAN_TIME" \
            from p$ht_info host'

        self.getAHostScoreSql = 'select host.host_id "HOST_ID", host.host_name "HOST", host.dc_info "LOCATION", host.last_scan_score "AVG_SCORE", host.last_scan_id "LAST_SCAN", host.last_scan_time "LAST_SCAN_TIME" \
            from p$ht_info host \
            where host.host_id = %(HostId)s'

        self.getLocVendorHostScoreSql = 'select distinct host.host_id "HOST_ID", host.host_name "HOST", host.dc_info "LOCATION", host.last_scan_score "AVG_SCORE", \
                host.last_scan_id "LAST_SCAN", host.last_scan_time "LAST_SCAN_TIME", \
                tenant.tenant_vendor "VENDOR", tenant.vendor_prod_name "VENDOR_PRODUCT" \
            from p$ht_tenant tenant, p$ht_info host \
            where tenant.tenant_vendor = %(VendorId)s and tenant.host_id = host.host_id \
            and host.dc_info = %(Location)s'

        self.getLocHostScoreSql = 'select host.host_id "HOST_ID", host.host_name "HOST", host.dc_info "LOCATION", host.last_scan_score "AVG_SCORE", host.last_scan_id "LAST_SCAN", host.last_scan_time "LAST_SCAN_TIME" \
            from p$ht_info host \
            where host.dc_info = %(Location)s'

        self.getVendorHostScoreSql = 'select distinct host.host_id "HOST_ID", host.host_name "HOST", host.dc_info "LOCATION", host.last_scan_score "AVG_SCORE", \
                host.last_scan_id "LAST_SCAN", host.last_scan_time "LAST_SCAN_TIME", \
                tenant.tenant_vendor "VENDOR", tenant.vendor_prod_name "VENDOR_PRODUCT" \
            from p$ht_tenant tenant, p$ht_info host \
            where tenant.tenant_vendor = %(VendorId)s and tenant.host_id = host.host_id '

        self.getAllVendorProdAvgScoreSql = 'select tenant_vendor "VENDOR", vendor_prod_name "PRODUCT", avg(last_scan_score) "AVG_SCORE" \
            from p$ht_tenant \
            group by tenant_vendor, vendor_prod_name \
            order by tenant_vendor, vendor_prod_name'

        self.getAVendorProdAvgScoreSql = 'select tenant_vendor "VENDOR", vendor_prod_name "PRODUCT", avg(last_scan_score) "AVG_SCORE" \
            from p$ht_tenant \
            where tenant_vendor = %(VendorId)s \
            group by tenant_vendor, vendor_prod_name \
            order by tenant_vendor, vendor_prod_name'

        self.hostTenantScoreSql = 'select host.host_name "HOST", tenant.tenant_type "TENANT_TYPE", tenant.tenant_name "TENANT_NAME", tenant.last_scan_score "LAST_SCORE", tenant.last_scan_id "LAST_SCAN", tenant.last_scan_time "LAST_ScAN_TIME", \
            tenant.tenant_type "TYPE", tenant.tenant_vendor "VENDOR", tenant.vendor_prod_name "PRODUCT", tenant.tenant_version "VERSION" \
            from p$ht_tenant tenant, p$ht_info host \
            where tenant.host_id = host.host_id \
            order by host.host_name, tenant.tenant_type, tenant.tenant_name '

        self.getAllLocVendorAvgScoreSql = 'select host.dc_info "LOCATION", tenant.tenant_vendor "VENDOR", tenant.vendor_prod_name "PRODUCT", avg(tenant.last_scan_score) "AVG_SCORE" \
            from p$ht_tenant tenant, p$ht_info host \
            where host.host_id = tenant.host_id \
            group by host.dc_info, tenant.tenant_vendor, tenant.vendor_prod_name \
            order by host.dc_info, tenant.tenant_vendor, tenant.vendor_prod_name '

        self.getALocAllVendorAvgScoreSql = 'select host.dc_info "LOCATION", tenant.tenant_vendor "VENDOR", tenant.vendor_prod_name "PRODUCT", avg(tenant.last_scan_score) "AVG_SCORE" \
            from p$ht_tenant tenant, p$ht_info host \
            where host.host_id = tenant.host_id and \
                host.dc_info = %(Location)s \
            group by host.dc_info, tenant.tenant_vendor, tenant.vendor_prod_name \
            order by host.dc_info, tenant.tenant_vendor, tenant.vendor_prod_name '

        self.getAllLocAVendorAvgScoreSql = 'select host.dc_info "LOCATION", tenant.tenant_vendor "VENDOR", tenant.vendor_prod_name "PRODUCT", avg(tenant.last_scan_score) "AVG_SCORE" \
            from p$ht_tenant tenant, p$ht_info host \
            where host.host_id = tenant.host_id and \
                tenant.tenant_vendor = %(VendorId)s \
            group by host.dc_info, tenant.tenant_vendor, tenant.vendor_prod_name \
            order by host.dc_info, tenant.tenant_vendor, tenant.vendor_prod_name '

        self.getALocAVendorAvgScoreSql = 'select host.dc_info "LOCATION", tenant.tenant_vendor "VENDOR", tenant.vendor_prod_name "PRODUCT", avg(tenant.last_scan_score) "AVG_SCORE" \
            from p$ht_tenant tenant, p$ht_info host \
            where host.host_id = tenant.host_id and \
                host.dc_info = %(Location)s and \
                tenant.tenant_vendor = %(VendorId)s \
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
