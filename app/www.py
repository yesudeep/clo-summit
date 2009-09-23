#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configuration as config
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import render_template, dec
#from appengine_utilities import Session
import logging

logging.basicConfig(level=logging.INFO)

class IndexPage(webapp.RequestHandler):
    def get(self):
        response = render_template('index.html')
        self.response.out.write(response)

class ProgramPage(webapp.RequestHandler):
    def get(self):
        response = render_template('program.html')
        self.response.out.write(response)

class ResearchPage(webapp.RequestHandler):
    def get(self):
        response = render_template('research/research.html')
        self.response.out.write(response)

class SponsorsPage(webapp.RequestHandler):
    def get(self):
        response = render_template('sponsors.html')
        self.response.out.write(response)

class MediaPage(webapp.RequestHandler):
    def get(self):
        response = render_template('media.html')
        self.response.out.write(response)

class AboutPage(webapp.RequestHandler):
    def get(self):
        response = render_template('about.html')
        self.response.out.write(response)

class RegisterPricingHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('register/pricing.html')
        self.response.out.write(response)

class RegisterPaymentHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('register/payment.html')
        self.response.out.write(response)

class RegisterParticipantsHandler(webapp.RequestHandler):
    def get(self):
        count = dec(self.request.get('count'))
        response = render_template('register/participants.html', count=count)
        self.response.out.write(response)

    def post(self):
        count = dec(self.request.get('count'))
        response = render_template('register/payment.html')
        self.response.out.write(response)

class ParticipatePage(webapp.RequestHandler):
    def get(self):
        response = render_template('research/participate.html')
        self.response.out.write(response)

class SpeakerPage(webapp.RequestHandler):
    def get(self):
        response = render_template('speaker.html')
        self.response.out.write(response)



urls = (
    ('/', IndexPage),
    ('/program/?', ProgramPage),
    ('/research/?', ResearchPage),
    ('/research/participate/?', ParticipatePage),
    ('/sponsors/?', SponsorsPage),
    ('/media/?', MediaPage),
    ('/register/pricing/?', RegisterPricingHandler),
    ('/register/payment/?', RegisterPaymentHandler),
    ('/register/participants/?', RegisterParticipantsHandler),
    ('/about/?', AboutPage),
    ('/speaker/?', SpeakerPage),
)

application = webapp.WSGIApplication(urls)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
    main()

