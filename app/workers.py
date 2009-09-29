#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configuration as config
from google.appengine.api import mail, memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import render_template
import logging

logging.basicConfig(level=logging.DEBUG)

MAIL_SENDER = config.MAIL_SENDER
ADMIN_MAIL_SENDER = config.ADMIN_MAIL_SENDER

# Workers should be idempotent.  Very rare duplicate emails are OK.
# We can manage idempotence to a fair degree with memcache.
def send_mail_worker(request, sender, to, subject, template_name, template_values):
    key = request.path + ' sent to ' + to + ' from ' + sender
    if not memcache.get(key):
        body = render_template(template_name, **template_values)
        mail.send_mail(sender=sender,
            to=to,
            subject=subject,
            body=body)
        logging.info(key)
        memcache.set(key, True, 120)
        logging.info('not memcached + sent')
    logging.info('memcached + not sending again')


class SurveyParticipationThanksWorker(webapp.RequestHandler):
    def post(self):
        template_values = {
            'full_name': self.request.get('full_name'),
            'survey_link': self.request.get('survey_link'),
        }
        send_mail_worker(request=self.request,
            sender=config.SURVEY_EMAIL,
            to=self.request.get('email'),
            subject='[CLO Summit] Thank you for participating in the CLO survey.',
            template_name='email/thanks/survey_participation.text',
            template_values=template_values)
        )

class RegistrationThanksWorker(webapp.RequestHandler):
    def post(self):
        template_values = {
            'full_name': self.request.get('full_name'),
        }
        send_mail_worker(request=self.request,
            sender=config.REGISTER_EMAIL,
            to=self.request.get('email'),
            subject='[CLO Summit] Thank you for registering for the CLO Summit',
            template_name='email/thanks/registration.text',
            template_values=template_values)
        )

class SpeakerNominationThanksWorker(webapp.RequestHandler):
    def post(self):
        template_values = {
            'full_name': self.request.get('full_name'),
        }
        send_mail_worker(request=self.request,
            sender=config.SPEAKERS_EMAIL,
            to=self.request.get('email'),
            subject='[CLO Summit] Thank you for nominating a speaker',
            template_name='email/thanks/speaker_nomination.text',
            template_values=template_values)
        )

urls = [
    ('/worker/mail/thanks/survey_participation/?', SurveyParticipationThanksWorker),
    ('/worker/mail/thanks/registration/?', RegistrationThanksWorker),
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

