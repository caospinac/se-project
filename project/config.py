import urllib.parse as urlparse
import os


PRODUCTION = True

if PRODUCTION:
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    DB_USER = url.username
    DB_PASSWORD = url.password
    DB_HOST = url.hostname
    DB_PORT = url.port
    DB_NAME = url.path[1:]
    PORT = int(os.environ['PORT'])
else:
    DB_USER = 'postgres'
    DB_PASSWORD = 'pgsql'
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'scinet'
    PORT = 8000

server = {
    'HOST': '0.0.0.0',
    'PORT': PORT,
    'DEBUG': True  # not PRODUCTION,
}

database = {
    'DB_CLIENT': 'sqlite',
    'DB_TEST_CLIENT': 'sqlite',
    'DB_USER': DB_USER,
    'DB_PASSWORD': DB_PASSWORD,
    'DB_HOST': DB_HOST,
    'DB_PORT': DB_PORT,
    'DB_NAME': DB_NAME,
    'DB_TEST_NAME': 'test.sqlite',
    'SQL_DEBUG': not PRODUCTION,
}

SALT = 'fadfGADG.,[g5asfe$78dsfdfgfg//?¿678.-.-'
