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


urls = (
    ('/', IndexPage),
)


application = webapp.WSGIApplication(urls)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
    main()


