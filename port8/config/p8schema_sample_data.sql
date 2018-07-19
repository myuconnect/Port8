# UI Page and its associated action

LOAD DATA LOCAL INFILE "/home/anil/app/port8/config/cis_11g_12c_latest.csv" INTO TABLE p8rep.p$secpol_ver_comp_ctrl
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(control_id, seq_order, disp_control_id, comp_id, control_title, status, scored, description, rational, remediation, expect_display, result_display)
;

LOAD DATA LOCAL INFILE "/home/anil/app/port8/config/host_csv.csv" INTO TABLE p8rep.p$ht_info
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(host_id,host_name,location,dc_info,mac_address,processor,total_sockets,cores_per_socket,thread_per_core,total_cpus,phys_memory_mb,swap_memory_mb,network_interface,ip_addresses,os,os_version,os_release,commision_date,decommision_date,uptime_mins,last_scan_id,last_scan_seq_id,last_scan_time,last_scan_score)
;

LOAD DATA LOCAL INFILE "/home/anil/app/port8/config/host_tenant_csv.csv" INTO TABLE p8rep.p$ht_tenant
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n' 
IGNORE 1 LINES
(tenant_id,host_id,tenant_type,tenant_name,tenant_vendor,vendor_prod_name,tenant_version,backup_policy_id,sec_policy_ver_id,start_date,end_date,last_scan_id,last_scan_seq_id,last_scan_time,last_scan_score)
;

insert into p$ui_page (
    page_id, page_name, page_details, page_status
    )
    values
    ('pg100001','Score main','Average score main','ACTIVE'),
    ('pg100002','Location score summary','Location average score','ACTIVE'),
    ('pg100003','Vendor score summary','Vendor average score','ACTIVE'),
    ('pg100004','Location Vendor score summary','Location Vendor average score','ACTIVE'),
    ('pg100005','Host score summary','Host average score (All,Location,Vendor,LocVendor)','ACTIVE'),
    ('pg100006','Tenant score summary','Tenant score (All,Location,Vendor,LocVendor, Host)','ACTIVE'),
    ('pg100007','Host Search','Host Search','ACTIVE');

insert into p$ui_action (
    action_id, page_id, action_name, action_details, action_status,
    bpm_library, bpm_class, bpm_method, bpm_arguments, bpm_call_json, bpm_status)
    values
    ('pg100001_001','pg100001','DISP_LANDING','Display landing','ACTIVE','com.port8.bpm.user_interface','Interface','getOverallAvgScore',NULL,'{"lib":"com.port8.bpm.user_interface","cls":"Interface","method":"getOverallAvgScore","args":[]}', 'ACTIVE'),
    ('pg100002_001','pg100002','DISP_LANDING','Display landing','ACTIVE','com.port8.bpm.user_interface','Interface','getLocAvgScore',NULL,'{"lib":"com.port8.bpm.user_interface","cls":"Interface","method":"getLocAvgScore","args":[]}', 'ACTIVE'),
    ('pg100003_001','pg100003','DISP_LANDING','Display landing','ACTIVE','com.port8.bpm.user_interface','Interface','getVendorAvgScore',NULL,'{"lib":"com.port8.bpm.user_interface","cls":"Interface","method":"getVendorAvgScore","args":[]}', 'ACTIVE'),
    ('pg100004_001','pg100004','DISP_LANDING','Display landing','ACTIVE','com.port8.bpm.user_interface','Interface','getLocVendorAvgScore',NULL,'{"lib":"com.port8.bpm.user_interface","cls":"Interface","method":"getLocVendorAvgScore","args":[]}', 'ACTIVE'),
    ('pg100005_001','pg100005','DISP_LANDING','Display landing','ACTIVE','com.port8.bpm.user_interface','Interface','getHostAvgScore',NULL,'{"lib":"com.port8.bpm.user_interface","cls":"Interface","method":"getHostAvgScore","args":[]}', 'ACTIVE'),
    ('pg100006_001','pg100006','DISP_LANDING','Display landing','ACTIVE','com.port8.bpm.user_interface','Interface','getHostTenantScore',NULL,'{"lib":"com.port8.bpm.user_interface","cls":"Interface","method":"getHostTenantScore","args":[]}', 'ACTIVE'),
    ('pg100007_001','pg100007','SEARCH','Search Host','ACTIVE','com.port8.bpm.user_interface','Interface','getHostInfo',NULL,'{"lib":"com.port8.bpm.user_interface","cls":"Interface","method":"getHostInfo","args":[]}', 'ACTIVE');

