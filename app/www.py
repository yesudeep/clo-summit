#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configuration as config
import logging

from decimal import Decimal, ROUND_DOWN, ROUND_UP
from google.appengine.api import memcache
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from hc_gae_util.data.countries import COUNTRIES_SELECTION_LIST
from hc_gae_util.data.geoip import ip_address_to_country_code
from hc_gae_util.sessions import SessionRequestHandler
from hc_gae_util.urlhelper import url_join_path
from os.path import splitext
from utils import queue_mail_task, render_template, dec
from datetime import datetime

from models import Participant, ParticipantGroup, SurveyParticipant, Speaker, \
    JOB_TYPE_TUPLE_MAP, get_pricing_per_individual, SURVEY_LINK, BillingSettings, \
    TRANSACTION_TYPE_EBS, PRICING_TAX, EARLY_BIRD_OFFER_END_DATE, HostInformation
from ebs.merchant.data import MODE_DEVELOPMENT, MODE_PRODUCTION, PAYMENT_GATEWAY_URL
from ebs_properties import ShippingContact, BillingContact, BillingInformation

if config.DEPLOYMENT_MODE == config.DEPLOYMENT_MODE_PRODUCTION:
    ebs_mode = MODE_PRODUCTION
elif config.DEPLOYMENT_MODE == config.DEPLOYMENT_MODE_DEVELOPMENT:
    ebs_mode = MODE_DEVELOPMENT

logging.basicConfig(level=logging.INFO)

def get_host_info(request):
    host_info = HostInformation()
    host_info.ip_address = request.remote_addr
    host_info.http_user_agent = request.headers.get('User-Agent', '')
    host_info.http_accept_language = request.headers.get('Accept-Language', '')
    host_info.http_accept_encoding = request.headers.get('Accept-Encoding', '')
    host_info.http_accept_charset = request.headers.get('Accept-Charset', '')
    host_info.http_accept = request.headers.get('Accept', '')
    host_info.http_referer = request.headers.get('Referer', '')
    return host_info

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
        values = {
            'early_bird_offer_end_date': EARLY_BIRD_OFFER_END_DATE,
            'today_date': datetime.utcnow().date(),
        }
        response = render_template('register/pricing.html', **values)
        self.response.out.write(response)

class RegisterPaymentHandler(SessionRequestHandler):
    def get(self):
        participants = self.session.get('participants', None)
        if participants:
            db.put(participants)
            self.session['participants'] = participants
            total_price = self.session.get('total_price', None)
            tax_amount = self.session.get('tax_amount', None)
            calculated_price = self.session.get('calculated_price', None)
            group = self.session['participant_group']
            #primary_participant = self.session.get('primary_participant')
            primary_participant = Participant.get_primary_participant_for_group(group)
            self.session['primary_participant'] = primary_participant
            participant_count = self.session.get('participant_count')
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
            #primary_participant.put()
            billing_settings = BillingSettings.get_settings(deployment_mode=ebs_mode)

            billing_contact = BillingContact(name=primary_participant.full_name, \
                phone=primary_participant.phone_number, \
                email=primary_participant.email,
                address=primary_participant.address, \
                city=primary_participant.city, \
                postal_code=primary_participant.zip_code, \
                state=primary_participant.state_province, \
                country=primary_participant.country_code)
            shipping_contact = ShippingContact(name=primary_participant.full_name, \
                phone=primary_participant.phone_number, \
                email=primary_participant.email,
                address=primary_participant.address, \
                city=primary_participant.city, \
                postal_code=primary_participant.zip_code, \
                state=primary_participant.state_province, \
                country=primary_participant.country_code)
            billing_information = BillingInformation(account_id=billing_settings.account_id, \
                reference_no=group.key().id(), \
                amount=total_price, \
                mode=ebs_mode, \
                description= str(total_price) + ' for ' + str(participant_count) + ' participant(s) to attend CLO Summit.', \
                return_url=url_join_path(config.ABSOLUTE_ROOT_URL, '/billing/ebs?DR={DR}'))
            d = {}
            d.update(billing_contact.fields())
            d.update(shipping_contact.fields())
            d.update(billing_information.fields())
            form_fields = [(k,v) for (k,v) in d.iteritems()]

            response = render_template('register/payment.html',
                form_fields=form_fields,
                payment_gateway_url=PAYMENT_GATEWAY_URL,
                participants=participants,
                total_price=total_price,
                tax_amount=tax_amount,
                calculated_price=calculated_price)
            self.response.out.write(response)
        else:
            self.redirect('/register/pricing/')

