__author__ = "datacorner.fr"
__email__ = "admin@datacorner.fr"
__license__ = "MIT"

import datetime
import importlib.resources

from pipelite.datasources.odbcDS import odbcDS 
import pipelite.constants as P
from pipelite.plDataset import plDataset

from bppidb.bprepo.blueprismSQLBuilder import blueprismSQLBuilder
from bppidb.bprepo.bpLogsProcessing import bpLogsProcessing
import bppidb.constants as C

CFGFILES_DSOBJECT = "bprepoDS.json"
CFGFILES_CONNSTRING = "connectionstring"
CFGPARAMS_PROCESS = "processname"
CFGPARAMS_PARAMETERS = "parameters"
CFGPARAMS_STAGETYPES = "stagetypefilters"
CFGFILES_VBO = "includevbo"
CFGPARAMS_UNICODE = "unicode"
CFGPARAMS_DELTAFILE = "delta-file"
BPQUERY_PKG_LOCATION = "bppidb.config"
DS_JSON_VALIDATION_PKGLOC = "bppidb." + P.RESOURCE_PKGFOLDER_DATASOURCES

class bprepoDS(odbcDS):

    @property
    def parametersValidationFile(self):
        filename = self.getResourceFile(DS_JSON_VALIDATION_PKGLOC, CFGFILES_DSOBJECT)
        return str(filename)

    @property
    def getQueryFile(self):
        return importlib.resources.files(BPQUERY_PKG_LOCATION).joinpath(C.BPLOG_INI4SQL)

    def initialize(self, cfg) -> bool:
        """ initialize and check all the needed configuration parameters
        Args:
            cfg (objConfig) : params for the data source.
                example: {'separator': ',', 'filename': 'test2.csv', 'path': '/tests/data/', 'encoding': 'utf-8'}
        Returns:
            bool: False if error
        """
        try:
            self.connectionString = cfg.getParameter(CFGFILES_CONNSTRING, C.EMPTY)
            self.processName = cfg.getParameter(CFGPARAMS_PROCESS, C.EMPTY)
            self.parameters = cfg.getParameter(CFGPARAMS_PARAMETERS, C.EMPTY)
            self.stagetypes = cfg.getParameter(CFGPARAMS_STAGETYPES, [])
            self.vbo = cfg.getParameter(CFGFILES_VBO, C.EMPTY)
            self.unicode = cfg.getParameter(CFGPARAMS_UNICODE, C.EMPTY)
            self.deltaFile = cfg.getParameter(CFGPARAMS_DELTAFILE, C.EMPTY)
            return True
        except Exception as e:
            self.log.error("{}".format(e))
            return False
        
    def __getDeltaTag(self) -> str:
        """ Get the last load date to use for the delta loading (when requested)
        Returns:
            _type_: date in straing format
        """
        if (self.deltaFile != C.EMPTY):
            try:
                with open(self.deltaFile, "r") as file:
                    fromdate = file.read()
                return fromdate
            except:
                self.log.error("Unable to read/get the tagged delta date")
                return C.EMPTY
        else:
            return C.EMPTY

    def __updDeltaTag(self):
        """ Update the date for the next delta load
        """
        if (self.deltaFile != C.EMPTY):
            try:
                with open(self.deltaFile, "w") as file: # store in the delta file the latest delta load 
                    file.write(datetime.datetime.now().strftime(C.BP_DELTADATE_FMT))
            except:
                self.log.error("Unable to write the tagged new delta date")

    @property
    def bpQuery(self) -> str:
        """Build the SQL Query to get the BP logs against the BP repository
            The BP Logs SQL query is stored in the bp.config file and can be customized with several args:
                * {attrxml}: Name of the INPUT/OUTPUT attributes columns (XML format)
                * {processname}: Process Name in Blue Prism
                * {stagetypefilter}: list of stage to filter out
                * {delta}: Delta loading condition on datetime (Between or < >)
                * {tablelog}: Name of the Log table (unicode or not unicode)
        Returns:
            str: built SQL Query
        """
        try: 
            # Build the Query
            sqlBuilder = blueprismSQLBuilder(log=self.log,
                                            query=self.getQueryFile)
            sqlBuilder.setConnectionParams(bpStageTypes=self.stagetypes,
                                           processName=self.processName,
                                           includeVBO=self.vbo,
                                           unicode=self.unicode,
                                           deltaDate=self.__getDeltaTag())
            sql = sqlBuilder.build()
            self.log.debug("SQL -> {}".format(sql))
            return sql
        except Exception as e:
            self.log.error("Unable to build the Blue Prism Query " + str(e))
            return C.EMPTY

    def read(self) -> plDataset:
        """ Returns all the data in a DataFrame format
        Returns:
            pd.DataFrame(): dataset read
        """
        # get the bru logs from the BP repository
        originalDS = self.read_sql(self.bpQuery)

        if (originalDS.count > 0):
            # -- Transform the logs --
            logs = bpLogsProcessing(dfLogs=originalDS.get(), log=self.log)
            # Filter out the df by selecting only the Start & End (main page / process) stages if requested
            logs.removeStartEndStages(C.BP_MAINPAGE_DEFAULT)
            # Get the attributes from the BP logs
            logs.addAttributes(",".join(str(n) for n in self.parameters))
            # Add the stage identifier / event mapping needs
            logs.createStageID()
            # drop working or obsolete fields
            logs.dropFields([C.COL_OBJECT_TAB, C.BPLOG_OBJTYPE_COL, C.BPLOG_OBJNAME_COL])

            newLogs = plDataset()
            newLogs.set(logs.content)

        # Update the date for the next delta load
        self.__updDeltaTag()

        return newLogs