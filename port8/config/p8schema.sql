# 
create database p8rep;

use p8rep;

SELECT @@SQL_MODE;
SET SQL_MODE = ('ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION');

# User/Role access

create table p$ui_page (
    page_id              VARCHAR(50)             NOT NULL PRIMARY KEY,
    page_name            VARCHAR(100)            NOT NULL,
    page_details         VARCHAR(200)            NOT NULL,
    page_status          ENUM('ACTIVE','INACTIVE')
);

create table p$ui_action (
    action_id               VARCHAR(50)             NOT NULL PRIMARY KEY,
    page_id                 VARCHAR(50)             NOT NULL,
    action_name             VARCHAR(100)            NOT NULL,
    action_details          VARCHAR(200)            NOT NULL,
    action_status           ENUM('ACTIVE','INACTIVE'),
    bpm_library             VARCHAR(100)            NOT NULL,
    bpm_class               VARCHAR(80)             NOT NULL,
    bpm_method              VARCHAR(100)            NOT NULL,
    bpm_arguments           VARCHAR(100)            ,
    bpm_call_json           JSON                    NOT NULL,
    bpm_status              ENUM ('ACTIVE','INACTIVE') NOT NULL
);

create table p$factory_call_info (
    action_id               VARCHAR(20)             PRIMARY KEY,
    Description             VARCHAR(200)            NOT NULL,
    bpm_library             VARCHAR(100)            NOT NULL,
    bpm_class               VARCHAR(80)             NOT NULL,
    bpm_method              VARCHAR(100)            NOT NULL,
    bpm_arguments           VARCHAR(100)            NOT NULL,
    bpm_call_json           JSON                    NOT NULL,
    bpm_status              ENUM ('ACTIVE','INACTIVE') NOT NULL
);

#alter table p$factory_call_info add constraint p$factory_call_info_pk (ui_page_action_id);

create table p$ui_page_access (
    page_id                 VARCHAR(50)             NOT NULL,
    user_role_id            VARCHAR(20)             NOT NULL,
    access_type             ENUM('READ ONLY','ALL')
);

alter table p$ui_page_access add constraint p$ui_page_access_pk primary key(page_id, user_role_id);

create table p$ui_page_access_excl (
    page_id                 VARCHAR(50)             NOT NULL,
    user_role_id            VARCHAR(20)             NOT NULL,
    access_type             ENUM('READ ONLY','ALL')
);

alter table p$ui_page_access_excl add constraint p$ui_page_access_pk primary key(page_id, user_role_id);

create table p$ui_page_action_access (
    action_id               VARCHAR(50)             NOT NULL,
    page_id                 VARCHAR(50)             NOT NULL,
    user_role_id            VARCHAR(20)             NOT NULL,
    access_type             ENUM('READ ONLY','ALL')
);

alter table p$ui_page_action_access add constraint p$ui_page_action_access_pk primary key(action_id, user_role_id);


create table p$ui_page_action_access_excl (
    action_id               VARCHAR(50)             NOT NULL,
    user_role_id            VARCHAR(20)             NOT NULL,
    access_type             ENUM('READ ONLY','ALL')
);

alter table p$ui_page_action_access_excl add constraint p$ui_page_access_pk primary key(action_id , user_role_id);


# Security Policy

CREATE TABLE p$security_policy (
    security_policy_id      VARCHAR (10)            NOT NULL PRIMARY KEY,
    target                  VARCHAR (15)            NOT NULL comment 'Type of tenant this securty belongs to Oracle Database/RHEL/MYSQL/MONGO/MYSQL ',
    status                  ENUM('ACTIVE','INACTIVE') DEFAULT 'INACTIVE'   comment 'ACTIVE/INACTIVE',
    start_date              DATE                    NOT NULL comment 'Start date of this securty polict',
    end_time                DATE                    NOT NULL comment 'End Date of this secutity policy',
    comments                TEXT                             comment 'Any comment we feel applicable'
);

CREATE TABLE p$sec_policy_ver (
    sec_policy_ver_id       VARCHAR (10)            NOT NULL PRIMARY KEY,
    security_policy_id      VARCHAR (10)            NOT NULL, 
    version                 VARCHAR (10)            NOT NULL comment 'Version of tenant this security applies to, Oracle database 12c has more security scan comparing to version 11g',
    status                  ENUM('ACTIVE','INACTIVE') DEFAULT 'INACTIVE'   comment 'ACTIVE/INACTIVE',
    start_date              DATE                    NOT NULL comment 'Start date of this securty polict',
    end_time                DATE                    NOT NULL comment 'End Date of this secutity policy',
    comments                TEXT                             comment 'Any comment we feel applicable'
);

