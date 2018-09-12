import os, platform

class Setup(object):
	def __init__(self):
		self.os = platform.system().upper()
		self.initFile = "init.json"
		self.bootstrapFile = "boostrap.json" 
		self.appName = "port8"

	def acceptValue(heading):
		value = input(heading)

	def isDirExist(dirNameup):
		return os.path.isdir(dirName)

if __name__ == '__main__':
	setup = Setup()
	# validate home dir
	try:
		while True:
			homeDir = setup.acceptValue("Pls enter PORT8 home directory (must be empty) :")
			if os.path.isdir(homeDir) and os.listdir(homeDir):
				print("Sorry, directory [{dir}] is not empty !!!".format(dir = homeDir))
				continue

			if not os.path.isdir(dirName)
				os.mkdir(homeDir)
	except Exception as err:
		print("error [{error}] occurred during setup, Pls contact Port8 Support !!!")
		raise
	#dir structure /<home dir>/app/port8/com/bin
	print("creating directories     :")
	os.mkdir(homeDir)