insert into p$security_policy (
    security_policy_id, target, status, start_date, end_time, comments
    )
    values
    ('SEC_ORA','ORACLE-DB','ACTIVE','2018-01-01', '9999-12-31','This is for Oracle database Standalone/RAC'),
    ('SEC_MYSQL','ORA-MYSQL','ACTIVE','2018-01-01', '9999-12-31','This is for Oracle MySql'),
    ('SEC_MONGO','MONGO-DB','ACTIVE','2018-01-01', '9999-12-31','This is for Mongo database'),
    ('SEC_MSSQL','MS-SQL','ACTIVE','2018-01-01', '9999-12-31','This is for Microsoft Sql server');

insert into p$sec_policy_ver (
    sec_policy_ver_id, security_policy_id, version, status, start_date, end_time, comments
    )
    values
    ('ORA11G','SEC_ORA','11*','ACTIVE','2018-01-01', '2018-12-31','This is for Oracle database Standalone/RAC 11g'),
    ('ORA12C','SEC_ORA','11*','ACTIVE','2018-01-01', '2018-12-31','This is for Oracle database Standalone/RAC 12c'),
    ('MYSQL4','SEC_MYSQL','4*','ACTIVE','2018-01-01', '2018-12-31','This is for Oracle MY SQL version 4*'),
    ('MYSQL5','SEC_MYSQL','5*','ACTIVE','2018-01-01', '2018-12-31','This is for Oracle MY SQL version 5*'),
    ('MONGO2','SEC_MOMGO','2*','ACTIVE','2018-01-01', '2018-12-31','This is for Mongo database version 2*'),
    ('MONGO3','SEC_MOMGO','3*','ACTIVE','2018-01-01', '2018-12-31','This is for Mongo database version 3*');

insert into p$sec_policy_ver_comp (
    comp_id, sec_policy_ver_id, seq_order, disp_comp_id, comp_name, sub_comp_name, status, comments
    )
    values
    ('ORA11G1001','ORA11G', 1,'1.0', 'Oracle Database Installation and Patching Requirements', null,   'ACTIVE','This is for validating ORACLE installation and patching requirements'),
    ('ORA11G1002','ORA11G', 2,'2.1', 'Oracle Parameter Settings','Listener Settngs','ACTIVE','This is for validating ORACLE database Listener setting parameter'),
    ('ORA11G1003','ORA11G', 3,'2.2', 'Oracle Parameter Settings','Database Settngs','ACTIVE','This is for validating ORACLE database Database parameter'),
    ('ORA11G1004','ORA11G', 4,'3.0', 'Oracle connectons and login restrictions',null,'ACTIVE','This is for validating database profile and its resource settings'),
    ('ORA11G1005','ORA11G', 5,'4.1', 'Default Public Privileges for Packages and Object Types','Revoke Default Public Privileges for Packages and Object Types','ACTIVE','Revoke Default Public Privileges for Packages and Object Types'),
    ('ORA11G1006','ORA11G', 6,'4.2', 'Default Public Privileges for Packages and Object Types','Revoke Non-Default Privileges for Packages and Object Types','ACTIVE','Revoke Non-Default Privileges for Packages and Object Types'),
    ('ORA11G1007','ORA11G', 7,'4.3', 'Default Public Privileges for Packages and Object Types','Revoke Excessive System Privileges','ACTIVE','Revoke Excessive System Privileges'),
    ('ORA11G1008','ORA11G', 8,'4.4', 'Default Public Privileges for Packages and Object Types','Revoke Role Privileges','ACTIVE','Revoke Role Privileges'),
    ('ORA11G1009','ORA11G', 9,'4.5', 'Default Public Privileges for Packages and Object Types','Revoke Excessive Table and View Privileges','ACTIVE','Revoke Excessive System Privileges'),
    ('ORA11G1010','ORA11G',10,'5.1', 'Audit/Logging Policies and Procedures','Traditional Auditing','ACTIVE','Audit/Logging Policies and Procedures - Traditional Auditing'),
    ('ORA12C1001','ORA12C', 1,'1.0', 'Oracle Database Installation and Patching Requirements',null,    'ACTIVE','This is for validating ORACLE installation and patching requirements'),
    ('ORA12C1002','ORA12C', 2,'2.1', 'Oracle Parameter Settings','Listener Settngs','ACTIVE','This is for validating ORACLE database Listener setting parameter'),
    ('ORA12C1003','ORA12C', 3,'2.2', 'Oracle Parameter Settings','Database Settngs','ACTIVE','This is for validating ORACLE database Database parameter'),
    ('ORA12C1004','ORA12C', 4,'3.0', 'Oracle connectons and login restrictions',null,'ACTIVE','This is for validating database profile and its resource settings'),
    ('ORA12C1005','ORA12C', 5,'4.1', 'Default Public Privileges for Packages and Object Types','Revoke Default Public Privileges for Packages and Object Types','ACTIVE','Revoke Default Public Privileges for Packages and Object Types'),
    ('ORA12C1006','ORA12C', 6,'4.2', 'Default Public Privileges for Packages and Object Types','Revoke Non-Default Privileges for Packages and Object Types','ACTIVE','Revoke Non-Default Privileges for Packages and Object Types'),
    ('ORA12C1007','ORA12C', 7,'4.3', 'Default Public Privileges for Packages and Object Types','Revoke Excessive System Privileges','ACTIVE','Revoke Excessive System Privileges'),
    ('ORA12C1008','ORA12C', 8,'4.4', 'Default Public Privileges for Packages and Object Types','Revoke Role Privileges','ACTIVE','Revoke Role Privileges'),
    ('ORA12C1009','ORA12C', 9,'4.5', 'Default Public Privileges for Packages and Object Types','Revoke Excessive Table and View Privileges','ACTIVE','Revoke Excessive System Privileges'),
    ('ORA12C1010','ORA12C',10,'5.1', 'Audit/Logging Policies and Procedures','Traditional Auditing','ACTIVE','Audit/Logging Policies and Procedures - Traditional Auditing'),
    ('ORA12C1011','ORA12C',11,'5.2', 'Audit/Logging Policies and Procedures','Unified Auditing','ACTIVE','Audit/Logging Policies and Procedures - Unified Auditing');

