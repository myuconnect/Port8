from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utility import Utility
from com.port8.core.mysqlutils import MysqlUtil
from com.port8.core.infrastructure import RestInfra
from jsonschema import validate
from com.port8.core.error import *

class InterfaceUtil(object, metaclass=Singleton):
	def __init__(self):
		self.utility = Utility()
		self.globals = Global()
		self.infra = RestInfra()
		self.logger = self.infra.Logger
			
		self.repDB = MysqlUtil(self.logger)
		self.repConn = self.repDB.getRepDBConnection()

	def getAvgScore(self):
		'''
		Description: Returns overall average CIS scan score
		Return: <average_score>
		'''
		try:
			# Average score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.avgScoreSql, SqlArgs=None, SqlOutput = self.globals.SqlOutput['Dict'])

			myData = float()

			if dbResult['Status'] == self.globals.Success:
				myData = round(dbResult['Data'][0]['AVG_SCORE'],2)
				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def getAvgLocScore(self):
		'''
		Description: Returns average CIS scan score for each location
		Return: [{"<LOCATION>" : <average_score>}]
		'''
		try:
			# Average location score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.locAvgScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])
			myData = []

			if dbResult['Status'] == self.globals.Success:
				for loc in dbResult['Data']:
					myData.append({ loc['LOCATION'] : round(loc['AVG_SCORE'],2) })
				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def getAvgHostScore(self):
		'''
		Description: Returns average CIS scan score for all host
		Return: [{"<HOST>" : <average_score>, "LOCATION" : <location>}]
		'''
		try:
			# Average location score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.hostScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			myData = list()

			if dbResult['Status'] == self.globals.Success:
				for host in dbResult['Data']:
					myData.append({host['HOST'] : round(host['AVG_SCORE'],2), "Location" : host['LOCATION'], "LastScan" : host["LAST_SCAN"], "LastScanTime" : host["LAST_SCAN_TIME"]})

				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def getAvgVendorScore(self):
		'''
		Description: Returns average CIS scan score for all Venodr and its product
		Return: [{"<vendor>" : {<product> : <score>} }]
		'''
		try:
			# Average location score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.vendorProdAvgScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			myData = list()

			if dbResult['Status'] == self.globals.Success:
				for vendorProdList in dbResult['Data']:
					#checking if vendor exists
					vendor = [indx for indx, val in enumerate(myData) if vendorProdList['VENDOR'] in val.keys()]
					if not vendor:
						# vendor doesnt exist, adding new vendor and product
						myData.append({vendorProdList['VENDOR'] : [{vendorProdList['PRODUCT'] : round(vendorProdList['AVG_SCORE'],2)}]})
					else:
						# vendor exist, adding product
						myData[vendor[0]][vendorProdList['VENDOR']].append({vendorProdList['PRODUCT'] : round(vendorProdList['AVG_SCORE'],2) })

				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def getAvgLocVendorScore(self):
		'''
		Description: Returns average CIS scan score for all Venodr and its product
		Return: [{"<location>" : {<vendor> : {<product> : <score> }}}]
		'''
		try:
			# Average location score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.locVendorAvgScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			myData = list()

			if dbResult['Status'] == self.globals.Success:
				for locVendor in dbResult['Data']:
					#checking if Location exisit
					location = [indx for indx, val in enumerate(myData) if locVendor['LOCATION'] in val.keys() ]

					if not location:
						# Location does not exist, will add new record
						#print('location not found', locVendor)
						myData.append(
							{ 
								locVendor['LOCATION'] : 
									[ {locVendor['VENDOR'] : [ {locVendor['PRODUCT'] : round(locVendor['AVG_SCORE'],2)} ] } ]
							}
						)
						#print('location not found', myData)
					else:
						location = location[0]
						#print('location found',locVendor['LOCATION'])
						# we found location, will check if vendor exists
						#print('location:',locVendor['LOCATION'])
						#print('mydata:',myData)
						#print('location indx:',location)
						#print('mydata loc:',myData[location][locVendor['LOCATION']])
						#print('before finding vendor',myData[location][locVendor['LOCATION']])
						vendor = [indx for indx, val in enumerate(myData[location][locVendor['LOCATION']]) if locVendor['VENDOR'] in val.keys() ]

						if not vendor:
							#vendor not found for this location, will add new vendor
							#print('vendor not found',myData[location][locVendor['LOCATION']])
							myData[location][locVendor['LOCATION']].append(
								{ locVendor['VENDOR'] : [ {locVendor['PRODUCT'] : round(locVendor['AVG_SCORE']) }] }
							)
						else:
							vendor = vendor[0]
							#print('vendor found',location,locVendor['LOCATION'],vendor,myData)
							# vendor for this location found, add product to this vendor
							myData[location][locVendor['LOCATION']][vendor][locVendor['VENDOR']].append({locVendor['PRODUCT'] : round(locVendor['AVG_SCORE'])})
				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def getTenantScan(self, TenantId, ScanId = 'Latest'):
		'''
		Description: Get latest tenant scan for a tenant id
		Args: 
			TenantId : TenantId
			ScanId : optional (default is 'Latest')
		'''
		try:
			if scanId == self.globals.latest:
				latestScan = self.getLatestTenantScan(TenantId)
				if dbResult['Status'] == self.globals.Success:
					if dbResult['Data']:
						myScanId = dbResult['Data']['SCAN_ID']
						myScanSeqId = dbResult['Data']['SEQ_ID']
				else:
					raise ValueError('')
				myScanId = dbResult['Data']['ScanId']
			else:
				myScanId = scanId

				dbResult = self.repDB.execSelectSql(self.repConn, self.globals.getTenantScanSummarySql) 			
		except Exception as e:
			raise e

	def getLastTenantScan(self, TenantId):
		'''
		Description: Get latest scan id for a tenant
		Args: 
			TenantId : TenantId
			ScanId : optional (default is 'Latest')
		Returns: last scan id and scan seq id
		'''
		try:
			mySqlArgs = {'TenantId' : TenantId}
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.getLatestTenantScansSql, SqlArgs = TenantId, SqlOutput = self.globals.SqlOutput['Dict'])
			if dbResult['Status'] == self.globals.Success:
				# if we got data, we need to extract dict from tuple
				if dbResult['Data']:
					dbResult['Data'] = dbResult['Data'][0]

			return dbResult

		except Exception as e:
			raise e


	'''
	def buildSummScanResponse(self, AvgScore, LocScore, HostScore, TenantScore, LocTenantScore):
        try:

            myData = self.getACopy(self.globals.Template['ScanSummaryData'])

            myData['AvgScore'] = round(AvgScore['AVG_SCORE'],2)

            for loc in LocScore:
                myData['LocAvgScore'].append({loc['LOCATION'] : round(loc['AVG_SCORE'],2)})

            for host in HostScore:
                myData['HostScore'].append({host['HOST'] : round(host['AVG_SCORE'],2)})

            for tenant in TenantScore:
                #checking if vendor exists
                vendor = [key for key, val in myData['TenantScore'].items() if key == tenant['VENDOR'] ]
                if not vendor:
                    # vendor doesnt exist, adding new vendor and product
                    myData['TenantScore'].update({tenant['VENDOR'] : [{tenant['PRODUCT'] : round(tenant['AVG_SCORE'],2)}]})
                else:
                    # vendor exist, adding product
                    myData['TenantScore'][vendor[0]].append({tenant['PRODUCT'] : round(tenant['AVG_SCORE'],2) })

            for locTenant in LocTenantScore:
                #checking if Location exisit
                location = [key for key, val in myData['LocTenAvgScore'].items() if key == locTenant['LOCATION'] ]
                if not location:
                    # Location does not exist, will add new record
                    myData['LocTenAvgScore'].update({
                        locTenant['LOCATION'] : 
                            [ {locTenant['VENDOR'] : [ {locTenant['PRODUCT'] : round(locTenant['AVG_SCORE'],2)} ] } ]
                        }
                    )
                else:
                    # we found location, will check if vendor exists
                    #[key for key, val in myData['LocTenAvgScore'][locTenant['LOCATION']].items() if key == locTenant['LOCATION']['VENDOR'] ]
                    vendorIndex = [indx for indx, value in enumerate(myData['LocTenAvgScore'][locTenant['LOCATION']]) if value == locTenant['VENDOR'] ]
                    if not vendorIndex:
                        #vendor not found for this locaation, will add new vendor
                        myData['LocTenAvgScore'][locTenant['LOCATION']].append({
                            locTenant['VENDOR'] : [{locTenant['PRODUCT'] : round(locTenant['AVG_SCORE'])} ] 
                        })
                    else:
                        # vendor for this location found, add product to this vendor
                        myData['LocTenAvgScore'][locTenant['LOCATION']][vendorIndex].append({
                            locTenant['PRODUCT'] : rund(locTenant['AVG_SCORE'])
                        })

            myResponse = self.getACopy(self.globals.Template['Response'])
            myResponse['Status'] = self.globals.Success
            myResponse['Message'] = self.globals.Success
            myResponse['Data'] = myData

            return myResponse

        except Exception as err:
            raise err
	'''
if __name__ == "__main__":
	util = InterfaceUtil()
	avg = util.getAvgScore()
	print(avg)
	hostScore = util.getAvgHostScore()
	print(hostScore)
	locScore = util.getAvgLocScore()
	print(locScore)
	vendorScore = util.getAvgVendorScore()
	print(vendorScore)
	locVendScore = util.getAvgLocVendorScore()
	print(locVendScore)