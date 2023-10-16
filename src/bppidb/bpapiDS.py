__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import bppidb.constants as C
import pipelite.constants as P
import pandas as pd
import requests 
import urllib.parse
import warnings
from pipelite.baseobjs.BODataSource import BODataSource 
from pipelite.plDataset import plDataset

# BLUE PRISM API
PBAPI_VER = "/api/v7"
BPAPI_SESSIONS_LIST = "/sessions"
BPAPI_SESSION_HEAD = "/sessions/{}"
BPAPI_SESSION_LOGS = "/sessions/{}/logs"
BPAPI_SESSION_PARAMS = "/sessions/{}/parameters"

CFGFILES_URLAUTH = "url-auth"
CFGFILES_SSL = "ssl"
CFGFILES_PAGESIZE = "pagesize"
CFGFILES_CLIENTID = "client-id"
CFGFILES_CLIENTSECRET = "client-secret"
CFGFILES_URLAPI = "url-api"
CFGPARAMS_PROCESS = "processname"

PAGESIZE_DEFAULT = 300

CFGFILES_DSOBJECT = "bpapiDS.json"
DS_JSON_VALIDATION_PKGLOC = "bbpidb." + P.RESOURCE_PKGFOLDER_DATASOURCES
AUTH_TOKEN_SUFFIX_URL = "/connect/token"

warnings.filterwarnings('ignore')

