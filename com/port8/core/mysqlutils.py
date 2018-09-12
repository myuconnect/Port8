import mysql.connector
from mysql.connector import connect, errors

from com.port8.core.singleton import Singleton
#from com.port8.core.environment import Environment
from com.port8.core.infrastructure import RestInfra
#from com.port8.core.loggingP8 import Logging
from com.port8.core.globals import Global
from com.port8.core.utility import Utility
from com.port8.core.error import *

class MysqlUtil(object, metaclass=Singleton):

	def __init__(self,logger = None):

		self.util = Utility()
		self.globals = Global()
		#self.env = Environment()
		self.dbResponse = self.util.getACopy(self.globals.Template['DBResponse'])
		self.infra = RestInfra()
		self.encryptKey = self.infra._Infra__bootStrapData['Main']['Key']
		
		if logger:
			self.logger = logger
		else:
			print('no logger is available, can not store logging information')
			self.logger = None
		# select @@port;
		# show variables where variable_name = 'port' 
		# select user();
		# insert json in mysql
		#	insert into temp values(json_array(json_object('id',1001,'when','2015-01-01 10:00:00','score',35), json_object('id',1002,'when','2015-02-01 10:00:00','score',45)) );

	def makeConnection(self,host, port, username, encryptPass, dbName, tzone = None):
		try:
			#print('pass',self.util.decrypt(self.env.encryptPass))
			conn = connect(host=host, port=port, user=username, password=self.util.decrypt(self.encryptKey, encryptPass), database=dbName)
			#print(conn)
			# we need to set the timezone as requested for this connection
			if tzone:
				conn.time_zone = '+00:00'
			return conn
		except errors.Error as error:
			#return self.util.buildDBResponse(self.globals.Error, None, None, error)
			raise
		except Exception as error:
			raise
			#return self.util.buildDBResponse(self.globals.Error, None, None, error)

	def getRepDBConnection(self):
		try:
			#print('pass',self.util.decrypt(self.env.encryptPass))
			conn = self.makeConnection(\
				self.infra.dbConfigData['host'], \
				self.infra.dbConfigData['port'], \
				self.infra.dbConfigData['user'], \
				self.infra.dbConfigData['password'], \
				self.infra.dbConfigData['database'])
			return conn

		except Exception as error:
			raise
			#return self.util.buildDBResponse(self.globals.Error, None, None, error)

	def execSelectSql(self, **args):
		'''
		Description: Execute Select statement
		Arguments: Key word arguments
					Conn : Connection handler
					SqlText : Sql to be executed
					SqlArgs : Arguments need to be passed to sql (optional), default = None (SqlArgs should be in dict)
					SqlOutput : Sqloutput Dict/Touple (optional), default = Touple
		Usage : execSelectSql(<connection>, <sql>, <sql args (optional)>, <sql output Dict/Touple (optional)> )
		Return : Array 

		internal --> #mySqlArgs = ','.join(list(map(lambda x: '%s', args)))

		'''
		try:
			myRequiredArgs = ['Conn','SqlText']

			#Validating arguments
			myArgValResult = self.util.valArguments(myRequiredArgs, args) 
			if myArgValResult['Status'] == self.globals.UnSuccess:
				raise InvalidArguments(myArgValResult['Message'])

			#extracting arguments
			myDBConn = args['Conn']
			mySqlText = args['SqlText']

			if not mySqlText.upper().startswith(('SELECT','INSERT','UPDATE','DELETE')):
				raise InvalidArguments('SQL statement can be SELECT/INSERT/UPDATE/DELETE only')

			mySqlArgs = args['SqlArgs'] if 'SqlArgs' in args else None
			mySqlOutput = args['SqlOutput'] if 'SqlOutput' in args else self.globals.SqlOutput['Default']

			if mySqlOutput not in self.globals.SqlOutput['All']:
				mySqlOutput = self.globals.SqlOutput['Default']

			# executing sql
			print('Executing sql >>>',mySqlText, mySqlArgs)
			myDBcur = myDBConn.cursor(buffered=True)
			totalRows = myDBcur.execute(mySqlText, mySqlArgs)

			if mySqlText.upper().startswith('SELECT'):
				if myDBcur.with_rows:	# if we got any data
					myTotalRows = myDBcur.rowcount
					#myCurDesc = myDBcur.description
					myAllColumns = myDBcur.column_names
					myRawData = myDBcur.fetchall()

					# build the sqloutput
					if mySqlOutput == self.globals.SqlOutput['Dict']:
						#myAllColumns = [column[0] for column in myCurDesc]
						myData = [dict(zip(myAllColumns, row)) for row in myRawData]
					else:
						myData = myRawData
				else:
					myData = None
			elif mySqlText.upper().startswith(('INSERT','UPDATE','DELETE')):
				pass

			myDBcur.close()
			return self.util.buildDBResponse(self.globals.Success, myData, myTotalRows)

		except errors.Error as error:
			#return self.util.buildDBResponse(self.globals.Error, None, None, error)
			raise
		except Exception as error:
			self.util.logError()
			raise
			#return self.util.buildDBResponse(self.globals.Error, None, None, error)

	def commitTrans(self, dbConn):
		try:
			dbConn.commit()
		except errors.Error as error:
			return self.util.buildDBResponse(self.globals.Error, None, None, error)
		except Exception as error:
			return self.util.buildDBResponse(self.globals.Error, None, None, error)

	def rollbackTrans(self, dbConn):
		try:
			dbConn.rollback()
		except errors.Error as error:
			return self.util.buildDBResponse(self.globals.Error, None, None, error)
		except Exception as error:
			return self.util.buildDBResponse(self.globals.Error, None, None, error)

	def buildMarkerForSql(self, sqlText, argList, marker):
		sqlArgMarker = ', '.join(list(map(lambda x: marker, args)))
		return sqlText % sqlArgMarker

	def buildDynaSql(self, colList, tableList, criteria):
		if colList:
			mySql = colList

			# adding tables to sql 
			for indx, table in enumerate(tableList):
				if indx > 0:
					# found more than one table, we need to add ',' in from clause to seperate tables
					mySql = ''.join([mySql, ' , ', table ])
				else:
					mySql = ''.join([mySql, ' from ' , table ])

			# adding where clause 
			if criteria:
				mySql = ''.join([mySql, ' where ' , criteria])

			return mySql
