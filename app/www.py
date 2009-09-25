#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configuration as config
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import render_template, dec
#from appengine_utilities import Session
import logging
from models import Participant, SurveyParticipant, Speaker, JOB_TYPE_TUPLE_MAP
from util.sessions import SessionRequestHandler

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
        participants = self.session['participants']
        response = render_template('register/payment.html', participants=participants)
        self.response.out.write(response)

class RegisterParticipantsHandler(SessionRequestHandler):
    def get(self):
        count = dec(self.request.get('count'))
        response = render_template('register/participants.html', count=count)
        self.response.out.write(response)

    def post(self):
        count = dec(self.request.get('count'))

        participants = []
        for x in range(count):
            i = str(x + 1)
            participant = Participant()
            participant.full_name = self.request.get('full_name_' + i)
            participant.email = self.request.get('email_' + i)
            participant.mobile_number = self.request.get('mobile_number_' + i)

            participants.append(participant)

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

        response = render_template('thank_you.html', message_title="Thank you for participating in the survey.", message_body="We appreciate you taking the time to participate in the survey.  We shall contact you within 48 hours.")
        self.response.out.write(response)

class SpeakerNominationHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('speaker.html')
        self.response.out.write(response)

    def post(self):
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
        speaker.put()

        response = render_template('thank_you.html', message_title='Thank you for nominating a speaker.', message_body='We appreciate your taking the time to nominating a speaker.  We will get in touch with you soon')
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
    ('/speaker/nominate/?', SpeakerNominationHandler),
)

application = webapp.WSGIApplication(urls, debug=config.DEBUG)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
    main()

