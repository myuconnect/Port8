from com.port8.core.singleton import Singleton
from com.port8.core.globals import Global
from com.port8.core.utility import Utility
from com.port8.core.error import *

import uuid, hashlib

# we need to authenticate users and process credential. 
# User credential:
#	1. Authenticate against AD
#	2. Autthenticate with user id and password
# Process credential:
#	1.) Authneticate with key
#		Server will store master key, requestor must send an encrypted (SHA-256) key with request which need to be validated
#	2.) Authneticate with password, requestor must send an encrypted password
# Client must register its key/password before submitting a request to be executed

'''
#Password
import uuid
import hashlib
 
def hash_password(password):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
 
new_pass = input('Please enter a password: ')
hashed_password = hash_password(new_pass)
print('The string to store in the db is: ' + hashed_password)
old_pass = input('Now please enter the password again to check: ')
if check_password(hashed_password, old_pass):
    print('You entered the right password')
else:
    print('I am sorry but the password does not match')
'''
class Security(object, metaclass=Singleton):
	def __init__(self):
		self.util = Utility()

	def geneHashKey512(self, keyStr):
		'''
		Description: Generate SHA512 key
		'''
		salt = uuid.uuid4().hex
		return hashlib.sha512(salt.encode() + keyStr.encode()).hexdigest() + ':' + salt

	def isValidKey(self, keyStr, hashedKeyStr):
		'''
		Description: Validate if key str matches with SHA512 hash key
		'''
		password, salt = hashedKeyStr.split(':')
		return password == hashlib.sha512(salt.encode() + keyStr.encode()).hexdigest()

	def encrypt(self, secretKey, clearText):
		'''
		Description: Encrypt clear text with Secret key
		'''
		import base64
		encryptText = []
		for i in range(len(clearText)):
			key_c = secretKey[i % len(secretKey)]
			enc_c = chr((ord(clearText[i]) + ord(key_c)) % 256)
			encryptText.append(enc_c)
		return base64.urlsafe_b64encode("".join(encryptText).encode('utf-8')).decode('utf-8')

	def decrypt(self, secretKey, encryptText):
		'''
		Description: Descrypt encrypted text to clear text with Secret key
		'''
		import base64
		decryptText = []
		#enc = base64.urlsafe_b64decode(encryptText).decode('utf-8')
		enc = base64.urlsafe_b64decode(encryptText).decode()

		for i in range(len(enc)):
			key_c = secretKey[i % len(secretKey)]
			dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
			decryptText.append(dec_c)
		return "".join(decryptText)