#insert into p$sec_policy_ver_comp (
#    comp_id, parent_comp_id, sec_policy_ver_id, seq_order, disp_comp_id, comp_name, status, comments
#    )
#    values
#    ('ORA12C1001',null,         'ORA12C', 1,'1.0', 'Oracle Database Installation and Patching Requirements',    'ACTIVE','This is for validating ORACLE installation and patching requirements'),
#    ('ORA12C1002',null,         'ORA12C', 2,'2.1', 'Oracle Parameter Settings','ACTIVE','This is for validating ORACLE database OS file permission'),
#    ('ORA12C1003','ORA12C1002', 'ORA12C', 3,'2.1', 'Listener Settngs','ACTIVE','This is for validating ORACLE database Listener setting parameter'),
#    ('ORA12C1004','ORA12C1002', 'ORA12C', 4,'2.2', 'Database Settngs','ACTIVE','This is for validating ORACLE database Database parameter'),
#    ('ORA12C1005',null,         'ORA12C', 5,'3.0', 'Oracle connectons and login restrictions','ACTIVE','This is for validating database profile and its resource settings'),
#    ('ORA12C1006','ORA12C1004', 'ORA12C', 6,'4.0', 'Default Public Privileges for Packages and Object Types','ACTIVE','Default Public Privileges for Packages and Object Types'),
#    ('ORA12C1007','ORA12C1004', 'ORA12C', 6,'4.1', 'Revoke Non-Default Privileges for Packages and Object Types','ACTIVE','Revoke Non-Default Privileges for Packages and Object Types'),
#    ('ORA12C1008','ORA12C1004', 'ORA12C', 6,'4.2', 'Revoke Excessive System Privileges','ACTIVE','Revoke Excessive System Privileges'),
#    ('ORA12C1009','ORA12C1004', 'ORA12C', 6,'4.4', 'Revoke Role Privileges','ACTIVE','This is for validating Oracle user access and authorization');
#    ('ORA12C1010','ORA12C1004', 'ORA12C', 6,'4.5', 'Revoke Excessive Table and View Privileges','ACTIVE','Revoke Excessive System Privileges'),
#    ('ORA12C1011',null,         'ORA12C', 6,'5.6', 'Revoke Excessive System Privileges','ACTIVE','Revoke Excessive System Privileges'),
#    ('ORA12C1012','ORA12C1004', 'ORA12C', 6,'4.0', 'Revoke Excessive System Privileges','ACTIVE','Revoke Excessive System Privileges'),

