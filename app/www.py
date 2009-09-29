#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configuration as config
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import render_template, dec
#from appengine_utilities import Session
from models import Participant, ParticipantGroup, SurveyParticipant, Speaker, JOB_TYPE_TUPLE_MAP, get_pricing_per_individual, SURVEY_LINK
from hc_gae_util.sessions import SessionRequestHandler
from decimal import Decimal
from utils import queue_mail_task
from os.path import splitext
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
        response = render_template('research/research.html', survey_link=SURVEY_LINK)
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

class RegisterPricingHandler(SessionRequestHandler):
    def get(self):
        response = render_template('register/pricing.html')
        self.response.out.write(response)

class RegisterPaymentHandler(SessionRequestHandler):
    def get(self):
        participants = self.session.get('participants', None)
        total_price = self.session.get('total_price', None)
        if participants:
            db.put(participants)
            for participant in participants:
                queue_mail_task(url='/worker/mail/thanks/registration/',
                    params=dict(
                        full_name=participant.full_name,
                        email = participant.email,
                        key=str(participant.key())
                    ),
                    method='POST'
                )
            response = render_template('register/payment.html', participants=participants, total_price=total_price)
            self.response.out.write(response)
        else:
            self.redirect('/register/pricing/')

class RegisterParticipantsHandler(SessionRequestHandler):
    def get(self):
        count = dec(self.request.get('count'))
        minimum = dec(self.request.get('min'))
        response = render_template('register/participants.html', count=count, minimum=minimum)
        self.response.out.write(response)

    def post(self):
        count = dec(self.request.get('count'))
        pricing = Decimal(str(get_pricing_per_individual(count)))

        total_price = Decimal('0')
        participants = []

        group = ParticipantGroup()
        group.put()

        for x in range(count):
            i = str(x + 1)

            full_name = self.request.get('full_name_' + i)
            if full_name:
                participant = Participant()
                participant.full_name = full_name
                participant.email = self.request.get('email_' + i)
                participant.mobile_number = self.request.get('mobile_number_' + i)
                participant.address = self.request.get('address_' + i)
                participant.phone_number = self.request.get('phone_number_' + i)
                participant.designation = self.request.get('designation_' + i)
                participant.organization = self.request.get('organization_' + i)
                participant.department = self.request.get('department_' + i)
                participant.pricing = pricing
                participant.group = group
                total_price += pricing
                participants.append(participant)

        self.session['total_price'] = total_price
        self.session['participant_count'] = count
        self.session['participants'] = participants

        self.redirect('/register/payment/')

class ParticipatePage(webapp.RequestHandler):
    def get(self):
        response = render_template('research/participate.html', job_types=JOB_TYPE_TUPLE_MAP)
        self.response.out.write(response)

    def post(self):
        survey_participant = SurveyParticipant()
        survey_participant.full_name = self.request.get('full_name')
        survey_participant.designation = self.request.get('designation')
        survey_participant.department = self.request.get('department')
        survey_participant.job_type = self.request.get('job_type')
        survey_participant.organization = self.request.get('organization')
        survey_participant.organization_website = self.request.get('organization_website')
        survey_participant.city = self.request.get('city')
        survey_participant.email = self.request.get('email')
        survey_participant.mobile_number = self.request.get('mobile_number')
        survey_participant.put()

        queue_mail_task(url='/worker/mail/thanks/survey_participation/',
            params=dict(
                full_name=survey_participant.full_name,
                email = survey_participant.email,
                survey_link=SURVEY_LINK,
                key=str(survey_participant.key())
            ),
            method='POST'
        )

        response = render_template('thank_you.html', message_title="Thank you for participating in the survey.", message_body="We appreciate you taking the time to participate in the survey.  We shall contact you within 48 hours.")
        self.response.out.write(response)

class SpeakerNominationHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('speaker.html')
        self.response.out.write(response)

    def post(self):
        presentation_filename = self.request.get('presentation_filename')

        speaker = Speaker()
        speaker.full_name = self.request.get('full_name')
        speaker.designation = self.request.get('designation')
        speaker.organization = self.request.get('organization')
        speaker.department = self.request.get('department')
        speaker.organization_website = self.request.get('organization_website')
        speaker.city = self.request.get('city')
        speaker.email = self.request.get('email')
        speaker.mobile_number = self.request.get('mobile_number')
        speaker.research_topic = self.request.get('research_topic')
        speaker.bio_sketch = self.request.get('bio_sketch')
        speaker.presentation = db.Blob(self.request.get('presentation'))
        speaker.presentation_filename = presentation_filename
        speaker.presentation_extension = splitext(presentation_filename)[1]
        speaker.put()

        queue_mail_task(url='/worker/mail/thanks/speaker_nomination/',
            params=dict(
                full_name=speaker.full_name,
                email = speaker.email,
                key=str(speaker.key())
            ),
            method='POST'
        )

        response = render_template('thank_you.html', message_title='Thank you for nominating a speaker.', message_body='We appreciate your taking the time to nominating a speaker.  We will get in touch with you soon')
        self.response.out.write(response)

urls = (
    ('/', IndexPage),
    ('/about/?', AboutPage),
    ('/media/?', MediaPage),
    ('/program/?', ProgramPage),
    ('/research/?', ResearchPage),
    ('/sponsors/?', SponsorsPage),
    ('/speaker/nominate/?', SpeakerNominationHandler),
    ('/research/participate/?', ParticipatePage),
    ('/register/pricing/?', RegisterPricingHandler),
    ('/register/payment/?', RegisterPaymentHandler),
    ('/register/participants/?', RegisterParticipantsHandler),
)

application = webapp.WSGIApplication(urls, debug=config.DEBUG)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()

