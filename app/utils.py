# -*- coding: utf-8 -*-

import configuration as config
from jinja2 import Environment, FileSystemLoader
from functools import partial
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api.labs import taskqueue
from appengine_utilities.sessions import Session
import urllib

jinja_env = Environment(loader=FileSystemLoader(['templates']))

#Jinja2 custom filters
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    if value and hasattr(value, 'strftime'):
        formatted_datetime = value.strftime(format)
    else:
        formatted_datetime = ""
    return formatted_datetime

jinja_env = Environment(loader=FileSystemLoader(['templates']))
jinja_env.filters['datetimeformat'] = datetimeformat
jinja_env.filters['urlencode'] = urllib.urlencode

dec = partial(int, base=10)

def render_template(template_name, **context):
	template = jinja_env.get_template(template_name)
	new_context = {}
	new_context.update(config.TEMPLATE_BUILTINS)
	new_context.update(context)
	return template.render(new_context)

from datetime import datetime

def get_iso_datetime_string(date_object):
  return date_object.strftime('%Y-%m-%dT%H:%M:%S')

def login_required_signup(handler_method):
    """A decorator to require that a user be logged in to access a handler.

    To use it, decorate your get() method like this:

    @login_required('/profile/')
    def get(self):
      user = users.get_current_user(self)
      self.response.out.write('Hello, ' + user.nickname())

    We will redirect to a login page if the user is not logged in. We redirect to the request URI,
    if redirect_uri is not specified and Google Accounts only redirects back as a GET
    request, so this should not be used for POSTs.
    """
    def check_login(self, *args):
        if self.request.method != 'GET':
            raise webapp.Error('The check_login decorator can only be used for GET '
                         'requests')
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url('/account/signup/?continue=' + self.request.uri))
            return
        else:
            handler_method(self, *args)
    return check_login