#insert into p$secpol_ver_comp_ctrl (
#    control_id, display_id, scan_name, expect_display, output_disp_head, library, cls, method, arguments, 
#    method_call_json, validation, status, comments, history, scored)
#    values
#    ('ORA10G_01_01','1.01', 'Ensure listener.ora has restrictive permission', 
#        'listener.ora octal value must be less than or equal to 644','Displaying listener.ora octal value',
#        'com.port8.core.isecurity', 'SecScan', 'valOsFileOctalValue', '"listener.ora", "le",644', 
#        '[
#            {
#                "library":"com.port8.core.isecurity",
#                "class": "SecScan", 
#                "method": {"name" : "valOsFileOctalValue", "arguments" : ["{ORACLE_HOME}","OS_SPEC_FILE","listener","le",644]}
#            }
#        ]', null,
#        'Active', 'Validating listener.ora file octal value',NULL, 'YES'),
#    ('ORA10G_01_02','1.02', 'Ensure tnsnames.ora has restrictive permission', 
#        'tnsnames.ora octal value must be less than or equal to 644','Displaying tnsnames.ora octal value',
#        'com.port8.core.isecurity', 'SecScan', 'valOsFileOctalValue', '"tnsnames.ora","le",644', 
#        '[
#            {
#                "library":"com.port8.core.isecurity",
#                "class": "SecScan", 
#                "method": {"name" : "valOsFileOctalValue", "arguments" : ["{ORACLE_HOME}","FILE","tnsnames.ora","le",644]}
#            }
#        ]', null,
#        'Active', 'Validating tnsnames.ora file octal value',NULL, 'YES'),
#    ('ORA10G_01_03','1.03', 'Ensure tkprof has restrictive permission', 
#        'tkprof/tkrpof.exe octal value must be less than or equal to 700','Displaying tkprof/tkprof.exe octal value',
#        'com.port8.core.isecurity', 'SecScan', 'valOsFileOctalValue', '"tkprof","le",700', 
#        '[
#            {
#                "library":"com.port8.core.isecurity",
#                "class": "SecScan", 
#                "method": {"name" : "valOsFileOctalValue", "arguments" : ["{ORACLE_HOME}","OS_SPEC_FILE","tkprof","le",644]}
#            }
#        ]', null,
#        'Active', 'Validating tkprof file octal value',NULL, 'YES'),
#    ('ORA10G_01_04','1.04', 'Ensure sqlplus has restrictive permission', 
#        'sqlplus/Sqlplus.exe octal value must be restrictive of 700','Displaying sqlplus* octal value',
#        'com.port8.core.isecurity', 'SecScan', 'valOsFileOctalValue', '"sqlplus", "sqlplus*.exe","le",700', 
#        '[
#            {
#                "library":"com.port8.core.isecurity",
#                "class": "SecScan", 
#                "method": {"name" : "valOsFileOctalValue", "arguments" : ["{ORACLE_HOME}","OS_SPEC_FILE","sqlplus","le",700]}
#            }
#        ]', null,
#        'Active', 'Validating sqlplus* file octal value',NULL, 'YES'),
#    ('ORA10G_01_05','1.05', 'Ensure no init/pfile exists in ORACLE_HOME must use spfile',
#        'init/pfile must not exist in ORACLE_HOME/dbs','Listing init/pfile from ORACLE_HOME/dbs',
#        'com.port8.core.isecurity', 'SecScan', 'valOsFileExistence', '', 
#        '[
#            {
#                "library":"com.port8.core.isecurity",
#                "class": "SecScan", 
#                "method": {"name" : "valOsFileExistence", "arguments" : ["{ORACLE_HOME}/dbs","FILE_PATTERN","*pfile*","NOT_EXIST"]}
#            }
#        ]', null,
#        'Active', 'Validating existense of init/pfile',NULL, 'YES'),
#    ('ORA10G_01_06','1.06', 'Ensure ORACLE_HOME directory has restrictive permission',
#        'ORACLE_HOME directory octal value must be less than 700 ','Listing octal value of ORACLE_HOME/dbs',
#        'com.port8.core.isecurity', 'SecScan', 'valOsFileOctalValue', '"{ORACLE_HOME}","le",700', 
#        '[
#            {
#                "library":"com.port8.core.isecurity",
#                "class": "SecScan", 
#                "method": {"name" : "valOsFileOctalValue", "arguments" : ["{ORACLE_HOME}","DIR","dir", "le",700]}
#            }
#        ]', null,
#        'Active', 'Validating ORACLE_HOME octal value',NULL, 'YES'),
#    ('ORA10G_01_07','1.07', 'Ensure files in ORACLE_HOME/bin directory has restrictive permission',
#        'ORACLE_HOME directory octal value must be less than 700 ','Listing octal value of ORACLE_HOME/dbs',
#        'com.port8.core.isecurity', 'SecScan', 'valOsFileOctalValue', '"{ORACLE_HOME}","le",744', 
#        '[
#            {
#                "library":"com.port8.core.isecurity",
#                "class": "SecScan", 
#                "method": {"name" : "valOsFileOctalValue", "arguments" : ["{ORACLE_HOME}/bin","FILE_PATTERN","*", "le",700]}
#            }
#        ]', null,
#        'Active', 'Validating ORACLE_HOME octal value',NULL, 'YES');