class bpAPIExtractor(BODataSource):

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
            self.__urlAuth = cfg.getParameter(CFGFILES_URLAUTH, C.EMPTY)
            self.__sslCheck = cfg.getParameter(CFGFILES_SSL, False)
            self.__pageSize = cfg.getParameter(CFGFILES_PAGESIZE, PAGESIZE_DEFAULT)
            self.__clientID = cfg.getParameter(CFGFILES_CLIENTID, C.EMPTY)
            self.__secret = cfg.getParameter(CFGFILES_CLIENTSECRET, C.EMPTY)
            self.__urlApi = cfg.getParameter(CFGFILES_URLAPI, C.EMPTY) 
            self.__bpProcessName = cfg.getParameter(CFGPARAMS_PROCESS, C.EMPTY)
            return True
        except Exception as e:
            self.log.error("{}".format(e))
            return False

    def __buildAPIURL(self):
        return self.__urlApi + C.PBAPI_VER

    def __getSSLVerification(self):
        return (self.__sslCheck == C.YES)

    def __getPageSize(self):
        return self.__pageSize

    def __getAccessToken(self):
        """ OAuth2 protocol usage with the Blue Prism API to get the access token
        Returns:
            str: Blue Prism API Access Token
        """
        try:
            self.log.debug("BP API - Get the Blue Prism API access token")
            # Obtain an access token using client credentials grant
            token_params = {
                "grant_type": "client_credentials",
                "client_id": self.__clientID,
                "client_secret": self.__secret,
            }
            token_response = requests.post(self.__urlAuth + AUTH_TOKEN_SUFFIX_URL, 
                                           data=token_params, 
                                           verify=self.__getSSLVerification())
            token_data = token_response.json()
            self.log.debug("BP API - Blue Prism Access Token has been returned successfully")
            # The access token can be extracted from the response
            return token_data["access_token"]
        
        except Exception as e:
            self.log.error("bpAPIReader.__getAccessToken() -> Unable to get the Blue Prism API Access Token, " + str(e))
            return None

    def __getSessionIDList(self, access_token):
        """ Get the list of Blue Prism Sessions,by using the access token for making authorized API requests
        Args:
            access_token (str): Blue Prism API Token access
        Returns:
            DataFrame: List of Session ID
        """
        try:
            self.log.debug("BP API - Get the Blue Prism session list")
            headers = {
                "Authorization": "Bearer " + access_token,
            }
            api_endpoint = self.__buildAPIURL() + C.BPAPI_SESSIONS_LIST
            params = { 'sessionParameters.processName.eq': self.__bpProcessName }
            api_endpoint += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            api_response = requests.get(api_endpoint, 
                                        headers=headers, 
                                        verify=self.__getSSLVerification())
            if (api_response.status_code == C.HTTP_API_OK):
                df = pd.DataFrame.from_dict(api_response.json()["items"], orient='columns')
                self.log.debug("BP API - {} sessions have been returned.".format(len(df)))
                return df["sessionId"]
            else:
                self.log.error("bpAPIReader.__getSessionIDList() -> API Call error, {}".format((api_response.status_code)))
                return pd.DataFrame()
            
        except Exception as e:
            self.log.error("bpAPIReader.__getSessionIDList() -> Unable to get the Blue Prism session list, " + str(e))
            return pd.DataFrame()
 
    def __getSessionDetails(self, access_token, sessionID):
        """ Returns the global informations on a Blue Prism Session (header)
        Args:
            access_token (str): Blue Prism API Token access
            sessionID (str): Blue Prism Session ID
        Returns:
            DataFrame: Session details
        """
        try:
            self.log.debug("BP API - Get the Blue Prism session information (header)")
            api_endpoint = (self.__buildAPIURL() + C.BPAPI_SESSION_HEAD).format(sessionID)
            headers = {
                "Authorization": "Bearer " + access_token,
            }
            api_response = requests.get(api_endpoint, 
                                        headers=headers, 
                                        verify=self.__getSSLVerification())
            if (api_response.status_code == C.HTTP_API_OK):
                return api_response.json()
            else:
                raise Exception("API Call error, {}".format((api_response.status_code)))
            
        except Exception as e:
            self.log.error("bpAPIReader.__getSessionDetails() -> Unable to get the Blue Prism session global info, " + str(e))
            return pd.DataFrame()
        
    def __getSessionLogs(self, access_token, sessionID):
        """ Returns the all the sessions logs. The API works with pages (Max 1000 logs per page), so we've to loop into the returned pages.
        Args:
            access_token (str): Blue Prism API Token access
            sessionID (str): Blue Prism Session ID
        Returns:
            DataFrame: Session logs
        """
        try:
            self.log.debug("BP API - Get the Blue Prism session [{}] details".format(sessionID))
            loop_on_page = True
            all_logs = pd.DataFrame()
            next_page_token = ""
            iteration = 1
            # The API returns logs per pages (Max 1000 logs per page)
            while (loop_on_page):
                self.log.debug("BP API - Get logs per page, iteration N°{}".format(iteration))
                # Build URL API Call
                api_endpoint = (self.__buildAPIURL() + C.BPAPI_SESSION_LOGS).format(sessionID)
                params = { 'sessionLogsParameters.itemsPerPage': self.__getPageSize() }
                if (next_page_token != ""):
                    params.update( { "sessionLogsParameters.pagingToken" : next_page_token })
                api_endpoint += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

                headers = {  "Authorization": "Bearer " + access_token }
                api_response = requests.get(api_endpoint, 
                                            headers=headers, 
                                            verify=self.__getSSLVerification())
                # Aggregate the logs (all pages)
                if (api_response.status_code == C.HTTP_API_OK):
                    df = pd.DataFrame.from_dict(api_response.json()["items"], orient='columns')
                    all_logs = pd.concat([all_logs, df]) 
                    next_page_token = api_response.json()["pagingToken"]
                if (next_page_token == None or api_response.status_code != C.HTTP_API_OK):
                    self.log.debug("bpAPIReader.__getSessionInfos() -> No more pages")
                    loop_on_page = False
                iteration += 1
            self.log.debug("BP API - {} sessions details (steps/stages) have been returned.".format(len(all_logs)))
            return all_logs
        
        except Exception as e:
            self.log.error("bpAPIReader.__getSessionLogs() -> Unable to get the Blue Prism session [{}] details, {}".format(sessionID, str(e)))
            return pd.DataFrame()

    def __getSessionParameters(self, access_token, sessionID):
        """ Returns the all the sessions parameters. 
            *** In progress **
        Args:
            access_token (str): Blue Prism API Token access
            sessionID (str): Blue Prism Session ID
        Returns:
            json: parameters
        """
        ssl_verification = self.__getSSLVerification()
        api_endpoint = (self.__buildAPIURL() + C.BPAPI_SESSION_PARAMS).format(sessionID)
        headers = {
            "Authorization": "Bearer " + access_token,
        }
        api_response = requests.get(api_endpoint, headers=headers, verify=ssl_verification)
        return api_response.json()

    def read(self) -> plDataset:
        """ Returns all the BP Repository data in a df
        Returns:
            bool: False is any trouble when reading
        """
        try:
            access_token = self.__getAccessToken()
            if (access_token != None):
                sessionIDList = self.__getSessionIDList(access_token)
                logs = plDataset()
                # Aggregate the logs from all the sessions
                for session in sessionIDList:
                    self.log.debug("BP API - Collect logs from session {} ...".format(session))
                    session_info = self.__getSessionDetails(access_token, session)
                    session_logs = self.__getSessionLogs(access_token, session)
                    # Add Session log data
                    session_logs["ResourceName"] = session_info['resourceName']
                    session_logs["status"] = session_info['status']
                    session_logs["SessionID"] = session
                    logs.concatWith(session_logs)
                    #logs = pd.concat([logs, session_logs]) 
                    self.log.debug("BP API - session {} logs collected successfully, Total: {} rows/logs".format(session, logs.count))
            return logs
        
        except Exception as e:
            self.log.error("bpAPIReader.read() Error: " + str(e))
            return plDataset()