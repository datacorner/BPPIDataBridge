__author__ = "datacorner.fr"
__email__ = "admin@datacorner.fr"
__license__ = "MIT"

from pipelite.interfaces.IDataSource import IDataSource 
import pipelite.constants as C
from bppidb.bppi.bppiRepository import bppiRepository

CFGFILES_DSOBJECT = "bppiDS.json"
CFGPARAMS_SERVER = "server"
CFGPARAMS_TOKEN = "token"
CFGPARAMS_TABLE = "table"
CFGPARAMS_TODOS = "todos"
DS_JSON_VALIDATION_PKGLOC = "bppidb." + C.RESOURCE_PKGFOLDER_DATASOURCES

class bppiDS(IDataSource):
    def __init__(self, config, log):
        super().__init__(config, log)

    @property
    def parametersValidationFile(self):
        filename = self.getResourceFile(DS_JSON_VALIDATION_PKGLOC, CFGFILES_DSOBJECT)
        return str(filename)
    
    def initialize(self, cfg) -> bool:
        """ initialize and check all the needed configuration parameters
        Args:
            cfg (objConfig) : params for the data source.
                example: {'separator': ',', 'filename': 'test2.csv', 'path': '/tests/data/', 'encoding': 'utf-8'}
        Returns:
            bool: False if error
        """
        try:
            self.server = cfg.getParameter(CFGPARAMS_SERVER, C.EMPTY)
            self.token = cfg.getParameter(CFGPARAMS_TOKEN, C.EMPTY)
            self.table = cfg.getParameter(CFGPARAMS_TABLE, C.EMPTY)
            self.todos = cfg.getParameter(CFGPARAMS_TODOS, [])
            return True
        except Exception as e:
            self.log.error("{}".format(e))
            return False

    def write(self, dataset) -> bool:
        # Initialize repository
        bppiRepo = bppiRepository(log=self.log)
        bppiRepo.initialize(server=self.server, token=self.token)
        # load data files
        if (bppiRepo.load(dataset, self.table)):
            # Execute To DO if needed
            bppiRepo.executeToDo(todos=self.todos, table=self.table)
        return True