if __name__ == "__main__":
	import socket
	mysql = MysqlUtil()
	#myHost = socket.gethostname()
	myHost='localhost'
	myPort = 3306
	myUser='root'
	myTextPass = 'root'
	myDbName = 'p8rep'
	myEncryptPass = mysql.util.encrypt(mysql.encryptKey,'root')
	#print(myHost,myPort,myUser,myTextPass,myEncryptPass,myDbName)
	conn = mysql.makeConnection(myHost, myPort,myUser,myEncryptPass, myDbName)
	print('connection',conn)

	data = mysql.execSelectSql(Conn = conn, SqlText = mysql.globals.allTenantAvgScoreSql, SqlArgs=None, SqlOutput = mysql.globals.SqlOutput['Dict'])
	print('Status >> ', data['Status'], 'Rows >>', data['Rows'], 'Type >>', type(data['Data']), 'Data >>', data['Data'])
	for row in data['Data']:
		print(row)

	myHost = {'HostId':'H10001'}
	data = mysql.execSelectSql(Conn = conn, SqlText = mysql.globals.allHostTenantAvgScoreSql, SqlArgs = myHost, SqlOutput = mysql.globals.SqlOutput['Dict'])
	print('Status >> ', data['Status'], 'Rows >>', data['Rows'], 'Type >>', type(data['Data']), 'Data >>', data['Data'])
	for row in data['Data']:
		print(row)
	
	myHost = {'TenantVendor':'Oracle'}
	data = mysql.execSelectSql(Conn = conn, SqlText = mysql.globals.allVedorTenantScoreSql, SqlArgs = myHost, SqlOutput = mysql.globals.SqlOutput['Dict'])
	print('Status >> ', data['Status'], 'Rows >>', data['Rows'], 'Type >>', type(data['Data']), 'Data >>', data['Data'])
	for row in data['Data']:
		print(row)

	myHost = {'TenantVendor':'Oracle','VendorProduct' : 'Oracle'}
	data = mysql.execSelectSql(Conn = conn, SqlText = mysql.globals.allVedorProdTenantScoreSql, SqlArgs = myHost, SqlOutput = mysql.globals.SqlOutput['Dict'])
	print('Status >> ', data['Status'], 'Rows >>', data['Rows'], 'Type >>', type(data['Data']), 'Data >>', data['Data'])
	for row in data['Data']:
		print(row)

	#self.allHostTenantAvgScoreSql
	#print(data['Data'])
