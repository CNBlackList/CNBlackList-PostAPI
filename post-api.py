import dbmanager
import postmanager
import time
import os
import sys
import platform

import _thread
from flask import Flask
from flask import request

print('Starting POST API server...\n')

APIKEY = os.getenv('POSTAPI_APIKEY')
PORT = os.getenv('POSTAPI_PORT')
BIND = os.getenv('POSTAPI_BIND')
DEBUG = os.getenv('POSTAPI_DEBUG')
DBPATH = os.getenv('POSTAPI_DBPATH')
FORKPROCESS = os.getenv('POSTAPI_FORKPROCESS')

if APIKEY == None:
    raise ValueError('Invalid API Key')
if PORT == None:
    PORT = 8080
else:
    PORT = int(PORT)
if BIND == None:
    BIND = '0.0.0.0'
if DEBUG == None:
    DEBUG = False
else:
    if DEBUG == 'true':
        DEBUG = True
    elif DEBUG == 'false':
        DEBUG = False
    else:
        raise ValueError('debug')
if FORKPROCESS == None:
    FORKPROCESS = False
else:
    if FORKPROCESS == 'true':
        FORKPROCESS = True
    elif FORKPROCESS == 'false':
        FORKPROCESS = False
    else:
        raise ValueError('FORKPROCESS')

dbmgr = dbmanager.DBManager(DBPATH)
app = Flask(__name__)
@app.route('/postapi', methods = ['GET', 'POST'])
def postapi_receiver():
    method = request.values.get("method", "__invalid__")
    if method == '__invalid__':
        return '{"ok": false, "code": 1001, "message": "Invalid method."}'
    apikey = request.values.get("apikey", "__invalid__")
    if apikey != APIKEY:
        return '{"ok": false, "code": 1002, "message": "Invalid API Key."}'
    if method == 'new_ban':
        uid = request.values.get("uid", "__invalid__")
        ban = request.values.get("ban", "__invalid__")
        level = request.values.get("level", "__invalid__")
        expires = request.values.get("expires", "__invalid__")
        reason = request.values.get("reason", "__invalid__")
        try:
            uid = int(uid)
        except ValueError:
            return '{"ok": false, "code": 1003, "message": "Invalid value: User ID (uid)."}'
        try:
            level = int(level)
        except ValueError:
            return '{"ok": false, "code": 1003, "message": "Invalid value: level."}'
        if ban != 'true' and ban != 'false':
            return '{"ok": false, "code": 1004, "message": "Invalid value: Ban (ban)."}'
        post_data = {'id': uid, 'ban': ban, 'level': level, 'expires': expires, 'reason': reason}
        _thread.start_new_thread(
            postmanager.notify_all,
            (post_data, dbmgr.get_post_list())
        )
        return '{"ok": true, "code": 1000, "message": "Processing"}'
    if method == 'new_key':
        keyid = request.values.get("keyid", "__invalid__")
        post_url = request.values.get("post_url", "__invalid__")
        try:
            keyid = int(keyid)
        except ValueError as e:
            return '{"ok": false, "code": 1003, "message": "Invalid value: Key ID (keyid)."}'
        if post_url == '__invalid__':
            return '{"ok": false, "code": 1003, "message": "Invalid value: Post URL (post_url)."}'
        dbmgr.add_post_task(keyid, post_url)
        return '{"ok": true, "code": 1000, "message": "Success!"}'
    if method == 'remove_key':
        keyid = request.values.get("keyid", "__invalid__")
        try:
            keyid = int(keyid)
        except ValueError as e:
            return '{"ok": false, "code": 1003, "message": "Invalid value: Key ID (keyid)."}'
        dbmgr.remove_post_task(keyid)
        return '{"ok": true, "code": 1000, "message": "Success!"}'
    return 'failed: unknown error.'

def run_web_app():
    app.run(
        host = BIND,
        port = PORT,
        threaded = True,
        debug = DEBUG
    )

def create_daemon():
    try:
        if os.fork() > 0: os._exit(0)
    except OSError as error:
        print('fork #1 failed: %d (%s)' % (error.errno, error.strerror))
        os._exit(1)    
    os.chdir('/')
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork()
        if pid > 0:
            print('Daemon PID %d' % pid)
            pidfile = open('/tmp/postapi.pid', 'w')
            pidfile.writelines(str(pid))
            pidfile.close()
            os._exit(0)
    except OSError as error:
        print('fork #2 failed: %d (%s)' % (error.errno, error.strerror))
        os._exit(1)
    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdout = open('/dev/null', 'r')
    #si = open("/dev/null", 'r')
    #so = open("/dev/null", 'a+')
    #se = open("/dev/null", 'a+', 0)
    #os.dup2(si.fileno(), sys.stdin.fileno())
    #os.dup2(so.fileno(), sys.stdout.fileno())
    #os.dup2(se.fileno(), sys.stderr.fileno())
    run_web_app()

if __name__ == '__main__': 
    if platform.system() == "Linux":
        if FORKPROCESS:
            create_daemon()
        else:
            run_web_app()
    else:
        run_web_app()