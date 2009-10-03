#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configuration as config
import logging
from google.appengine.api import users, memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import render_template, dec
import utils
import models

logging.basicConfig(level=logging.DEBUG)

class ParticipantsHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('admin/generic_list.html', page_name='participants', page_description='Participants for the event.')
        self.response.out.write(response)

class SurveyParticipantsHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('admin/generic_list.html', page_name='survey_participants', page_description='Survey participants.')
        self.response.out.write(response)

class SpeakersHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('admin/generic_list.html', page_name='speakers', page_description='Speakers for the event.')
        self.response.out.write(response)

urls = [
	('/admin/?', ParticipantsHandler),
	('/admin/speakers/?', SpeakersHandler),
	('/admin/survey_participants/?', SurveyParticipantsHandler),
    ('/admin/participants/?', ParticipantsHandler),
]
application = webapp.WSGIApplication(urls, debug=config.DEBUG)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
	main()

