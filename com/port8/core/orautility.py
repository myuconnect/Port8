import cx_Oracle
from com.port8.core.environment import Environment
from com.port8.core.singleton import Singleton
from com.port8.core.logging import Logging
from com.port8.core.globals import Global
from com.port8.core.utility import Util

class OraUtil(object, metaclass=Singleton):
	def __init__(self):

		if self.util.getHostType == 'SUN':
			self.oratab = '/var/opt/oratab'
		else:
			self.oratab = '/etc/oratab'

		if not self.util.isFileExist(self.oratab):
			raise BootstrapError('oratab file [{file}] is missing !!!'.format(file=self.oratab))
		self.globals = Global()

	def makeDsnTns4Sid(self, host, port, oracleSid):
		'''
		Decription: Returns DSN/TNS informartion for given host, port and sid
		Usage: cancelSql(<host>, <port>, <sid>)
		'''	
		try:
			return cx_Oracle.makdedsn(host=hsot, port=port, sid = oracleSid)
		except Exception as err:
			raise err

	def makeDsnTns4Srvc(self, host, port, serviceName):
		'''
		Decription: Returns DSN/TNS informartion for given host, port and servicename
		Usage: cancelSql(<host>, <port>, <srvcname>)
		'''	
		try:
			return cx_Oracle.makdedsn(host=hsot, port=port, service_name = serviceName)
		except Exception as err:
			raise err

	def getConnAsSysdba(self, oracleSid):
		'''
		Decription: connect to local instance as sysdba
		Usage: cancelSql(<host>, <port>, <srvcname>)
		'''	
		if self.isSidInOraTab(oracleSid):
			self.setOracleEnv(oracleSid)
			return cx_Oracle.connect(mode = cx_Oracle.SYSDBA)
 
	def getConnection(self, host, port, serviceName, username, passwd, sysdba = False):
		'''
		Decription: connect to local instance as sysdba
		Usage: cancelSql(<host>, <port>, <srvcname>)
		'''	
		dsn = self.makeDsnTns4Srvc(host, port, serviceName)

		if sysdba:
			return cx_Oracle.connect(user = username, password = passwd, dsn = dsn, mode = cx_Oracle.SYSDBA)
		else:
			return cx_Oracle.connect(user = username, password = passwd, dsn = dsn)
			

	def isConnectionAlive(self, dbconn):
		'''
		Decription: Checks if specified db connection is still alive 
		Usage: isConnectionAlive(<target_db_conn_handler>)
		'''
		try:
			dbConn.ping()
			return True 
		except cx_Oracle.InterfaceError as err:
			return False
		except Exception as e:
			raise e

	def cancelSql(self, dbConn):
		'''
		Decription: Cancel long running sql to a specified connection handle
		Usage: cancelSql(<target_db_conn_handler>)
		'''
		try:
			if self.isValidConnection(dbConn):
				dbConn.cancel() 
		except cx_Oracle.InterfaceError as err:
			return False
		except Exception as e:
			raise e

	def getSidInfoFromOratab(self, oracleSid):
		'''
		Description: Get Oracle sid information from oratab file
		Usage: getSidInforFromOraTab(<oracle_sid>)
		'''
		try:
			return self.util.getLineForPattern(self.oratab, oracleSid,1,'STARTWITH')

		except Exception as e:
			raise e

	def isSidInOraTab(self, oracleSid):
		'''
		Description: checks if oracle sid argument is in oratab file
		Usage: isSidInOraTab(<oracle_sid>)
		'''
		return oracleSid in self.getSidInfoFromOratab(oracleSid)

	def setOracleEnv(self, oracleSid):
		'''
		Description: Sets Oracle environment (ORACLE_HOME, ORACLE_SID, add ORACLE_HOME/bin to exisitn path) at local host.
					 Oracle sid must be present in oratab file
		Usage: setOracleEnv(<oracle_sid>)
		'''
		try:
			if self.isSidInOraTab(oracleSid):
				curOraenvVal = self.util.getEnv('ORAENV_ASK')
				self.util.setEnv('ORAENV_ASK','NO')
				self.util.seyEnv('ORACLE_SID',oracleSid)
				self.util.runOsCmd(self.setOraEnvOSCmd)
				self.util.setEnv('ORAENV_ASK',curOraenvVal)
		except Exception as e:
			raise e

	def execSelectSql(self, dbConn, sqlText, sqlParam, outputType = 'WO_COLUMN'):
		try:
			if outputType not in [self.globals.outputTypeWCOLUMN, self.globals.outputTypeWOCOLUMN]:
				raise ValueError 

			if not self.isConnectionAlive(dbConn):
				raise ValueError('DB Connection is not alive >>> {conn}'.format(conn = dbConn))

			dbCursor = dbconn.cursor() 
			dbCusor.execute(sqlText, sqlParam)

			if outputType == self.globals.outputTypeWCOLUMN:
				#will build the dict for the result sets,column name --> key, data --> value
			    columns = [i[0] for i in dbCursor.description]
			    dbResult = [dict(zip(columns, row)) for row in dbCursor]
			else:
				dbResult = dbCursor.fetchall()[0]

			return dbResult

		except Exception as error:
			raise error
