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
			
		self.mySqlUtil = MysqlUtil(self.logger)
		self.repConn = self.mySqlUtil.getRepDBConnection()

	def __getAvgScore(self, args):
		'''
		Description: Returns overall average CIS scan score
		Return: <average_score>
		'''
		try:
			# initializing
			myMandatoryArgs = ["SecurityToken"]

			# Validaring arguments
			myValResult = self.utility.valRequiredArg(args, myMandatoryArgs)

			if myValResult[0] == self.globals.UnSuccess:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, myValResult[2])
				return myResponse

			# Average score
			dbResult = self.mySqlUtil.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.avgScoreSql, SqlArgs=None, SqlOutput = self.globals.SqlOutput['Dict'])

			myScore = float()

			if dbResult['Status'] == self.globals.Success:
				myScore = round(dbResult['Data'][0]['AVG_SCORE'],2)
				myData = [{'AvgScore': myScore}]
				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def __getAvgLocScore(self, args):
		'''
		Description: Returns average CIS scan score for each location
		Return: [{"<LOCATION>" : <average_score>}]
		'''
		try:
			# initializing
			myMandatoryArgs = ["SecurityToken"]
			myOptionalArgs = ["Location"]

			# Validaring arguments
			myValResult = self.utility.valRequiredArg(args, myMandatoryArgs)

			if myValResult[0] == self.globals.UnSuccess:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, myValResult[2])
				return myResponse
				#raise InvalidArguments(myValResult[2])

			if not ('Location' in args):
				dbResult = self.mySqlUtil.execSelectSql(\
					Conn = self.repConn, SqlText = self.globals.getAllLocAvgScoreSql, SqlArgs = args, SqlOutput = self.globals.SqlOutput['Dict'])
			else:
				# will pass args
				dbResult = self.mySqlUtil.execSelectSql(\
					Conn = self.repConn, SqlText = self.globals.getALocAvgScoreSql, SqlArgs = args, SqlOutput = self.globals.SqlOutput['Dict'])
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

	def __getHostInfo(self, args):
		'''
		Description: Returns average CIS scan score for all host
		Arguments: Optional; HostName, HostId,OS, PhysicalMem, Location
			# OS = [], 0 --> OS name, 1--> os ver
			# PhysMemory [] --> 0 --> Operator, 1--> Value
			# Location

		Return: [{"<HOST>" : <average_score>, "LOCATION" : <location>}]
		'''
		try:
			# initializing
			myMandatoryArgs = ["SecurityToken"]
			myOptionalArgs = ["Location","VendorId","HostId","HostName","OS","PhysMemory"]
			myCriteria = myDynaSql = myDynaSqlWhereClause = myDynaSqlGroupByClause = myDynaSqlOrderByClause = ""

			# Validaring arguments
			myArguments = self.utility.removeEmptyKeyFromDict(args)
			myValResult = self.utility.valRequiredArg(myArguments, myMandatoryArgs)
			print('arg recvd', myArguments)

			if myValResult[0] == self.globals.UnSuccess:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, myValResult[2])
				return myResponse

			mySelectColList = self.globals.getHostDetailsCol
			mySelectTabList = self.globals.getHostDetailsFromClause

			if self.utility.isKeyInDict(myArguments, 'HostId') or self.utility.isKeyInDict(myArguments, 'HostName'): 
			#if 'HostName' or 'HostId' in myArguments:
				if 'HostName' in myArguments:
					myCriteria = ''.join([' host_name = %(HostName)s'])

				elif 'HostId' in myArguments:
					myCriteria = ''.join([' host_id = %(HostId)s'])
			else:
				print('Host arg is not found, looking for other arguments ..., table list >>>', mySelectTabList)
				# building dynamic sql (adding table and column to main sql as argument passed)
				if 'VendorId' in myArguments:
					if not self.utility.getValCntInList(mySelectTabList, 'p$ht_tenant tenant'):
						mySelectTabList.append('p$ht_tenant tenant')
						mySelectColList = ''.join([mySelectColList,', tenant.tenant_version TENANT_VERSION, \
							tenant.tenant_name TENANT_NAME, tenant.tenant_vendor TENANT_VENDOR, tenant.vendor_prod_name VENDOR_PRODUCT'])

					myCriteria = ''.join([' tenant.tenant_vendor = %(VendorId)s'])

				# Vendor product criteria
				if 'Product' in myArguments:
					if not self.utility.getValCntInList(mySelectTabList, 'p$ht_tenant tenant'):
						mySelectTabList.append('p$ht_tenant tenant')
						mySelectColList = ''.join([mySelectColList,', tenant.tenant_version TENANT_VERSION, \
							tenant.tenant_name TENANT_NAME, tenant.tenant_vendor TENANT_VENDOR, tenant.vendor_prod_name VENDOR_PRODUCT'])

					if myCriteria:
						myCriteria = ''.join([myCriteria, ' and ', ' tenant.vendor_prod_name = %(Product)s'])
					else:
						myCriteria = ''.join([myCriteria, ' tenant.vendor_prod_name = %(Product)s'])

				# Location/DC_INFO criteria
				if 'Location' in myArguments:
					if myCriteria:
						myCriteria = ''.join([myCriteria,' and ', 'dc_info = %(Location)s'])
					else:
						myCriteria = ''.join(['dc_info = %(Location)s'])
					#myArguments.update({'Location' : myArguments['Location']})

				#OS criteria
				if 'OS' in myArguments:
					myOS = myOSVer = None

					if (isinstance(myArguments['OS'], list) or isinstance(myArguments['OS'], tuple)) and len(myArguments['OS'] == 2):
						myOS = myArguments['OS'][0]
						myOSVer = myArguments['OS'][1]
						myArguments.update({'OS' : myOS, 'OSVersion' : myOSVer})
					elif (isinstance(myArguments['OS'], list) or isinstance(myArguments['OS'], tuple)) and len(myArguments['OS'] == 1):
						myOS = myArguments['OS'][0]
						myArguments.update({'OS' : myOS})
					else:
						myOS  = myArguments['OS']
						myArguments.update({'OS' : myOS})

					if myCriteria: 
						if myOS:
							myCriteria = ''.join([myCriteria,' and ', 'OS = %(OS)s'])

						if myOSVer:
							myCriteria = ''.join([myCriteria,' and ', 'OSVersion = %(OSVersion)s'])
					else:
						if myOS:
							myCriteria = ''.join(['OS = %(OS)s'])

						if myOSVer:
							myCriteria = ''.join([myCriteria, ' and ', 'OSVersion = %(OSVersion)s'])

				if 'PhysicalMem' in myArguments:
					myPhysMem = myPhysMemOper = None

					if len(myArguments['PhysicalMem'] == 2):
						myPhysMem = myArguments['PhysicalMem'][0]
						myPhysMemOper = myArguments['OS'][1]
					elif len(myArguments['OS'] == 1):
						myPhysMem = myArguments['OS'][0]
						myPhysMemOper = ' = '
					else:
						myPhysMem  = myArguments['OS']
						myPhysMemOper = ' = '

					myArguments.update({'PhyscialMem' : myPhysMem})
					if myCriteria:
						myCriteria = ''.join([myCriteria,' and ', 'physical_memory_mb ' , myPhysMemOper, ' %(PhysicalMem)s'])
					else:					
						myCriteria = ''.join(['physical_memory_mb ' , myPhysMemOper, ' %(PhysicalMem)s'])

			print('Criteria >>>', myCriteria)
			myDynaSql = self.mySqlUtil.buildDynaSql(mySelectColList, mySelectTabList, myCriteria)

			print('dynamic sql',myDynaSql, myArguments)
			dbResult = self.mySqlUtil.execSelectSql(\
				Conn = self.repConn, SqlText = myDynaSql, SqlArgs = myArguments, SqlOutput = self.globals.SqlOutput['Dict'])

			myHostData = []

			if dbResult['Status'] == self.globals.Success:
				for host in dbResult['Data']:
					myData = {
						'HostId' : host['HOST_ID'],'Host': host['HOST'],
						"Location" : host['LOCATION'], "PhysicalLoc" : host['PHYSICAL_LOC'],
						"OS" : host['OS'], "OSVersion" : host['OSVersion'], "OSRelease" : host['OS_RELEASE'],
						"PhysicalMemMB" : host['PHYSICAL_MEMORY_MB'], "SwapMemMB" : host['SWAP_MEMORY_MB'],
						"IPAddress" : host['IP_ADDRESSES'],
						'AvgScore' : round(host['AVG_SCORE'],2), "LastScan" : host["LAST_SCAN"], "LastScanTime" : host["LAST_SCAN_TIME"]}
					
					if 'TENANT_VENDOR' in host:	
						myData.update({'TenantVendor' : host['TENANT_VENDOR']})
					if 'VENDOR_PRODUCT' in host:	
						myData.update({'VendorProduct' : host['VENDOR_PRODUCT']})
					if 'TENANT_NAME' in host:
						myData.update({'TenantName' : host['TENANT_NAME']})
					if 'TENANT_VERSION' in host:
						myData.update({'TenantVersion' : host['TENANT_VERSION']})

					myHostData.append(myData)
				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myHostData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise
		finally:
			del myMandatoryArgs
			del myOptionalArgs
			del myCriteria
			del myDynaSql
			del myDynaSqlWhereClause
			del myDynaSqlGroupByClause 
			del myDynaSqlOrderByClause
			del myArguments
			del myValResult
			del myResponse
			del mySelectColList
			del mySelectTabList


	def __getAvgHostScore(self, args):
		'''
		Description: Returns average CIS scan score for all host
		Arguments: Optional; HostId, Location, VendorId
		Return: [{"<HOST>" : <average_score>, "LOCATION" : <location>}]
		'''
		try:
			# initializing
			myMandatoryArgs = ["SecurityToken"]
			myOptionalArgs = ["Location","VendorId","HostId"]

			# Validaring arguments
			myArguments = self.utility.removeEmptyKeyFromDict(args)
			myValResult = self.utility.valRequiredArg(myArguments, myMandatoryArgs)

			if myValResult[0] == self.globals.UnSuccess:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, myValResult[2])
				return myResponse

			Location = Vendor = host = ''

			if 'HostId' in myArguments:
				# get host avg scroe for a host
				print('Host id passed, ignoring rest of criteria')
				mySql = self.globals.getAHostScoreSql
				#myArgs = self.utility.getACopy(myArguments)

			elif 'Location' in myArguments and 'VendorId' in myArguments:
				print('Loc/Venodr id passed, ignoring rest of criteria')
				mySql = self.globals.getLocVendorHostScoreSql
				#myArgs = self.utility.getACopy(myArguments)

			elif 'Location' in myArguments:
				print('Loc id passed, ignoring rest of criteria')
				mySql = self.globals.getLocHostScoreSql
				#myArgs = self.utility.getACopy(myArguments)

			elif 'VendorId' in myArguments:
				print('Vendor id passed, ignoring rest of criteria')
				mySql = self.globals.getVendorHostScoreSql
				#myArgs = self.utility.getACopy(myArguments)

			else:
				# no argument passed, returning all hosts
				print('No arguments passed, getting all host')
				mySql = self.globals.getAllHostScoreSql
				myArguments = None

			print('Sql, args >>> ',mySql, myArguments)
			dbResult = self.mySqlUtil.execSelectSql(\
				Conn = self.repConn, SqlText = mySql, SqlArgs = myArguments, SqlOutput = self.globals.SqlOutput['Dict'])

			myHostData = []

			if dbResult['Status'] == self.globals.Success:
				for host in dbResult['Data']:
					myData = {'HostId' : host['HOST_ID'],'Host': host['HOST'], 'AvgScore' : round(host['AVG_SCORE'],2), "Location" : host['LOCATION'], "LastScan" : host["LAST_SCAN"], "LastScanTime" : host["LAST_SCAN_TIME"]}
					if 'VENDOR' in host:
						myData.update({"Vendor" : host['VENDOR']})
					if 'VENDOR_PRODUCT' in host:
						myData.update({"VendorProduct" : host['VENDOR_PRODUCT']})
					myHostData.append(myData)
				myResponse = self.utility.buildResponse(self.globals.Success, self.globals.Success, myHostData)
			else:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, dbResult['Data'])

			return myResponse

		except Exception as error:
			raise

	def __getAllTenantScore(self):
		try:
			# Average location score
			dbResult = self.mySqlUtil.execSelectSql(\
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

	def __getAvgVendorScore(self, args):
		'''
		Description: Returns average CIS scan score for all Venodr and its product
		Return: [{"<vendor>" : {<product> : <score>} }]
		'''
		try:
			# initializing
			myMandatoryArgs = ["SecurityToken"]
			myOptionalArgs = ["VendorId"]

			# Validaring arguments
			myArguments = self.utility.removeEmptyKeyFromDict(args)
			myValResult = self.utility.valRequiredArg(myArguments, myMandatoryArgs)

			if myValResult[0] == self.globals.UnSuccess:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, myValResult[2])
				return myResponse

			if 'VendorId' in myArguments:
				#found vendor, will return score for this vendor
				mySql = self.globals.getAVendorProdAvgScoreSql
				#myArgs = self.utility.getACopy(args)

			else:
				# will return score for all vendor
				mySql = self.globals.getAllVendorProdAvgScoreSql
				myArguments = None

			dbResult = self.mySqlUtil.execSelectSql(\
				Conn = self.repConn, SqlText = mySql, SqlArgs = myArguments, SqlOutput = self.globals.SqlOutput['Dict'])

			myData = []

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

	def __getAvgLocVendorScore(self, args):
		'''
		Description: Returns average CIS scan score for all Venodr and its product
		Return: [{"<location>" : {<vendor> : {<product> : <score> }}}]
		'''
		try:
			# Average location score
			# initializing
			myMandatoryArgs = ["SecurityToken"]
			myOptionalArgs = ["Location","VendorId"]

			# Validaring arguments
			myArguments = self.utility.removeEmptyKeyFromDict(args)
			myValResult = self.utility.valRequiredArg(args, myMandatoryArgs)

			if myValResult[0] == self.globals.UnSuccess:
				myResponse = self.utility.buildResponse(self.globals.UnSuccess, myValResult[2])
				return myResponse

			if 'Location' in myArguments and 'VendorId' in myArguments:
				mySql = self.globals.getALocAVendorAvgScoreSql
				#myArgs = self.utility.getACopy(myArguments)

			elif 'Location' in myArguments:
				mySql = self.globals.getALocAllVendorAvgScoreSql
				#myArgs = self.utility.getACopy(myArguments)

			elif 'VendorId' in myArguments:
				mySql = self.globals.getAllLocAVendorAvgScoreSql
				#myArgs = self.utility.getACopy(myArguments)
			else:
				mySql = self.globals.getAllLocVendorAvgScoreSql
				myArguments = None

			dbResult = self.mySqlUtil.execSelectSql(\
				Conn = self.repConn, SqlText = mySql, SqlArgs = myArguments, SqlOutput = self.globals.SqlOutput['Dict'])

			myData = []

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

				dbResult = self.mySqlUtil.execSelectSql(self.repConn, self.globals.getTenantScanSummarySql) 			
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
			dbResult = self.mySqlUtil.execSelectSql(\
				Conn = self.repConn, SqlText = self.globals.getLatestTenantScansSql, SqlArgs = TenantId, SqlOutput = self.globals.SqlOutput['Dict'])
			if dbResult['Status'] == self.globals.Success:
				# if we got data, we need to extract dict from tuple
				if dbResult['Data']:
					dbResult['Data'] = dbResult['Data'][0]

			return dbResult

		except Exception as e:
			raise e

	###
	### Host/Tenant Details
	#def __getHostDetails(self, args):


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