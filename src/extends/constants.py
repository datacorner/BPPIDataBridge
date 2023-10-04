EMPTY = ""

# BPPI API
API_1_0 = "/api/ext/1.0/"
API_REPOSITORY_CONFIG = "repository/repository-import-configuration"
API_SERVER_UPLOAD_INFOS = "repository/{}/file/upload-url"
API_SERVER_LOAD_2_REPO = "repository/{}/load"
API_PROCESSING_STATUS = "processing"
API_EXECUTE_TODO = "repository/{}/execute-todo-list"
API_DEF_WAIT_DURATION_SEC = 2
API_DEF_NB_ITERATION_MAX = 60
API_STATUS_IN_PROGRESS = "IN_PROGRESS"
API_STATUS_ERROR = "ERROR"
API_BLOC_SIZE_LIMIT = 10000 # Same limitation as the current API call via java

# Blue Prism stuff
BPLOG_FIELD_LOGID = "logId"
BPLOG_FIELD_SESSIONID = "SessionID"
BPLOG_STARTDATETIME_COL = "resourceStartTime"       # Name of the Start Date & time column in the BP Repo
BPLOG_FILTERDATE_COL = "LOG.startdatetime"
BPLOG_RESOURCENAME_COL = "ResourceName"             # DW name
BPLOG_STAGETYPE_COL = "stageType"                   # Name of the stagetype column in the BP Repo
BPLOG_STAGENAME_COL = "stageName"                   # Name of the stagename column in the BP Repo
BPLOG_RESULT_COL = 'result'                         # Execution result
BPLOG_PAGENAME_COL = "pagename"                     # Only in PB repo
BPLOG_ACTIONNAME_COL = "actionname"                 # Only in PB repo
BPLOG_OBJTYPE_COL = "OBJECT_TYPE"                   # Only in PB repo
BPLOG_OBJNAME_COL = 'OBJECT_NAME'                   # Only in PB repo
BPLOG_PAGENAME_COL = "pagename"                     # Name of the pagename column in the BP Repo
BPLOG_PROCESSNAME_COL = "processname"               # Name of the process name column in the BP Repo
BPLOG_ATTRIBUTE_COL = "attributexml"                # Name of the attributexml column in the BP Repo
BPLOG_LOG_UNICODE = "BPASessionLog_Unicode"         # BP Log table name for unicode
BPLOG_LOG_NONUNICODE = "BPASessionLog_NonUnicode"   # BP Log table name for non unicode
BPLOG_INI4SQL = "bprepo.sql"                        # File which contains the BP SQL Query
BP_STAGE_START = "Start"                            # Name of the BP Start stage
BP_STAGE_END = "End"                                # Name of the BP End stage
BP_MAINPAGE_DEFAULT = "Main Page"                   # Name of the BP Main Page (process)
BP_DEFAULT_DELTAFILE = "bpdelta.tag"                # Default filename for the delta tag
BP_DELTADATE_FMT = "%Y-%m-%d %H:%M:%S"              # Delta date format %Y-%m-%d %H:%M:%S
COL_STAGE_ID = "stageId"
COL_OBJECT_TAB = "OBJECT_TAB"