CREATE TABLE p$sec_policy_ver_comp (
    comp_id                 VARCHAR (20)            NOT NULL PRIMARY KEY,
    disp_comp_id            VARCHAR (20)            NOT NULL COMMENT 'Display comp id; id will be displayed',
    comp_name               VARCHAR (80)            NOT NULL comment 'Main component name',
    sub_comp_name           VARCHAR (80)                     comment 'Sub component of main component (optional)',
    seq_order               INTEGER                 NOT NULL comment 'Order in which component be assessed',
    sec_policy_ver_id       VARCHAR (20)                     comment 'sec_policy_ver_id to this component beongs to',
    status                  ENUM('ACTIVE','INACTIVE') DEFAULT 'INACTIVE'   comment 'ACTIVE/INACTIVE',
    comments                VARCHAR (1000)                   comment 'comments'
);

CREATE TABLE p$secpol_ver_comp_ctrl (
    control_id              VARCHAR (20)            NOT NULL PRIMARY KEY,
    disp_control_id         VARCHAR (10)            NOT NULL comment 'Display control id',
    control_title           VARCHAR (1000)          NOT NULL comment 'Scan Name description',
    comp_id                 VARCHAR (20)            NOT NULL comment 'Compoent to which this control belongs to',
    severity                ENUM('9','5','1')      comment 'Severity of control High/Medium/Low',
    description             TEXT                             comment 'Detailed description of control',
    seq_order               INTEGER                 NOT NULL comment 'Seq order in which control of a given component to be assessed',
    rational                TEXT                             comment 'Ratonal of this control',
    remediation             TEXT                             comment 'Remediation of this control',
    expect_display          VARCHAR (1000)          NOT NULL comment 'Expected Dispaly; expected output display of this scan (REMOTE_LISTENER should be set to SCAN_NAME:PORT)',
    result_display          VARCHAR (1000)          NOT NULL comment 'control result display heading',
    library                 VARCHAR (200)           NOT NULL comment 'Library/module to be used for execution of this scan',
    cls                     VARCHAR (100)           NOT NULL comment 'Class which need to instantiated for execution of this scan',
    method                  VARCHAR (200)           NOT NULL comment 'Method from cls which need to executed for this scan', 
    arguments               VARCHAR (1000)                   comment 'Argument which need to be passed to methd as stated in mehtod column',
    addl_call_info          TEXT                             comment 'Any additional information to be used during call (for e.g. sql)',
    method_call_json        JSON,
    validation              VARCHAR (200)                    comment 'Validation need to be performed upon execution of method',
    is_exclusion_allowed    VARCHAR (1)                      comment 'Does this control allow exclusion during execution of this control',
    excl_type               VARCHAR (10)                     comment 'exclusion type SQL_WHERE_CLAUSE, OS_FILTER_OUTPUT',
    excl_list               TEXT                             comment 'default exclusion which need to be applied',
    status                  ENUM('ACTIVE','INACTIVE')        comment 'ACTIVE/INACTIVE',
    comments                VARCHAR (2000),
    history                 TEXT                             comment 'Store the changes happened mainly to Status, if status is changed to INACTIVE',
    scored                  VARCHAR (3)                      comment 'YES/NO, is this scan scored'
);


# following table will store any control which has been excluded for a tenant
# this control will not be executed but will be reported as skiped and would not be marked as "scored"

CREATE TABLE p$ht_excluded_control (
    tenant_id               VARCHAR (20),
    control_id              VARCHAR (20)                     comment 'control to be excluded for this tenant',
    excl_support_docs       TEXT                             comment 'Any supporting docs like Change # for customer excluded control for tenant',
    created_by              VARCHAR (20),
    created_date            TIMESTAMP
);

ALTER TABLE p$ht_excluded_control add constraint p$ht_excluded_control_pk primary key (tenant_id, control_id);

# following table will store user/ct defined exclusion list for certain control and tenant
# any exclusion list found for control will be added to exisitng control exclusion list already defined