class BillingProviderEBSHandler(SessionRequestHandler):
    def get(self):
        from pickle import dumps
        from ebs.merchant.api import get_ebs_request_parameters

        dr = self.request.get('DR')
        if dr:
            billing_settings = BillingSettings.get_settings(deployment_mode=ebs_mode)
            request = get_ebs_request_parameters(dr, billing_settings.secret_key)

            response_code = request.get('ResponseCode', None)
            response_message = request.get('ResponseMessage', 'There was no response from the billing system.')

            group = self.session.get('participant_group')
            group.transaction_response_id = str(request.get('PaymentID'))
            group.transaction_response_code = str(response_code)
            group.transaction_response_message = response_message
            group.transaction_response_type = TRANSACTION_TYPE_EBS
            group.transaction_response_amount = request.get('Amount', '0')
            group.transaction_response = str(request)
            group.transaction_response_object = db.Blob(dumps(request))
            group.when_transaction_response_occurred = request.get('DateCreated')
            group.put()

            if response_code == 0:
                # mark the participant group as paid.
                message_title = 'Thank you for participating in the summit'
                group_id = group.key().id()
                logging.info('Payments for group: %s with %d processed.' % (group.title, group_id))

                participants = self.session.get('participants')
                if participants:
                    # Send email to all the participants about their attendance.
                    for participant in participants:
                        queue_mail_task(url='/worker/mail/thanks/registration/',
                            params=dict(
                                full_name=participant.full_name,
                                email = participant.email,
                                key=str(participant.key())
                            ),
                            method='POST'
                        )
                    # Send email to the payer the invoice.
                    primary_participant = self.session.get('primary_participant')
                    queue_mail_task(url='/worker/mail/thanks/registration_payment/',
                        params=dict(
                            full_name=primary_participant.full_name,
                            email = primary_participant.email,
                            key=str(primary_participant.key()),
                            transaction_amount=group.transaction_response_amount
                        ),
                        method='POST'
                    )
            else:
                message_title = 'There was an error processing your payment.'
            response = render_template('thank_you.html', message_title=message_title, message_body=response_message + ''' Thank you for registering for the summit. An email confirming your payment and registration shall be sent to you shortly. In case you don't receive the email confirmation within 24 hours or you have any queries, please contact +91 22 66301060 / 22026166 from 10.30 AM IST to 6.30 AM IST''')
        else:
            response = render_template('thank_you.html', message_title="A problem occurred with the billing system.", message_body="We did not receive a proper response from the billing system.")

        self.response.out.write(response)


class RegisterParticipantsHandler(SessionRequestHandler):
    def get(self):
        count = dec(self.request.get('count', '0'))
        minimum = dec(self.request.get('min', '0'))

        if not count:
            self.redirect('/register/pricing/')

        if config.LOCAL:
            country_code = 'IND'
        else:
            country_code = ip_address_to_country_code(self.request.remote_addr, 'IND')
        response = render_template('register/participants.html', count=count, minimum=minimum, country_code=country_code, countries=COUNTRIES_SELECTION_LIST)
        self.response.out.write(response)

    def post(self):
        count = dec(self.request.get('count'))
        pricing = Decimal(str(get_pricing_per_individual(count)))

        total_price = Decimal('0')
        participants = []

        host_info = get_host_info(self.request)
        host_info.put()

        group = ParticipantGroup()
        group.title = self.request.get('organization_1') + '/' + self.request.get('email_1')
        group.host_info = host_info
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

        tax_amount = (total_price * PRICING_TAX)
        tax_amount = tax_amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
        calculated_price = total_price
        total_price = total_price + tax_amount

        self.session['calculated_price'] = calculated_price
        self.session['tax_amount'] = tax_amount
        self.session['total_price'] = total_price
        self.session['participant_count'] = count
        self.session['participants'] = participants
        self.session['participant_group'] = group
        self.session['primary_participant'] = primary_participant



        self.redirect('/register/payment/')

class ParticipatePage(webapp.RequestHandler):
    def get(self):
        response = render_template('research/participate.html', job_types=JOB_TYPE_TUPLE_MAP)
        self.response.out.write(response)

    def post(self):
        host_info = get_host_info(self.request)
        host_info.put()

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
        survey_participant.host_info = host_info
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
        host_info = get_host_info(self.request)
        host_info.put()

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
        speaker.host_info = host_info
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
    ('/unsupported/browser/?', UnsupportedBrowserPage),
    ('/billing/ebs/?', BillingProviderEBSHandler),
)

application = webapp.WSGIApplication(urls, debug=config.DEBUG)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()

