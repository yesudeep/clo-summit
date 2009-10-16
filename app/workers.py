#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configuration as config
from google.appengine.ext import webapp
from google.appengine.api import mail, memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import render_template
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

# Workers should be idempotent.  Very rare duplicate emails are OK.
# We can manage idempotence to a fair degree with memcache.
def send_mail_worker(cache_key, request, template_name, template_values, to, subject, sender=config.NO_REPLY_EMAIL, reply_to=None):
    key = request.path + ' sent to: ' + to + ' from: ' + sender + cache_key
    logging.info('Attempting mail worker: ' + key)
    logging.info(request)
    if not memcache.get(key):
        body = render_template(template_name, **template_values)
        if reply_to:
            kwargs = dict(reply_to=reply_to)
        else:
            kwargs = {}
        mail.send_mail(sender=sender,
            to=to,
            subject=subject,
            body=body, **kwargs)
        logging.info("Mail Worker: " + key)
        memcache.set(key, True, 120)
        logging.info('not memcached + sent')
    logging.info('memcached + not sending again')

class SurveyParticipationThanksWorker(webapp.RequestHandler):
    def post(self):
        template_values = {
            'full_name': self.request.get('full_name'),
            'survey_link': self.request.get('survey_link'),
        }
        send_mail_worker(cache_key=self.request.get('key'),
            request=self.request,
            to=self.request.get('email'),
            subject='[CLO Summit] Thank you for participating in the CLO survey.',
            template_name='email/thanks/survey_participation.text',
            template_values=template_values,
            reply_to=config.SURVEY_EMAIL
        )
        self.response.out.write("Survey participation thanks.")

class RegistrationThanksWorker(webapp.RequestHandler):
    def post(self):

        template_values = {
            'full_name': self.request.get('full_name')
        }
        send_mail_worker(cache_key=self.request.get('key'),
            request=self.request,
            to=self.request.get('email'),
            subject='[CLO Summit] Thank you for registering for the CLO Summit',
            template_name='email/thanks/registration.text',
            template_values=template_values,
            reply_to=config.REGISTER_MAILBOX
        )
        self.response.out.write("Registration attendee thanks.")

class RegistrationPaymentThanksWorker(webapp.RequestHandler):
    def post(self):
        template_values = {
            'full_name': self.request.get('full_name'),
            'transaction_amount': self.request.get('transaction_amount'),
        }
        send_mail_worker(cache_key=self.request.get('key'),
            request=self.request,
            to=self.request.get('email'),
            subject='[CLO Summit] Thank you for your payment',
            template_name='email/thanks/registration_payment.text',
            template_values=template_values,
            reply_to=config.REGISTER_MAILBOX
        )
        self.response.out.write("Registration attendee thanks.")


class SpeakerNominationThanksWorker(webapp.RequestHandler):
    def post(self):
        template_values = {
            'full_name': self.request.get('full_name'),
            'today': datetime.utcnow()
        }
        send_mail_worker(cache_key=self.request.get('key'),
            request=self.request,
            to=self.request.get('email'),
            subject='[CLO Summit] Thank you for nominating a speaker',
            template_name='email/thanks/speaker_nomination.text',
            template_values=template_values,
            reply_to=config.SPEAKERS_MAILBOX
        )
        self.response.out.write("Speaker nomination thanks.")

urls = [
    ('/worker/mail/thanks/survey_participation/?', SurveyParticipationThanksWorker),
    ('/worker/mail/thanks/registration/?', RegistrationThanksWorker),
    ('/worker/mail/thanks/registration_payment/?', RegistrationPaymentThanksWorker),
    ('/worker/mail/thanks/speaker_nomination/?', SpeakerNominationThanksWorker),
]
application = webapp.WSGIApplication(urls, debug=config.DEBUG)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()