CREATE TABLE p$ht_ctrl_excl_attr (
    tenant_id               VARCHAR (20),
    control_id              VARCHAR (20)                     comment 'control to which this additional exlusion belongs to',
    excl_type               VARCHAR (10)                     comment 'exclusion type SQL_WHERE_CLAUSE, OS_FILTER_OUTPUT',
    excl_list               TEXT                             comment 'exclusion list',
    is_system               VARCHAR (1)                      comment 'Is this exclusion list created by system or by customer',
    excl_support_docs       TEXT                             comment 'Any supporting docs like Change control for customer created exclusion list',
    created_by              VARCHAR (20),
    created_date            TIMESTAMP
);

ALTER TABLE p$ht_ctrl_excl_attr add constraint p$ht_ctrl_excl_attr_pk primary key (tenant_id, control_id, excl_type);

# Host Tenant

# Host
CREATE TABLE p$ht_info (
    host_id                 VARCHAR (30)            NOT NULL PRIMARY KEY,
    host_name               VARCHAR (100)           NOT NULL comment 'Fully qualified host name including domain name',
    location                VARCHAR (200)           NOT NULL comment 'Location where host is residing, need this for tagging (RACK/CAGE info)',
    dc_info                 VARCHAR (200)           NOT NULL comment 'Host data center information',
    mac_address             VARCHAR (20)                     comment 'MAC address',
    processor               VARCHAR (30)            NOT NULL comment 'Processor type used in this host',
    total_sockets           INTEGER                 NOT NULL comment 'Total sockets on this host',
    cores_per_socket        INTEGER                 NOT NULL comment 'Total cores on each socket',
    thread_per_core         INTEGER                 NOT NULL comment 'Total thread on each socket',
    total_cpus              INTEGER                 NOT NULL comment 'CPUS computed as Total sockets * cores_per_thread * threads_rer_core',
    phys_memory_mb          INTEGER                 NOT NULL comment 'Total physical memory',
    swap_memory_mb          INTEGER                 NOT NULL comment 'Total swap configured on this host',
    network_interface       TEXT,
    ip_addresses            VARCHAR(30)             NOT NULL comment 'IP address (V4/V6) of host',
    os                      VARCHAR (20)            NOT NULL comment 'OS name residing on this host LINUX-RHEL/LINUX-SUSE/LINUX-CENTO/WINDOWS',
    os_version              VARCHAR (20)            NOT NULL comment 'OS version',
    os_release              VARCHAR (30)            NOT NULL comment 'OS Release',
    commision_date          DATE                        comment 'Whent this host went live',
    decommision_date        DATE                        comment 'Whent this host was decommisioned',
    uptime_mins             INTEGER                 NOT NULL comment 'uptime in minutes',
    scan_id                 varchar (20)                     comment 'Last successful scan id',
    scan_time               TIMESTAMP                        comment 'Last scan id timestamp',
    scan_score              DOUBLE                           comment 'Average score of this host (avg of all tenant score)',
    sev_high_score          DOUBLE                           comment 'Avergae high severity percentage of last scan (avg of all tenant score)',
    sev_med_score           DOUBLE                           comment 'Avergae med severity percentage of last scan (avg of all tenant score)',
    sev_low_score           DOUBLE                           comment 'Avergae low severity percentage of last scan (avg of all tenant score)'
);

CREATE TABLE p$ht_tenant (
    tenant_id               VARCHAR (20)            NOT NULL PRIMARY KEY,
    host_id                 VARCHAR (30)            NOT NULL,
    tenant_type             ENUM('OS','DB','MIDDLEWARE')
                                                    NOT NULL comment 'Tenant type OS/DB/MIDDLEWARE',
    tenant_name             VARCHAR (20)            NOT NULL comment 'Tenant name; DB Name, OS Name, (each host has tenant)',
    tenant_vendor           VARCHAR (20)            NOT NULL comment 'Vendor name; DB/OS Vendor name (Oracle/Microsoft/Mongo/RHEL)',
    vendor_prod_name        VARCHAR (20)            NOT NULL comment 'Vendors product name which this tenant belongs to (ORACLE has 2 main prod ORACLE DATABASE/MYSQL DATABASE)',
    tenant_version          VARCHAR (20)            NOT NULL comment 'Tenant version',
    backup_policy_id        VARCHAR (30)                     comment 'Backup policy attached for this tenant as described in backup policy table',
    sec_policy_ver_id       VARCHAR (30)                     comment 'Security policy (ver) attached for this tenant as described in security policy ver table, each vendor has different security policy',
    start_date              DATE                    NOT NULL comment 'Start date of security scan for this tenant',
    end_date                DATE                    NOT NULL comment 'End date of security scan for this tenant (if end date is in past, score will not reflect in host score',
    sec_scan_hist           JSON                             comment 'Last 2 security scan run in json format "," for e.g. [{id:<>,date,when:<>,score:<> [{id:01012018,when:01-JAN-2015,score:95 100000, 102:01022018 090000',
    scan_id                 varchar (20)                     comment 'Last successful scan id',
    scan_time               TIMESTAMP                        comment 'Last scan id timestamp',  
    scan_score              DOUBLE                           comment 'Scan score',
    sev_high_score          DOUBLE                           comment 'High severity percentage of last scan',
    sev_med_score           DOUBLE                           comment 'Med severity percentage of last scan',
    sev_low_score           DOUBLE                           comment 'Low severity percentage of last scan'
);

