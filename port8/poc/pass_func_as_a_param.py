# we should try this in factory model
def myMethod1(arg1):
	print('in myMethod',arg1, type(arg1))
	return arg1 # returing argument passed

def myMethod2(fun,arg1):
	# myMethod has already been executed, arg Fun would have return value from myMethod
	#print ("executing fun")
	print("fun",fun)
	#fun.__call__()
	print(arg1)
	return

myMethod2(myMethod1('test'),'test1')