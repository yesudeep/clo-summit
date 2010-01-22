#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging

from os.path import dirname, abspath, realpath, join as path_join


DIR_PATH = abspath(dirname(realpath(__file__)))
EXTRA_LIB_PATH = [
    path_join(DIR_PATH, 'lib'),
    path_join(DIR_PATH, 'lib', 'libs.zip'),
    dirname(DIR_PATH),
]
sys.path = EXTRA_LIB_PATH + sys.path

# Local imports go here.

logging.basicConfig(level=logging.DEBUG)

def sanitize_url(url):
    if not url.endswith('/'):
        url = url + '/'
    return url

from google.appengine.api import users

# See http://code.google.com/appengine/articles/gdata.html
APPLICATION_ID = os.environ['APPLICATION_ID']
APPLICATION_NAME = 'CLO Summit'
APPLICATION_URL = "clo-summit.appspot.com"
SERVER_PORT = os.environ['SERVER_PORT']
SERVER_NAME = os.environ['SERVER_NAME']
SERVER_SOFTWARE = os.environ['SERVER_SOFTWARE']
PRODUCTION_HTTP_PORT = 80


DEPLOYMENT_MODE_DEVELOPMENT = 'development'
DEPLOYMENT_MODE_PRODUCTION = 'production'

#DEPLOYMENT_MODE = 'development' if 'Development' in SERVER_SOFTWARE else 'production'
if SERVER_PORT and SERVER_PORT != str(PRODUCTION_HTTP_PORT):
    DEPLOYMENT_MODE = DEPLOYMENT_MODE_DEVELOPMENT
    HOST_NAME = '%s:%s' % (SERVER_NAME, SERVER_PORT)
else:
    DEPLOYMENT_MODE = DEPLOYMENT_MODE_PRODUCTION
    HOST_NAME = SERVER_NAME

#logging.debug(HOST_NAME)

NO_REPLY_EMAIL = 'no-reply@closummit.com'
ADMIN_EMAIL = 'administrator@closummit.com'
REGISTER_EMAIL = 'register@closummit.com'
SURVEY_EMAIL = 'survey@closummit.com'
SPONSORS_EMAIL = 'sponsors@closummit.com'
SPEAKERS_EMAIL = 'speakers@closummit.com'

SPEAKERS_MAILBOX = 'speakers@leapvault.com'
SPONSORS_MAILBOX = 'sponsors@leapvault.com'
REGISTER_MAILBOX = 'register@leapvault.com'

MAIL_SIGNATURE = '''Sincerely,
Team CLO Summit
--
Please visit http://www.closummitindia.com for updates about the event.
'''
NO_REPLY_MAIL_SIGNATURE = MAIL_SIGNATURE + '''
--
Please do not reply to this system generated message.
'''

if DEPLOYMENT_MODE == DEPLOYMENT_MODE_DEVELOPMENT:
    LOCAL = True
    DEBUG = True
    #PRIMARY_URL = '/'
    SECURE_URL = '/'
    #MINIFIED = ''
    MINIFIED = '-min'
else:
    LOCAL = False
    DEBUG = False
    #ABSOLUTE_ROOT_URL = 'http://www.closummit.com/'
    #PRIMARY_URL = 'http://www.closummit.com/'
    SECURE_URL = 'https://%s.appspot.com/' % APPLICATION_ID
    MINIFIED = '-min'

ABSOLUTE_ROOT_URL = 'http://%s:%s/' % (SERVER_NAME, SERVER_PORT)
PRIMARY_URL = ABSOLUTE_ROOT_URL
MEDIA_URL = PRIMARY_URL + 's/'

TEMPLATE_BUILTINS = {
    'LOCAL': LOCAL,
    'APPLICATION_NAME': APPLICATION_NAME,
    'APPLICATION_URL': sanitize_url(APPLICATION_URL),
    'ABSOLUTE_ROOT_URL': sanitize_url(ABSOLUTE_ROOT_URL),
    'MEDIA_URL': sanitize_url(MEDIA_URL),
    'PRIMARY_URL': sanitize_url(PRIMARY_URL),
    'SECURE_URL': sanitize_url(SECURE_URL),
    'TEMPLATE_DEBUG': DEBUG,
    'MINIFIED': MINIFIED,
    'MAIL_SIGNATURE': MAIL_SIGNATURE,
    'NO_REPLY_MAIL_SIGNATURE': NO_REPLY_MAIL_SIGNATURE,
}

TEMPLATE_DIRS = [
    path_join(DIR_PATH, 'templates'),
]

