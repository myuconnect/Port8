from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utility import Utility
from com.port8.bpm.user_interface_utils import InterfaceUtil
from com.port8.core.infrastructure import RestInfra
from com.port8.core.error import *
from com.port8.core.security import Security

class Interface(object, metaclass=Singleton):
	def __init__(self):
		self.utility = Utility()
		self.globals = Global()
		self.infra = RestInfra()
		self.logger = self.infra.Logger
			
		self.ui_util = InterfaceUtil()
		self.security = Security()

	def getLandingPageData(self):
		'''
		Description: Returns data for landing page, this method should be called after credential authentication
		Arguments: Security key
		Returns: Response ...
			{
				"Status" : "", 
				"Message" : "",
				"Data" : 
					[
						"AvgScore" : 75.00,
						"LocAvgScore" : [],
						"LocVendorScore" : [],
						"LocHostTenant" : [],
						"LocHostTenant" : []
					]
			}
		'''
		try:
			# initialize
			myLandingPageData = self.utility.getACopy(self.globals.Template['LandingPage'])

			# Get all the data
			#Avg overall Score
			dbResult = self.ui_util._InterfaceUtil__getAvgScore()
			if dbResult['Status'] != self.globals.Success:
				# build error response and return
				return
			else:
				avgScore = dbResult['Data']

			#Avg loc score
			dbResult = self.ui_util._InterfaceUtil__getAvgLocScore()
			if dbResult['Status'] != self.globals.Success:
				# build error response and return
				return
			else:
				avgLocScore = dbResult['Data']

			#Avg Vendor score
			dbResult = self.ui_util._InterfaceUtil__getAvgVendorScore()
			if dbResult['Status'] != self.globals.Success:
				return
			else:
				avgVendorScore = dbResult['Data']

			#Avg Loc Vendor score
			dbResult = self.ui_util._InterfaceUtil__getAvgLocVendorScore()
			if dbResult['Status'] != self.globals.Success:
				return
			else:
				avgLocVendorScore = dbResult['Data']

 			#Avg Host score
			dbResult = self.ui_util._InterfaceUtil__getAvgHostScore()
			if dbResult['Status'] != self.globals.Success:
				# build error response and return
				return
			else:
				avgHostScore = dbResult['Data']

 			#Host tenant score
			dbResult = self.ui_util._InterfaceUtil__getAllTenantScore()

			if dbResult['Status'] != self.globals.Success:
				# build error response and return
				return
			else:
				hostTenantScore = dbResult['Data']

			# Rearrange the data
			myLandingPageData['AvgScore'] = avgScore
			myLandingPageData['Location'] = avgLocScore
			myLandingPageData['Vendor'] = avgVendorScore
			#print('Location >>>', avgLocScore)
			#print('Vendor >>>', avgVendorScore)
			myLandingPageData['Vendor'] = avgVendorScore
			myLandingPageData['LocVendor'] = avgLocVendorScore 
			myLandingPageData['LocHost'] = avgHostScore
			myLandingPageData['HostTenant'] = hostTenantScore

			#print('LocVendor >>>',avgLocVendorScore)
			#print('Host >>>',avgHostScore)
			return myLandingPageData
		except Exception as error:
			raise error

	def getOverallAvgScore(self, args):
		try:
			#validating security credential
			myScore = self.ui_util._InterfaceUtil__getAvgScore(args)
			return myScore

		except Exception as error:
			raise error

	def getLocAvgScore(self, args):
		try:
			#validating security credential
			dbResult = self.ui_util._InterfaceUtil__getAvgLocScore(args)
			return dbResult

		except Exception as error:
			raise error

	def getVendorAvgScore(self, args):
		try:
			#validating security credential
			#Avg Vendor score
			dbResult = self.ui_util._InterfaceUtil__getAvgVendorScore(args)
			return dbResult

		except Exception as error:
			raise error

	def getLocVendorAvgScore(self, args):
		try:
			#validating security credential
			#Avg Loc Vendor score
			dbResult = self.ui_util._InterfaceUtil__getAvgLocVendorScore(args)
			return dbResult

		except Exception as error:
			raise error

	def getHostInfo(self, args):
		try:
			#validating security credential
			#Avg Host score
			dbResult = self.ui_util._InterfaceUtil__getAvgHostInfo(args)
			return dbResult

		except Exception as error:
			raise error

	def getHostAvgScore(self, args):
		try:
			#validating security credential
			#Avg Host score
			dbResult = self.ui_util._InterfaceUtil__getAvgHostScore(args)
			return dbResult

		except Exception as error:
			raise error

	def getHostInfo(self, args):
		try:
			#validating security credential
			#get host information
			dbResult = self.ui_util._InterfaceUtil__getHostInfo(args)
			return dbResult

		except Exception as error:
			raise error

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

if __name__ == "__main__":
	ui = Interface()
	data = ui.getLandingPageData()
	#print(data)
