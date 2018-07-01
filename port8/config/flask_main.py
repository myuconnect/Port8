from flask import Flask, flash, session, redirect, url_for, escape, request, jsonify, json
from datetime import timedelta
from com.port8.core.singleton import Singleton
from com.port8.bpm.factory import Factory
from com.port8.core.utility import Utility
from com.port8.core.infrastructure import RestInfra
from flask_cors import CORS

import logging

#'\x95\x8d\xe3\xab\x18\xc2\xc6\xeb\xd4+\x11H<\xdc\xd8m\xaf\xae0\xcfb\xdc\x84\x92\xc5\xb2\xado\x98\xc5\x08\xa9\xbb/\x95\xe9/\xda\x10\xaa\x1f\xb7k\x956SLCIj\r7v\xdbm\\\x1e\xdc\xf3M&$\xb0\xce\xdb\x18\xd6\xa3\x13\x85\xd0m\r\x1a]\xbe\xf8\xd8Q\xcf\xed\xaf\x0b\x827TB\xb7'
myLogger = logging.getLogger('uConnect')
util = Utility()
factory = Factory()
rest = RestInfra()

app = Flask(__name__)
CORS(app)
app.secret_key = '\x95\x8d\xe3\xab\x18\xc2\xc6\xeb\xd4+\x11H<\xdc\xd8m\xaf\xae0\xcfb\xdc\x84\x92\xc5\xb2\xado\x98\xc5\x08\xa9\xbb/\x95\xe9/\xda\x10\xaa\x1f\xb7k\x956SLCIj\r7v\xdbm\\\x1e\xdc\xf3M&$\xb0\xce\xdb\x18\xd6\xa3\x13\x85\xd0m\r\x1a]\xbe\xf8\xd8Q\xcf\xed\xaf\x0b\x827TB\xb7'
#session = {}

@app.before_request
def make_session_permanent():
    myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
    myModuleLogger.debug("initializing session information ...")
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    
@app.route('/port8', methods=['GET','POST'])
def port8():
  myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
  myModuleLogger.debug("port8 main page")

  return jsonify("Port8 !!!")

@app.route('/login', methods=['GET','POST'])
def login():
  myModuleLogger = logging.getLogger('port8.' +str(__name__) )
  myModuleLogger.debug("initiating login page")

  if request.method == 'POST':
    myModuleLogger.debug("got a POST request, initiating login page")
    session['username'] = request.form['username']
    myModuleLogger.debug("user [{user}]".format(user=session['username']))    
    #flash('You were successfully logged in')
    return redirect(url_for('getAMember', memberId = 'MEM192551'))
    #return redirect(url_for('uConnect'))

  return '''
    <form method="post">
      <p><input type=text name=username>
      <p><input type=submit value=Login>
    </form>

  '''
@app.route('/insert')
def insert():
  Member = MongoDB()
  MemberData = Member.InsertOneDoc('Member',{ 'Main':{'FirstName':'Aditya','LastName':'Singh'},'Address':{'Street':'44 Helena Street','City':'East Brunswick','State':'NJ','ZipCode':'08816'}})
  return jsonify(MemberData)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    flash('You were successfully logged out')
    session.pop('username', None)

    return redirect(url_for('login'))

@app.route('/requestPost', methods=['POST'])
def requestPost():
    print("raw request", request)
    myRequest = request.get_json()
    print(myRequest)
    if not(util.isValidRestRequest(myRequest)):
      return jsonify({"Status":"Error","Message":"Invalid request argument {arg} passed !!!".format(arg=myRequest)})

    app.logger.debug('got request {request}'.format(request=myRequest))
    factory = Factory()
    MemberData = factory.processRequest(myRequest)
    return jsonify(MemberData)

if __name__ == "__main__":
    print ("Initializing flask environment ...")

    infra = RestInfra()
    myFlaskHost = infra.restApiConfigData['FlaskHost']
    myFlaskPort = int(infra.restApiConfigData['FlaskPort'])

    print ("found, flask host:port", myFlaskHost, ":", myFlaskPort)

    app.run(debug=True, host=myFlaskHost, port=myFlaskPort, threaded=True)
  