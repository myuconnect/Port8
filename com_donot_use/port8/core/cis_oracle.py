from com.port8.core.environment import Environment
from com.port8.core.singleton import Singleton
from com.port8.core.logging import Logging
from com.port8.core.globals import Global
from com.port8.core.utility import Util


class CisOracle(object, metaclass=Singleton):
	def __init__(self):
		pass

	def performScan(self, oracleSid = 'ALL'):
		pass

	def valPatch(self, dbConn, psu):
		pass

	def valUsersWDefPass(self, dbConn):
		pass

	def valSampleSchema(self, dbConn):
		pass

	def valListenerAttr(self, dbConn):
		pass

	def valDBParam(self, dbConn):
		pass

	def valDBProfRes(self, dbConn):
		pass

	def valUserExternPasswd(self, dbConn):
		pass

	def valUserWDefProf(self, dbConn):
		pass

	def valPublicPrivs(self, dbConn):
		pass

	def valUnauthPrivs(self, dbConn):
		pass

	def valUnAuthTabPrivs(self, dbConn):
		pass

	def valUserMigTable(self, dbConn):
		pass

	def valTrdnlAudit(self, dbConn):
		pass