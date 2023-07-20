from flask import Flask, Response, render_template, jsonify, request, abort
from flask_basicauth import BasicAuth
import time
import subprocess

import json

def read_json(path):
    with open(path) as f:
        return json.load(f)

app = Flask(__name__)

@app.errorhandler(451)
def page_unavailable_for_legal_reasons(error):
    return render_template('451.html'), 451

secrets = read_json("secrets/secrets.json")
settings = read_json("application.json")

app.config['BASIC_AUTH_USERNAME'] = secrets['username']
app.config['BASIC_AUTH_PASSWORD'] = secrets['password']

basic_auth = BasicAuth(app)

program_status = "not running"
development_mode = True

def ip_is_valid():
    # get ip address
    ip = request.remote_addr
    if development_mode:
        return True
    # check if ip starts with 141.54
    if ip.startswith("141.54"):
        return True
    else:
        return False
  

'''
-----------------------------------------------------

Section for App-specific functions

-----------------------------------------------------
'''
import pdfsearch

@app.route('/')
def index():
    if not ip_is_valid():
        abort(451)
    try:
        q = request.args.get('q')
        print(q)
        if len(q) > 3:
            results = pdfsearch.search(q)
        else:
            results = []
        print(results)
    except Exception as e:
        print(e)
        results = []
    if results:
        return render_template('search.html', results=results, query=q)
    else:
        return render_template('landing_page.html', **read_json("application.json"))


@app.route('/search')
def search():
    if not ip_is_valid():
        abort(451)
    try:
        q = request.args.get('q')
        print(q)
        if len(q) > 3:
            results = pdfsearch.search(q)
        else:
            results = []
    except Exception as e:
        print(e)
        results = []
    return render_template('search.html', results=results, query=q)

'''
-----------------------------------------------------

Section for template functions

-----------------------------------------------------
'''


@app.route('/secret')
@basic_auth.required
def secret_page():
    return "You have access to the secret page!"

@app.route('/status')
def status():
    global program_status
    return jsonify(status=program_status)

@app.route('/logs')
@basic_auth.required
def logs():
    log_messages = []
    with open('app/log/application.log', 'r') as logfile:
        for line in logfile:
            try:
                time, application, log_type, message = line.strip().split(' ', 3)
                log_messages.append({'time': time, 'application': application, 'type': log_type, 'message': message})
            except Exception as e:
                print("Parse Error for log event:" + line)
    log_messages = log_messages[::-1]  # Reverse the order of the messages to display the latest message first
    return render_template('logs.html', log_messages=log_messages)


@app.route('/activate', methods=['POST'])
def activate():
    global program_status
    if program_status == "success":
        return jsonify(status='already running')
    program_running = True
    if start():
        program_status = "success"
    else:
        program_status = "failed"
    return jsonify(status=program_status)

def start():
    time.sleep(5)
    # code for your function goes here
    subprocess.Popen(["python", "app/main.py"]) 
    print("Calendar initialized")
    return True

if __name__ == '__main__':
    app.run()