# Scan Details
# Host scan (host and OS)
CREATE TABLE p$ht_scan (
    host_id                 VARCHAR(20)             NOT NULL,
    scan_id                 VARCHAR(20)             NOT NULL,
    scan_seq_id             INTEGER                 NOT NULL,
    phys_mem_mb             INTEGER                 NOT NULL comment 'Physical memory found on this host',
    swap_mem_mb             INTEGER                 NOT NULL comment 'Swap memory found on this host',
    total_sockets           INTEGER                 NOT NULL comment 'Total sockets found on this host',
    cores_per_socket        INTEGER                 NOT NULL comment 'Cores per socket found on this host',
    threads_per_core        INTEGER                 NOT NULL comment 'Thread per cores found on this host',
    network_interface       TEXT                    ,
    ip_address              VARCHAR(60)             NOT NULL comment 'IP address of host',
    grp_users_detail        TEXT                    NOT NULL comment 'group user detail',
    file_system             TEXT                             comment 'Filesystem information (FSTAB) We need physical device mapped to mounted FS and its usage (total, used, free)',
    schedule_details        TEXT                             comment 'Store job/task scheduled on this host',    
    uptime_mins             INTEGER                 NOT NULL comment 'Uptime of this server',
    scan_start_time         TIMESTAMP               NOT NULL comment 'Start time of this job run',
    scan_end_time           TIMESTAMP               NOT NULL comment 'End time of this job run',
    elapsed_seconds         INTEGER                          comment 'Total elapsed seconds for this scan job run'
);

ALTER TABLE p$ht_scan ADD constraint p$ht_scan_pk PRIMARY KEY ( host_id, scan_id, scan_seq_id );

# we dont need this, Host is built of hardware it doesnt have any kernel information
# kernel informatrion belongs to tenant os/db
CREATE TABLE p$ht_scan_config_detail (
    host_id                 VARCHAR(30)             NOT NULL,
    scan_id                 VARCHAR(20)             NOT NULL,
    scan_seq_id             INTEGER                 NOT NULL,
    scan_time               VARCHAR(20)             NOT NULL,
    config_name             VARCHAR(30)             NOT NULL comment 'Kernel config name of host, For e.g. OS: all kernel name',
    config_value            VARCHAR(1000)           NOT NULL comment 'Kernel config value',
    comment                 TEXT 
);

ALTER TABLE p$ht_scan_config_detail ADD PRIMARY KEY (host_id, scan_id, scan_seq_id);

CREATE TABLE p$ht_tenant_scan (
    tenant_id               VARCHAR(10)             NOT NULL,
    scan_id                 VARCHAR(20)             NOT NULL,
    scan_seq_id             INTEGER                 NOT NULL,
    scan_output             TEXT                                comment 'Security scan output for this control',
    scan_score              DOUBLE                              comment 'scan score',
    sev_high_score          DOUBLE                              comment 'High severity percentage of scan',
    sev_med_score           DOUBLE                              comment 'Med severity percentage of scan',
    sev_low_score           DOUBLE                              comment 'Low severity percentage of scan',    
    scan_status             ENUM('SUCCESS','UNSUCCESS')         comment 'scan status success or unsuccess',
    scan_comments           TEXT                                comment 'Any comments',
    tenant_enbaled_audit    TEXT                                comment 'All audit enabled for this tenant',
    tenant_options_used     TEXT                                comment 'All option of tenant vendor in use e.g. Oracle partitioning etc.',
    scan_start_time         TIMESTAMP               NOT NULL,
    scan_end_time           TIMESTAMP               NOT NULL
);

ALTER TABLE p$ht_tenant_scan ADD CONSTRAINT p$ht_tenant_scan_pk PRIMARY KEY ( tenant_id, scan_id, scan_seq_id);

