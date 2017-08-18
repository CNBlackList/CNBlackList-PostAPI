import json

class Config:

    def __init__(self, config_path = None):
        if config_path == None:
            f=open('./config.json','r')
        else:
            f=open(config_path,'r')
        j=f.read()
        j=json.loads(j)
        try:
            self.BIND = j['bind']
        except KeyError:
            print('Invalid bind address, exiting.')
            exit()
        try:
            self.PORT = j['port']
        except KeyError:
            print('Invalid port, exiting.')
            exit()
        try:
            self.DEBUG_MODE = j['debug_mode']
        except KeyError:
            print('debug_mode must be true or false, exiting.')
            exit()
        try:
            self.ACCESS_KEY = j['access_key']
        except KeyError:
            print('access_key cannot be null, exiting.')
            exit()
        try:
            self.REQUEST_PATH = j['request_path']
        except KeyError:
            print('request_path cannot be null, exiting.')
            exit()

    def get_config(self):
        return {
            'bind': self.BIND,
            'port': self.PORT,
            'debug_mode': self.DEBUG_MODE,
            'access_key': self.ACCESS_KEY,
            'request_path': self.REQUEST_PATH
        }