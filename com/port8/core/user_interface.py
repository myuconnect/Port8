import os,json,sys, logging, time, datetime
from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utility import Utility
from com.port8.core.mysqlutils import MysqlUtil
from com.port8.core.infrastructure import RestInfra
from jsonschema import validate
from com.port8.core.error import *


class Interface(object, metaclass=Singleton):
	def __init__(self):
		self.utility = Utility()
		self.globals = Global()
		self.infra = RestInfra()
		self.logger = self.infra.Logger
			
		self.repDB = MysqlUtil(self.logger)
		self.repConn = self.repDB.getRepDBConnection()

	def getScanOverview(self, request):
		try:
			#we are expecting security key as request

			# Average score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.avgScoreSql, SqlArgs=None, SqlOutput = self.globals.SqlOutput['Dict'])

			if dbResult['Status'] != self.globals.Success:
				return dbResult

			myAvgScore = dbResult['Data']

			# All location average score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.allLocAvgScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])
			
			if dbResult['Status'] != self.globals.Success:
				return dbResult

			myAllLocAvgScore = dbResult['Data']

			# All host average score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.allHostScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			if dbResult['Status'] != self.globals.Success:
				return dbResult

			myAllHostAvgScore = dbResult['Data']

			# All host tenant score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.allHostTenantScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			if dbResult['Status'] != self.globals.Success:
				return dbResult

			myAllHostTenantScore = dbResult['Data'] # we need to add this in formating

			# All tenant average score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.allTenantAvgScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			if dbResult['Status'] != self.globals.Success:
				return dbResult

			myAllTenantAvgScore = dbResult['Data']

			# All location tenant average score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.allLocTenantAvgScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			if dbResult['Status'] != self.globals.Success:
				return dbResult

			myAllLocTenantAvgScore = dbResult['Data']

			# Building response
			myResponse = self.utility.buildSummScanResponse(myAvgScore[0], myAllLocAvgScore, myAllHostAvgScore, myAllTenantAvgScore, myAllLocTenantAvgScore)

			return myResponse
		except Exception as e:
			raise e

	def getAllHost(self, request):
		'''
		dc_info = 'data center'
		os = 'RHEL/ms/oel'
		os_ver = 'version'
		location = 'location'
		'''
		try:
			myReqdArgs = []
			self.utility.validateArgs(request)

		except Exception as error:
			raise error

	def getAllTenants(self, request):
		try:
			pass
		except Exception as error:
			raise e

	def getTenantScan(self, **kwargs):
		pass

	def getScanScore(self, **kwargs):
		pass

	def getTenantConfig(self, **kwargs):
		pass

	def getHostConfig(self, **kwargs):
		pass

	def addCtrlException(self, **kwargs):
		pass

	def addCtrlExclusion(self, **kwargs):
		pass