CREATE TABLE p$ht_tenant_scan_detail (
    tenant_id               VARCHAR(10)             NOT NULL,
    scan_id                 VARCHAR(20)             NOT NULL,
    scan_seq_id             INTEGER                 NOT NULL,
    control_id              VARCHAR(20)             NOT NULL, 
    severity                ENUM('9','5','1')      comment 'Severity of control High/Medium/Low as it was during scan',
    additional_info         TEXT                             comment 'any additional info used to validate this control for e.g. control is an excpetion (we need to put change#), should also include any exclusion including default exclusion',
    expect_display          VARCHAR(1000)           NOT NULL comment 'Expected Dispaly; expected output results of this scan (REMOTE_LISTENER should be set to SCAN_NAME:PORT)',
    output_display          VARCHAR(1000)           NOT NULL comment 'Output display heading For e.g. "Lsiting all ports in use"',
    scan_output             TEXT                    NOT NULL comment 'Security scan output for this control',
    scan_status             ENUM('PASSED','FAILED','ERROR') 
                                                    comment 'Security scan result PASSED/FAILED/ERROR',
    scan_comments           TEXT                             comment 'Any comments', 
    scan_start_time         TIMESTAMP               NOT NULL,
    scan_end_time           TIMESTAMP               NOT NULL
);

ALTER TABLE p$ht_tenant_scan_detail ADD CONSTRAINT p$ht_tenant_secscan_detail_pk PRIMARY KEY ( tenant_id, scan_id, scan_seq_id, control_id);

CREATE TABLE p$ht_tenant_scan_config_detail (
    tenant_id               VARCHAR(30)             NOT NULL,
    scan_id                 VARCHAR(20)             NOT NULL,
    scan_seq_id             INTEGER                 NOT NULL,
    config_name             VARCHAR(30)             NOT NULL comment 'Kernel config name of tenant, For e.g. OS: all kernel name, DB: all parameter name present during scan',
    config_value            VARCHAR(100)            NOT NULL comment 'Kernel config value',
    comment                 TEXT,
    scan_time               DATE                    NOT NULL    
);

ALTER TABLE p$ht_tenant_scan_config_detail ADD CONSTRAINT p$ht_tenant_secscan_config_detail_pk PRIMARY KEY (tenant_id,  scan_id, scan_seq_id, config_name );

#Backup Policy of Tenant

CREATE TABLE ht$tenant_backup_policy (
    place_holder_dummy TEXT 
);

CREATE TABLE p$backup_policy (
    backup_policy_id        VARCHAR(10)              NOT NULL PRIMARY KEY,
    backup_target           VARCHAR(30)              NOT NULL COMMENT 'ORACLE/SQL SERVER/MYSQL/MONGO/LINUX-RHEL/LINUX-SUSE',
    backup_type             VARCHAR(30)              NOT NULL COMMENT 'PHYSICAL/LOGICAL',
    backup_utility          VARCHAR(30)              NOT NULL COMMENT 'RMAN/EXPDP or OTHER UTILITY (DB/OS Vendor specific)', 
    backup_component        VARCHAR(30)              NOT NULL COMMENT 'component to be backed up PHYSICAL >> FULL DB/INCREMENTAL/LOG, LOGICAL >>> FULL DB/SCHEMA/TABLE ',
    comments                TEXT 
);

CREATE TABLE p$backup_policy_detail (
    backup_schedule_id      VARCHAR(10)             NOT NULL,
    backup_policy_id        VARCHAR(10)             NOT NULL,
    Description             VARCHAR(100)            NOT NULL    comment 'Description of this backup schedule',
    backup_type             VARCHAR(30)             NOT NULL    comment 'Type of backup Full/Incremental/Log',
    backup_schedule         VARCHAR(30)             NOT NULL    comment 'Backup scheudle; daily (*), weekly (Day of week 0-6: W:6, every Sunday) / monthly (Date Of Month M:S/M:E/M:n --> Start/End/n=DOM, DOY date of year Y:S/Y:E/Y:n START/END/)' ,
    backup_utility          VARCHAR(30)             NOT NULL    comment 'utility/app to perform the backup',
    comments                TEXT 
);

ALTER TABLE p$backup_policy_detail add constraint p$bakup_policy_detail_pk PRIMARY KEY (backup_schedule_id, backup_policy_id);



# This table will hold all processes which is comprised of the task in the order need to be executed
# This can be called by manually or via a job

# Process info which will be called manually/schedule as a package

