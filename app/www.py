#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configuration as config
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import render_template


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
        response = render_template('research.html')
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

class RegisterPage(webapp.RequestHandler):
    def get(self):
        response = render_template('register.html')
        self.response.out.write(response)

class SpeakerPage(webapp.RequestHandler):
    def get(self):
        response = render_template('speaker.html')
        self.response.out.write(response)


urls = (
    ('/', IndexPage),
    ('/program/?', ProgramPage),
    ('/research/?', ResearchPage),
    ('/sponsors/?', SponsorsPage),
    ('/media/?', MediaPage),
    ('/register/?', RegisterPage),
    ('/about/?', AboutPage),
    ('/speaker/?', SpeakerPage),
)


application = webapp.WSGIApplication(urls)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
    main()