insert into p$process (
    proc_id, proc_name, proc_desc, proc_type, proc_status, _change_history
    )
    values
    ('PROC100001', 'SEC_SCAN_ALL', 'Security scan for all host and its tenants', 'SEC_SCAN','ACTIVE',
        '[ {"when": "Factory build", "What":"Factory build","Who": "Factory build"} ]'),
    ('PROC100002', 'SEC_SCAN_ADHOC_HOST', 'Ad-hoc security scan for Host(s)', 'SEC_SCAN','ACTIVE',
        '[ {"when": "Factory build", "What":"Factory build","Who": "Factory build"} ]'),
    ('PROC100003', 'SEC_SCAN_ADHOC_TENANT', 'Ad-hoc security scan for Tenant(s)', 'SEC_SCAN','ACTIVE',
        '[ {"when": "Factory build", "What":"Factory build","Who": "Factory build"} ]');

insert into p$process_task (
    task_id, proc_id, task_seq, library, cls, method, arguments, task_status,method_call_json
    )
    values
    ('TASK1000001','PROC100001',1,'com.port8.isecurity','SecScan','perfomrAllSecScan',NULL,'ACTIVE',
        '[
            {
                "library":"com.port8.core.isecurity",
                "class": "SecScan", 
                "method": {"name" : "performAllSecScan", "arguments" : []}
            }
        ]'),
    ('TASK1000002','PROC100002',2,'com.port8.isecurity','SecScan','perfAdHocHTSecScan',NULL,'ACTIVE',
        '[
            {
                "library":"com.port8.core.isecurity",
                "class": "SecScan", 
                "method": {"name" : "perfAdHocHTSecScan", "arguments" : ["{HOST_LIST}"]}
            }
        ]'),
    ('TASK1000003','PROC100002',3,'com.port8.isecurity','SecScan','perfAdHocTENTSecScan',NULL,'ACTIVE',
        '[
            {
                "library":"com.port8.core.isecurity",
                "class": "SecScan", 
                "method": {"name" : "perfAdHocTENTSecScan", "arguments" : ["{TENANT_LIST}"]}
            }
        ]');

insert into p$jobs_run_log (
    job_run_id, job_type, job_status, proc_id, start_time, end_time, total_unit, sofar
    )
    values
    ('01012018_100000001','SEC SCAN','STARTED', 'PROC1000001', now(),NULL,NULL,NULL),
    ('01012018_100000002','SEC SCAN','IN-PROGRESS', 'PROC1000002', now(),NULL,NULL,NULL);

    
insert into p$jobs_runtask_log (
    job_run_id, task_id, task_status, task_start_time, task_end_time, total_unit, sofar, last_heartbeat_time
    )
    values
    ('01012018_100000001','TASK1000001','STARTED',now(),NULL,1235,0,now());



## Host/Tenant scan data
# Users

