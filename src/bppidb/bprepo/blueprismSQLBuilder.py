__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import bppidb.constants as C
from .genericSQLBuilder import genericSQLBuilder

NO_FILTER = "1=1"

class blueprismSQLBuilder(genericSQLBuilder):
    def setConnectionParams(self, 
                            processName=C.EMPTY, 
                            bpStageTypes=[], 
                            includeVBO=True, 
                            unicode=False,
                            deltaDate=C.EMPTY):
        self.__processName = processName  
        self.__bpStageTypes = bpStageTypes  
        self.__includeVBO = includeVBO        
        self.__unicode = unicode
        self.__deltaDate = deltaDate

    def setSubstDict(self) -> dict:
        """ returns a dictionnary with all the values to substitute in the SQL query
        Returns:
            dict: dictionnary with values
        """
        try: 
            deltasql = NO_FILTER
            novbo = NO_FILTER

            # Build the filters on the VBO only
            if (not self.__includeVBO):
                novbo = C.BPLOG_PROCESSNAME_COL + " IS NULL"

            # Date Filtering and/or DELTA vs FULL
            if (self.__deltaDate != C.EMPTY):
                self.log.info("DELTA Load requested - from <" + str(self.__deltaDate) + ">")
                # DELTA LOAD (get date from file first)
                deltasql = " FORMAT(" + C.BPLOG_FILTERDATE_COL + ",'yyyy-MM-dd HH:mm:ss') >= '" + self.__deltaDate + "'"
            else:
                self.log.info("FULL Load requested")

            # BP Logs in unicode ? (default no)
            if (self.__unicode):
                tablelog = C.BPLOG_LOG_UNICODE
            else:
                tablelog = C.BPLOG_LOG_NONUNICODE
                
            # Finalize the SQL Query by replacing the parameters
            valuesToReplace = { 
                                "processname" : self.__processName, 
                                "stagetypefilters" : ",".join(str(n) for n in self.__bpStageTypes), 
                                "onlybpprocess" : novbo, 
                                "delta" : deltasql, 
                                "tablelog" : tablelog
                                }
            return valuesToReplace

        except Exception as e:
            self.log.error("Unable to build the Blue Prism Query " + str(e))
            return ""