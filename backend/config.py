#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

env_dict = os.environ


class Config:
    _LEO_API_PLATFORM_ENV = env_dict.get('LEO_API_PLATFORM_ENV', 'production')
    _LEO_API_PLATFORM_HOST = env_dict.get('LEO_API_PLATFORM_HOST', '127.0.0.1')
    _LEO_API_PLATFORM_PORT = env_dict.get('LEO_API_PLATFORM_PORT', 8888)
    _LEO_API_PLATFORM_MONGO_HOST = env_dict.get('LEO_API_PLATFORM_MONGO_HOST', '127.0.0.1')
    _LEO_API_PLATFORM_MONGO_PORT = env_dict.get('LEO_API_PLATFORM_MONGO_PORT', 27017)
    _LEO_API_PLATFORM_MONGO_USERNAME = env_dict.get('LEO_API_PLATFORM_MONGO_USERNAME')
    _LEO_API_PLATFORM_MONGO_PASSWORD = env_dict.get('LEO_API_PLATFORM_MONGO_PASSWORD')
    _LEO_API_PLATFORM_MONGO_DBNAME = env_dict.get('LEO_API_PLATFORM_MONGO_DBNAME', 'leo-api-platform-db')
    _LEO_API_PLATFORM_SECRET_KEY = env_dict.get('LEO_API_PLATFORM_SECRET_KEY', 'leo-platform-secret-key')

    def get_env(self):
        return self._LEO_API_PLATFORM_ENV

    def set_env(self, env):
        self._LEO_API_PLATFORM_ENV = env

    def get_port(self):
        if isinstance(self._LEO_API_PLATFORM_PORT, str):
            self._LEO_API_PLATFORM_PORT = int(self._LEO_API_PLATFORM_PORT)
        return self._LEO_API_PLATFORM_PORT

    def set_port(self, port):
        if isinstance(port, str):
            port = int(port)
        self._LEO_API_PLATFORM_PORT = port

    def get_host(self):
        return self._LEO_API_PLATFORM_HOST

    def set_host(self, host):
        self._LEO_API_PLATFORM_HOST = host

    def get_mongo_host(self):
        return self._LEO_API_PLATFORM_MONGO_HOST

    def set_mongo_host(self, host):
        self._LEO_API_PLATFORM_MONGO_HOST = host

    def get_mongo_port(self):
        if isinstance(self._LEO_API_PLATFORM_MONGO_PORT, str):
            self._LEO_API_PLATFORM_MONGO_PORT = int(self._LEO_API_PLATFORM_MONGO_PORT)
        return self._LEO_API_PLATFORM_MONGO_PORT

    def set_mongo_port(self, port):
        if isinstance(port, str):
            port = int(port)
        self._LEO_API_PLATFORM_MONGO_PORT = port

    def get_mongo_username(self):
        return self._LEO_API_PLATFORM_MONGO_USERNAME

    def set_mongo_username(self, username):
        self._LEO_API_PLATFORM_MONGO_USERNAME = username

    def get_mongo_password(self):
        return self._LEO_API_PLATFORM_MONGO_PASSWORD

    def set_mongo_password(self, password):
        self._LEO_API_PLATFORM_MONGO_PASSWORD = password

    def get_mongo_db_name(self):
        return self._LEO_API_PLATFORM_MONGO_DBNAME

    def set_mongo_default_db_name(self, db_name):
        self._LEO_API_PLATFORM_MONGO_DBNAME = db_name

    def get_secret_key(self):
        return self._LEO_API_PLATFORM_SECRET_KEY

    def set_secret_key(self, secret_key):
        self._LEO_API_PLATFORM_SECRET_KEY = secret_key


if __name__ == '__main__':
    config = Config()
    print('LEO_API_PLATFORM_ENV: ----------> %s' % config.get_env())
    print('LEO_API_PLATFORM_HOST: ----------> %s' % config.get_host())
    print('LEO_API_PLATFORM_PORT: ----------> %s' % config.get_port())
    print('LEO_API_PLATFORM_MONGO_HOST: ----------> %s' % config.get_mongo_host())
    print('LEO_API_PLATFORM_MONGO_PORT: ----------> %s' % config.get_mongo_port())
    print('LEO_API_PLATFORM_MONGO_USERNAME: ----------> %s' % config.get_mongo_username())
    print('LEO_API_PLATFORM_MONGO_PASSWORD: ----------> %s' % config.get_mongo_password())
    print('LEO_API_PLATFORM_MONGO_DEFAULT_DBNAME: ----------> %s' % config.get_mongo_db_name())
    print('LEO_API_PLATFORM_SECRET_KEY: ----------> %s' % config.get_secret_key())