insert into p$ht_info (
    host_id, host_name, location, dc_info, os, os_version, os_release, total_sockets, cores_per_socket, thread_per_core, total_cpus,ip_addresses, 
    phys_memory_mb, swap_memory_mb, commision_date, decommision_date, uptime_mins, 
    last_scan_id, last_scan_seq_id,last_scan_time, last_scan_score,mac_address,processor)
    values
    ('H20001', 'dev01.port8.com', 'floor:1b, cage : cage01, rack : rack01', "EAST - ATLANTA", "LINUX-RHEL","5.7", "1.2.3x3.64", 8,8,2,128,
     '10.02.01.32',10240,1024, NULL, NULL,1200,'JOBSEC10001',1,'2018-01-01 10:00:00',68.11,'sh53.43.4343434','Genuine Intel' ),
    ('H20002', 'dev02.port8.com', 'floor:1b, cage : cage01, rack : rack01', "EAST - ATLANTA", "LINUX-RHEL","5.7", "1.2.3x3.64", 8,8,2,128,
     '10.02.05.33',10240,1024, NULL, NULL,1200,'JOBSEC10001',1,'2018-01-01 10:00:00', 75, 're78.443434','Genuine Intel'  ),
    ('H20003', 'dev03.port8.com', 'floor:1b, cage : cage01, rack : rack01', "EAST - ATLANTA", "LINUX-RHEL","5.7", "1.2.3x3.64", 8,8,2,128,
     '10.02.05.38',10240,1024, NULL, NULL,1200,'JOBSEC10001',1,'2018-01-01 10:00:00', 65 ,'5453.43.43434','Genuine Intel' ),
    ('H20004', 'dev04.port8.com', 'floor:1b, cage : cage01, rack : rack01', "EAST - ATLANTA", "LINUX-RHEL","5.7", "1.2.3x3.64", 8,8,2,128,
     '10.03.05.72',10240,1024, NULL, NULL,1200,'JOBSEC10001',1,'2018-01-01 10:00:00', 60, 'gt89.43.43434','Genuine Intel' ),
    ('H20005', 'dev05.port8.com', 'floor:1b, cage : cage01, rack : rack01', "EAST - ATLANTA", "LINUX-RHEL","5.7", "1.2.3x3.64", 8,8,2,128,
     '10.03.05.88', 10240,1024, NULL, NULL,1200,'JOBSEC10001',1,'2018-01-01 10:00:00', 90, 'uy99.43.43434','Genuine Intel' ),
    ('H20006', 'dev06.port8.com', 'floor:1b, cage : cage01, rack : rack01', "EAST - ATLANTA", "LINUX-RHEL","5.7", "1.2.3x3.64", 8,8,2,128,
     '10.03.05.99',10240,1024, NULL, NULL,1200,'JOBSEC10001',1,'2018-01-01 10:00:00', 78, 'j587.43.4563','Genuine Intel' ),
    ('H20007', 'dev07.port8.com', 'floor:1b, cage : cage01, rack : rack01', "EAST - ATLANTA", "LINUX-RHEL","5.7", "1.2.3x3.64", 8,8,2,128,
     '10.02.05.101',10240,1024,NULL, NULL,1200,'JOBSEC10001',1,'2018-01-01 10:00:00', 58, '1111.43.434278','Genuine Intel' );

insert into p$ht_tenant (
    tenant_id, host_id, tenant_type, tenant_name, tenant_vendor, vendor_prod_name,tenant_version, 
    sec_policy_ver_id, start_date, end_date, last_scan_id, last_scan_seq_id, last_scan_time, last_scan_score  
    )
    values
    ('T200001','H20001','DB','DEV00001','ORACLE','ORACLE DATABASE','10.2.4','ORA_10G','2018-01-01','9999-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',75),
    ('T200002','H20001','DB','DEV00200','ORACLE','ORACLE DATABASE','11.2.4','ORA_11G','2018-01-01','2029-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',65),
    ('T200003','H20001','DB','DEV00200','ORACLE','ORACLE DATABASE','11.2.4','ORA_11G','2018-01-01','2029-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',35),
    ('T200004','H20001','DB','DEV00200','ORACLE','ORACLE DATABASE','11.2.4','ORA_11G','2018-01-01','2029-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',65),
    ('T200005','H20001','DB','DEV00200','ORACLE','ORACLE DATABASE','11.2.4','ORA_11G','2018-01-01','2029-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',80),
    ('T200006','H20001','DB','DEV00200','ORACLE','ORACLE DATABASE','11.2.4','ORA_11G','2018-01-01','2029-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',90),
    ('T200007','H20001','DB','DEV00200','ORACLE','ORACLE DATABASE','11.2.4','ORA_11G','2018-01-01','2029-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',60),
    ('T200008','H20001','DB','DEV00200','ORACLE','ORACLE DATABASE','11.2.4','ORA_11G','2018-01-01','2029-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',88),
    ('T200009','H20001','OS','dev01.port8.com','REDHAT','LINUX-RHEL','6.11','RHEL-OS-6','2018-01-01','2029-12-31','JOBSEC10001',1,'2018-01-01 10:00:00',55);
