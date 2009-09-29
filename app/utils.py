# -*- coding: utf-8 -*-

import configuration as config
from jinja2 import Environment, FileSystemLoader
from functools import partial
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api.labs import taskqueue
from appengine_utilities.sessions import Session
import urllib
import logging
from hc_gae_util.jinja_loaders import PythonLoader

jinja_env = Environment(loader=PythonLoader(['templates']))

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

def birthdate_to_tuple(birthdate):
    birthdate_year, birthdate_month, birthdate_day = birthdate.split('-')
    if birthdate_year == '0000':
         birthdate_year = str(models.DEFAULT_BIRTHDATE[0])
    return (dec(birthdate_year), dec(birthdate_month), dec(birthdate_day))

def birthdate_to_string(*birthdate_items):
    return '%d-%d-%d' % birthdate_items

def parse_iso_datetime_string(datetime_string):
    if 'T' in datetime_string:
        date_string, time_string = datetime_string.split('T')
    else:
        date_string = datetime_string
        time_string = '00:00:00'
    year, month, day = date_string.split('-')
    hours, minutes, seconds = time_string.split(':')
    year = dec(year)
    month = dec(month)
    day = dec(day)
    hours = dec(hours)
    minutes = dec(minutes)
    seconds = dec(seconds)
    return datetime(year, month, day, hours, minutes, seconds)



def queue_task(queue_name='default', *args, **kwargs):
    #taskqueue.Task(*args, **kwargs).add(queue_name=queue_name)
    taskqueue.Task(*args, **kwargs).add(queue_name)
    info = ' %(url)s %(method)s' % kwargs
    logging.info('[%s]' % (queue_name,) + info)

def queue_mail_task(*args, **kwargs):
    queue_task(queue_name='mail-queue', *args, **kwargs)

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

