import os
from flask import Flask, flash, session, redirect, url_for, escape, request, jsonify, json
from datetime import timedelta
#from com.port8.core.singleton import Singleton
from com.port8.bpm.factory import Factory
from com.port8.core.utility import Utility
from com.port8.core.infrastructure import RestInfra
from flask_cors import CORS

import logging

#print("Hello")
util = Utility()
factory = Factory()
infra = RestInfra()

#print(os.environ['APP_SETTINGS'])
app = Flask(__name__)
app.env = 'DEVELOPMENT'
app.config.from_object(os.environ['APP_SETTINGS'])

#print('1st',app.config)
CORS(app)

#session = {}

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    
@app.route('/port8', methods=['GET','POST'])
def port8():
  return jsonify("Port8 !!!")

@app.route('/login', methods=['GET','POST'])
def login():

  if request.method == 'POST':
    session['username'] = request.form['username']
    return redirect(url_for('getAMember', memberId = 'MEM192551'))

  return '''
    <form method="post">
      <p><input type=text name=username>
      <p><input type=submit value=Login>
    </form>

  '''

@app.route('/logout')
def logout():
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
    responseData = factory.processRequest(myRequest)
    return jsonify(responseData)

if __name__ == "__main__":
    print ("Initializing ...")
    myFlaskHost = infra.restApiConfigData['FlaskHost']
    myFlaskPort = int(infra.restApiConfigData['FlaskPort'])

    print ("found, flask host:port", myFlaskHost, ":", myFlaskPort)

    #app.env="DEVELOPMENT"
    app.config.from_object(util.getEnv('APP_SETTINGS'))
    #print(app.env)
    app.run(debug=True, host=myFlaskHost, port=myFlaskPort, threaded=True)
    #app.run()