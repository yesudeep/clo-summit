#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from appengine_utilities.sessions import Session

class SessionUser(object):
    """
    A SessionUser object keeps track of user state.
    """
    def __init__(self, **kwargs):
        self.dictionary = kwargs
        for key, val in kwargs.iteritems():
            setattr(self, key, val)

    def to_dict(self):
        return self.dictionary

class SessionRequestHandler(webapp.RequestHandler):
    """
    A SessionRequestHandler handler contains information about
    the current session.  It depends on the appengine_utilities.sessions
    package to maintain a session.
    """
    def __init__(self):
        webapp.RequestHandler.__init__(self)
        self.session = Session()
        if not 'is_logged_in' in self.session:
            self.session['is_logged_in'] = False

    def get_session_user(self):
        if self.is_logged_in():
            session_user = SessionUser(
                username = self.session.get('username', ''),
                nickname = self.session.get('nickname', ''),
                email = self.session.get('email', '')
            )
            return session_user
        else:
            return None

    def log_in(self, session_user):
        self.session['username'] = session_user.username
        self.session['nickname'] = session_user.nickname
        self.session['email'] = session_user.email
        self.session['is_logged_in'] = True

    def log_out(self):
        self.session['is_logged_in'] = False

    def is_logged_in(self):
        return self.session['is_logged_in']

class RPXSessionRequestHandler(webapp.RequestHandler):
    def __init__(self):
        webapp.RequestHandler.__init__(self)
        self.session = Session()
        if not 'is_logged_in' in self.session:
            self.session['is_logged_in'] = False

    def get_session_user(self):
        if self.is_logged_in():
            session_user = SessionUser(
                identifier = self.session.get('identifier', ''),
                username = self.session.get('username', ''),
                nickname = self.session.get('nickname', ''),
                email = self.session.get('email', ''),
                auth_provider = self.session.get('auth_provider', ''),
                phone_number = self.session.get('phone_number', ''),
                )
            return session_user
        else:
            return None

    def log_in(self, session_user):
        self.session['identifier'] = session_user.identifier
        self.session['username'] = session_user.username
        self.session['nickname'] = session_user.nickname
        self.session['auth_provider'] = session_user.auth_provider
        self.session['email'] = session_user.email
        self.session['phone_number'] = session_user.phone_number
        self.session['is_logged_in'] = True

    def log_out(self):
        self.session['is_logged_in'] = False

    def is_logged_in(self):
        return self.session['is_logged_in']