create table p$process(
    proc_id                 VARCHAR(20)             NOT NULL PRIMARY KEY,
    proc_name               VARCHAR(30)             NOT NULL comment 'Short name of process e.g. SEC_SCAN_ALL_HOSTS',
    proc_desc               VARCHAR(100)            NOT NULL comment 'detailed description of process',
    proc_type               VARCHAR(20)             NOT NULL comment 'Store process type, SECURITY SCAN, BACKUP etc.',
    proc_status             ENUM('ACTIVE','INACTIVE') DEFAULT 'INACTIVE'   
                                                             comment 'ACTIVE/INACTIVE',
    proc_work_unit          VARCHAR(20)                      comment 'Logical unit of work of this process which will be used to compute the total work during job run',
    proc_work_unit_call     JSON                             comment 'Method name to be used to get the total work neededduring job run',
    _change_history         JSON                             comment 'Store all the history '
);

create table p$process_task (
    task_id                 VARCHAR(20)             NOT NULL PRIMARY KEY,
    task_status             ENUM('ACTIVE','INACTIVE') DEFAULT 'INACTIVE'   comment 'ACTIVE/INACTIVE',
    proc_id                 VARCHAR(20)             NOT NULL,
    task_seq                INTEGER                 NOT NULL comment 'Process sequemces; step sequence of process ',
    library                 VARCHAR(200)            NOT NULL comment 'Library/module to be used for execution of this process step(seq)',
    cls                     VARCHAR(100)            NOT NULL comment 'Class which need to instantiated for execution of this process step(seq)',
    method                  VARCHAR(200)            NOT NULL comment 'Method from cls which need to executed for this process step(seq)',
    arguments               VARCHAR(1000)                    comment 'Argument which need to be passed to methd as stated in mehtod column',
    method_call_json        JSON                             comment 'Library, class, method and argument which need to be called to execute this step',
    work_unit               VARCHAR(20)                      comment 'Logical unit of work for this task which will be used to compute the total work during job run',
    work_unit_call          JSON                             comment 'Method name to be used to get the total work neededduring job run'
);

# Process run log

CREATE TABLE p$jobs_run_log (
    job_run_id              VARCHAR(20)             NOT NULL PRIMARY KEY comment 'Job run id; This can be Scan run id if job belongs to SCAN, backup job id if job belongs to backup',
    job_type                VARCHAR(100)            NOT NULL comment 'which job type this run belongs to i.e. SCAN/BACKUP etc.',
    proc_id                 VARCHAR(20)             NOT NULL comment 'process id which need to be executed',
    job_status              ENUM('PENDING','STARTED','IN-PROGRESS','COMPLETED-SUCCESS','COMPLETED-ERROR')   DEFAULT "PENDING" 
                                                             comment 'job status STARTED -> IN-PROGRESS -> COMPLETED SUCCESS/COMPLETED ERROR',
    start_time              TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                             comment 'Job start time',
    end_time                TIMESTAMP                        comment 'Job end time',
    elapsed_seconds         INTEGER                          comment 'Total elapsed seconds for this job',
    total_unit              INTEGER                          comment 'Total logical unit belongs to this job run For e.g. Security Scan Run for 100 host and 2 tenants each will result in 200 units which need to be completed',
    sofar                   INTEGER                          comment 'So far how many unit is completed, if we are tracking granular level, we can increment this unit with 1 for each scan control'
);

CREATE TABLE p$jobs_runtask_log (
    job_run_id              VARCHAR(20)             NOT NULL comment 'job run id; This can be Scan run id if job belongs to SCAN, backup job id if job belongs to backup',
    task_id                 VARCHAR(20)             NOT NULL comment 'process task id',
    task_status             ENUM('PENDING','STARTED','IN-PROGRESS','COMPLETED-SUCCESS','COMPLETED-ERROR')   DEFAULT "PENDING" comment 'job status STARTED -> IN-PROGRESS -> COMPLETED SUCCESS/COMPLETED ERROR',
    task_start_time         TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP,
    task_end_time           TIMESTAMP ,
    total_unit              INTEGER                          comment 'Total unit belongs to this job run For e.g. Security Scan Run for 100 host and 2 tenants each will result in 200 units which need to be completed',
    sofar                   INTEGER                          comment 'So far how many unit is completed, if we are tracking granular level, we can increment this unit with 1 for each scan control',
    last_heartbeat_time     TIMESTAMP                        comment 'Last time task updated the heart beat to ensure its alive'
);

alter table p$jobs_runtask_log add constraint p$jobs_runtask_log_pk primary key(job_run_id, task_id);
