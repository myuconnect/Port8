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

	def __getAvgScore(self):
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

	def __getAvgLocScore(self):
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
					myData.append({ 'Location' : loc['LOCATION'], 'AvgScore' : round(loc['AVG_SCORE'],2) })
				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def __getAvgHostScore(self, args = None):
		'''
		Description: Returns average CIS scan score for all host
		Return: [{"<HOST>" : <average_score>, "LOCATION" : <location>}]
		'''
		try:
			# average host score
			# initialization
			Location = Vendor = host = ''
			if args:
				if 'Location' in args:
					Location = args['Location']
				if 'Vendor' in args:
					Vendor = args['Vendor']
				if 'HostId' in args:
					HostId = args['HostId']

			# if no argument passed, returning all hosts
			if not args or (not Location and not Vendor and not HostId):
				dbResult = self.repDB.execSelectSql(\
					Conn = self.repConn, SqlText = self.globals.getAllHostScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			# get host avg scroe for a host
			if args and HostId:
				dbResult = self.repDB.execSelectSql(\
					Conn = self.repConn, SqlText = self.globals.getAHostScoreSql, SqlArgs = HostId, SqlOutput = self.globals.SqlOutput['Dict'])


			myData = list()

			if dbResult['Status'] == self.globals.Success:
				for host in dbResult['Data']:
					myData.append({'Host': host['HOST'], 'AvgScore' : round(host['AVG_SCORE'],2), "Location" : host['LOCATION'], "LastScan" : host["LAST_SCAN"], "LastScanTime" : host["LAST_SCAN_TIME"]})

				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def __getAllTenantScore(self):
		try:
			# Average location score
			dbResult = self.repDB.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.hostTenantScoreSql, SqlArgs = None, SqlOutput = self.globals.SqlOutput['Dict'])

			myData = list()
			#print(dbResult['Data'])
			if dbResult['Status'] == self.globals.Success:
				for tenant in dbResult['Data']:
					#checking if this is new venodr
					host = [indx for indx, val in enumerate(myData) if tenant['HOST'] in val.keys()]
					if not host:
						# vendor doesnt exist, adding new vendor and product
						myData.append({tenant['HOST'] : [{tenant['TENANT_NAME'] : round(tenant['LAST_SCORE'],2), "TYPE" : tenant["TYPE"], "VENDOR" : tenant["VENDOR"], "PRODUCT" : tenant["PRODUCT"], "VERSION" : tenant["VERSION"]}]} )
					else:
						# vendor exist, adding product
						myData[host[0]][tenant['HOST']].append({tenant['TENANT_NAME'] : round(tenant['LAST_SCORE'],2), "TYPE" : tenant["TYPE"], "VENDOR" : tenant["VENDOR"], "PRODUCT" : tenant["PRODUCT"], "VERSION" : tenant["VERSION"] })
						#myData[host[0]][tenant['HOST']].append({tenant['HOST'] : [{tenant['TENANT_NAME'] : round(tenant['LAST_SCORE'],2)}, "TYPE" : tenant["TYPE"], "VENDOR" : tenant["VENDOR"], "PRODUCT" : tenant["PRODUCT"], "VERSION" : tenant["VERSION"]]} )

				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			#print(myResponse)
			return myResponse

		except Exception as error:
			raise

	def __getAvgVendorScore(self):
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
					#vendor = [indx for indx, val in enumerate(myData) if vendorProdList['VENDOR'] in val.keys()]
					vendorIndx = [indx for indx, val in enumerate(myData) if myData[indx]['Vendor'] == vendorProdList['VENDOR']]
					if not vendorIndx:
						# vendor doesnt exist, adding new vendor and product
						myData.append({
							'Vendor' : vendorProdList['VENDOR'], 
							'Products' : [{
								'Product' : vendorProdList['PRODUCT'], 
								'AvgScore' : round(vendorProdList['AVG_SCORE'],2)
							}]
						})
					else:
						# vendor exist, adding product
						#print('Vendor >>> ',myData)
						vendorIndx = vendorIndx[0]
						myData[vendorIndx]['Products'].append({'Product' : vendorProdList['PRODUCT'], 'AvgScore' : round(vendorProdList['AVG_SCORE'],2) })

				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise


	def __getAvgLocVendorScore(self):
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
					locIndx = [indx for indx, val in enumerate(myData) if locVendor['LOCATION'] == myData[indx]['Location'] ]

					if not locIndx:
						# Location does not exist, will add new record
						#print('location not found', locVendor)
						myData.append({ 
							'Location' : locVendor['LOCATION'],
							'Vendors' : [{
								'Vendor' : locVendor['VENDOR'],
								'Products' : [{
									'Product' : locVendor['PRODUCT'], 'AvgScore' : round(locVendor['AVG_SCORE'],2)
								}] 
							}]
						})
						#print('location not found', myData)
					else:
						locIndx = locIndx[0]
						#print('location found',locVendor['LOCATION'])
						# we found location, will check if vendor exists
						#print('location:',locVendor['LOCATION'])
						#print('mydata:',myData)
						#print('location indx:',location)
						#print('mydata loc:',myData[location][locVendor['LOCATION']])
						#print('before finding vendor',myData[location][locVendor['LOCATION']])
						vendorIndx = [indx for indx, val in enumerate(myData[locIndx]['Vendors']) if locVendor['VENDOR'] == myData[locIndx]['Vendors'][indx]['Vendor'] ]

						if not vendorIndx:
							#vendor not found for this location, will add new vendor along with its 1st product
							#print('vendor not found',myData[location][locVendor['LOCATION']])
							myData[locIndx]['Vendors'].append({
								'Vendor' : locVendor['VENDOR'], 
								'Products' : [{
									'Product' : locVendor['PRODUCT'], 
									'AvgScore' : round(locVendor['AVG_SCORE']) 
								}] 
							})
						else:
							# vendor found, will add the product to this vendor
							vendorIndx = vendorIndx[0]
							myData[locIndx]['Vendors'][vendorIndx]['Products'].append({
									'Product' : locVendor['PRODUCT'],
									'AvgScore' : round(locVendor['AVG_SCORE'])
								})
							'''
							#print('vendor found',location,locVendor['LOCATION'],vendor,myData)
							# vendor for this location found, add product to this vendor
							prodIndx = [indx for indx, val in enumerate(myData[locIndx]['Vendors'][vendorIndx]['Products']) if locVendor['PRODUCT'] == myData[locIndx]['Vendors'][vendorIndx][indx]['Product'] ]
							
							if not prodIndx:
								# product not found, will add product to current vendor
								myData[locIndx]['Vendors'][vendorIndx].update({'Products' : [{
										'Product' : locVendor['Product'],
										'AvgScore' : round(locVendor['AVG_SCORE'])
									}]
								})
							else:
								prodIndx = prodIndx[0]
								myData[locIndx]['Vendors'][vendorIndx]['Products'].append({
										'Product' : locVendor['Product'],
										'AvgScore' : round(locVendor['AVG_SCORE'])
									})

							myData[location][locVendor['LOCATION']][vendor][locVendor['VENDOR']].append({locVendor['PRODUCT'] : round(locVendor['AVG_SCORE'])})
							myData[locIndx]['Vendors'][vendorIndx][vendor][locVendor['VENDOR']].append({locVendor['PRODUCT'] : round(locVendor['AVG_SCORE'])})
							'''
				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def __getTenantScan(self, TenantId, ScanId = 'Latest'):
		'''
		Description: Get latest tenant scan for a tenant id
		Args: 
			TenantId : TenantId
			ScanId : optional (default is 'Latest')
		'''
		try:
			if scanId == self.globals.latest:
				latestScan = self.__getLastTenantScan(TenantId)
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

	def __getLastTenantScan(self, TenantId):
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



if __name__ == "__main__":
	util = InterfaceUtil()
	'''
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
	'''
	#tenant_score = util._InterfaceUtil__getAllTenantScore()
	#print(tenant_score)