#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configuration as config
import logging

from decimal import Decimal
from google.appengine.api import memcache
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from hc_gae_util.data.countries import COUNTRIES_SELECTION_LIST
from hc_gae_util.data.geoip import ip_address_to_country_code
from hc_gae_util.sessions import SessionRequestHandler
from os.path import splitext
from utils import queue_mail_task, render_template, dec

from models import Participant, ParticipantGroup, SurveyParticipant, Speaker, JOB_TYPE_TUPLE_MAP, get_pricing_per_individual, SURVEY_LINK, BillingSettings
from ebs import MODE_DEVELOPMENT, MODE_PRODUCTION, PAYMENT_GATEWAY_URL, ShippingContact, BillingContact, BillingInformation

if config.DEPLOYMENT_MODE == config.DEPLOYMENT_MODE_PRODUCTION:
    ebs_mode = MODE_PRODUCTION
elif config.DEPLOYMENT_MODE == config.DEPLOYMENT_MODE_DEVELOPMENT:
    ebs_mode = MODE_DEVELOPMENT

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
        if participants:
            total_price = self.session.get('total_price', None)
            primary_participant = self.session.get('primary_participant')
            participant_count = self.session.get('participant_count')
            db.put(participants)
#           This mail should go in the thank you part after receiving successful payment from payment gateway.
#            for participant in participants:
#                queue_mail_task(url='/worker/mail/thanks/registration/',
#                    params=dict(
#                        full_name=participant.full_name,
#                        email = participant.email,
#                        key=str(participant.key())
#                    ),
#                    method='POST'
#                )
            primary_participant.put()
            billing_settings = BillingSettings.get_settings(deployment_mode=ebs_mode)

            billing_contact = BillingContact(name=primary_participant.full_name, \
                phone=primary_participant.phone_number, \
                email=primary_participant.email,
                address=primary_participant.address, \
                city=primary_participant.city, \
                postal_code=primary_participant.zip_code, \
                state=primary_participant.state_province, \
                country=primary_participant.country_code)
            shipping_contact = BillingContact(name=primary_participant.full_name, \
                phone=primary_participant.phone_number, \
                email=primary_participant.email,
                address=primary_participant.address, \
                city=primary_participant.city, \
                postal_code=primary_participant.zip_code, \
                state=primary_participant.state_province, \
                country=primary_participant.country_code)
            billing_information = BillingInformation(account_id=billing_settings.account_id, \
                reference_no=primary_participant.key().id(), \
                amount=total_price, \
                mode=ebs_mode, \
                description= str(total_price) + ' for ' + str(participant_count) + ' participant(s) to attend CLO Summit.', \
                return_url='/whatever/url/you/want')
            d = {}
            d.update(billing_contact.fields())
            d.update(shipping_contact.fields())
            d.update(billing_information.fields())
            form_fields = [(k,v) for (k,v) in d.iteritems()]

            response = render_template('register/payment.html', form_fields=form_fields, payment_gateway_url=PAYMENT_GATEWAY_URL, participants=participants, total_price=total_price)
            self.response.out.write(response)
        else:
            self.redirect('/register/pricing/')

class RegisterParticipantsHandler(SessionRequestHandler):
    def get(self):
        count = dec(self.request.get('count'))
        minimum = dec(self.request.get('min'))
        country_code = ip_address_to_country_code(self.request.remote_addr, 'IND')
        response = render_template('register/participants.html', count=count, minimum=minimum, country_code=country_code, countries=COUNTRIES_SELECTION_LIST)
        self.response.out.write(response)

    def post(self):
        count = dec(self.request.get('count'))
        pricing = Decimal(str(get_pricing_per_individual(count)))

        total_price = Decimal('0')
        participants = []

        group = ParticipantGroup()
        group.put()

        primary_participant = None
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
                participant.country_code = self.request.get('country_code_' + i)
                participant.state_province = self.request.get('state_province_' + i)
                participant.city = self.request.get('city_' + i)
                participant.zip_code = self.request.get('zip_code_' + i)
                participant.pricing = pricing
                if x == 0:
                    participant.is_primary = True
                    primary_participant = participant
                participant.group = group
                total_price += pricing
                participants.append(participant)

        self.session['total_price'] = total_price
        self.session['participant_count'] = count
        self.session['participants'] = participants
        self.session['primary_participant'] = primary_participant

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
        presentation = self.request.get('presentation')

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
        if presentation_filename:
            speaker.presentation = db.Blob(presentation)
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

class UnsupportedBrowserPage(webapp.RequestHandler):
    def get(self):
        cache_key = 'unsupported_browser_page'
        cached_response = memcache.get(cache_key)
        if cached_response:
            self.response.out.write(cached_response)
        else:
            response = render_template('ie.html')
            memcache.set(cache_key, response, 10)
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
    ('/unsupported/browser/?', UnsupportedBrowserPage)
)

application = webapp.WSGIApplication(urls, debug=config.DEBUG)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()

