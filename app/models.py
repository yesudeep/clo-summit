#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configuration as config
from google.appengine.api import memcache
from google.appengine.ext import db
from datetime import datetime, date
from hc_gae_util.db.models import RegularModel
from hc_gae_util.db.properties import DecimalProperty
from hc_gae_util.data.countries import COUNTRY_NAME_ISO_ALPHA_3_TABLE, ISO_ALPHA_3_CODES
from ebs.merchant.data import MODE_PRODUCTION, MODE_DEVELOPMENT
from decimal import Decimal

JOB_TYPES = {
    'clo': 'Chief Learning Officer',
    'head_of_learning_development': 'Head of Learning and Development',
    'talent_management': 'Talent Management',
    'employee_development': 'Employee Management',
    'head_of_human_resources': 'Head of Human Resources',
}
JOB_TYPE_CHOICES = JOB_TYPES.keys()
JOB_TYPE_CHOICES.sort()
JOB_TYPE_TUPLE_MAP = [(k, v) for (k, v) in JOB_TYPES.iteritems()]
JOB_TYPE_TUPLE_MAP.sort()

EARLY_BIRD_OFFER_END_DATE = date(2009, 10, 31)

PRICING = [
    7500, 7500,              # 1-2
    6500, 6500, 6500, 6500,  # 3-6
    6000, 6000, 6000,        # 7-9
]
EARLY_BIRD_PRICING = [
    7000, 7000,              # 1-2
    6250, 6250, 6250, 6250,  # 3-6
    5750, 5750, 5750, 5750,  # 7-9
]
PRICING_TAX = Decimal('10.3') / 100

TRANSACTION_TYPE_EBS = 'ebs'
TRANSACTION_TYPES = [
    TRANSACTION_TYPE_EBS,
]

SURVEY_LINK = "http://www.surveymonkey.com/s.aspx?sm=hZXdTol4KmfnW0ZBoxxaow_3d_3d"

MAX_FETCH_LIMIT = 1000

def get_pricing_per_individual(count=1, min_price=5500):
    today = datetime.utcnow()
    if today.date() <= EARLY_BIRD_OFFER_END_DATE:
        pricing = EARLY_BIRD_PRICING
    else:
        pricing = PRICING
    if count >= len(pricing):
        return min_price
    else:
        return pricing[count-1]

class HostInformation(RegularModel):
    ip_address = db.StringProperty()
    http_user_agent = db.StringProperty()
    http_accept_language = db.StringProperty()
    http_accept_charset = db.StringProperty()
    http_accept_encoding = db.StringProperty()
    http_accept = db.StringProperty()
    http_referer = db.StringProperty()

class ParticipantGroup(RegularModel):
    title = db.StringProperty()
    transaction_response_id = db.StringProperty()
    transaction_response_amount = DecimalProperty()
    transaction_response_code = db.StringProperty()
    transaction_response_type = db.StringProperty(choices=TRANSACTION_TYPES)
    transaction_response_message = db.StringProperty()
    transaction_response = db.TextProperty()
    transaction_response_object = db.BlobProperty()
    when_transaction_response_occurred = db.DateTimeProperty()

    host_info = db.ReferenceProperty(HostInformation, collection_name='particpant_groups')

class YahooApiSettings(RegularModel):
    api_key = db.StringProperty()
    boss_id = db.StringProperty()

    @classmethod
    def get_settings(cls):
        cache_key = 'YahooApiSettings.settings'
        yahoo_settings = memcache.get(cache_key)
        if not yahoo_settings:
            yahoo_settings = db.Query(YahooApiSettings).filter('is_deleted =', False).filter('is_active =', True).get()
            memcache.set(cache_key, yahoo_settings, 300)
        return yahoo_settings

class BillingSettings(RegularModel):
    account_id = db.StringProperty()
    secret_key = db.StringProperty()
    deployment_mode = db.StringProperty(choices=[MODE_PRODUCTION, MODE_DEVELOPMENT])

    @classmethod
    def get_settings(cls, deployment_mode=MODE_PRODUCTION):
        cache_key = 'BillingSettings.' + deployment_mode + '.first'
        billing_settings = memcache.get(cache_key)
        if not billing_settings:
            billing_settings = db.Query(BillingSettings) \
                .filter('deployment_mode =', deployment_mode) \
                .filter('is_deleted =', False) \
                .filter('is_active =', True) \
                .get()
            memcache.set(cache_key, billing_settings, 120)
        return billing_settings

class Participant(RegularModel):
    full_name = db.StringProperty()
    email = db.EmailProperty()
    mobile_number = db.StringProperty()
    phone_number = db.StringProperty()
    pricing = DecimalProperty()
    designation = db.StringProperty()
    department = db.StringProperty()
    organization = db.StringProperty()
    address = db.PostalAddressProperty()

    is_primary = db.BooleanProperty(default=False)

    zip_code = db.StringProperty()
    country_code = db.StringProperty(choices=ISO_ALPHA_3_CODES)
    city = db.StringProperty()
    state_province = db.StringProperty()

    group = db.ReferenceProperty(ParticipantGroup, collection_name='participants')

    @classmethod
    def get_primary_participant_for_group(cls, group):
        cache_key = 'Participant.is_primary=True and Participant.group=' + str(group.title)
        participant = memcache.get(cache_key)
        if not participant:
            participant = db.Query(Participant).filter('group =', group).filter('is_primary =', True).get()
            memcache.set(cache_key, participant, 300)
        return participant

    @classmethod
    def get_all(cls):
        cache_key = 'Participant.get_all'
        participants = memcache.get(cache_key)
        if not participants:
            participants = db.Query(Participant).order('full_name').fetch(MAX_FETCH_LIMIT)
            memcache.set(cache_key, participants, 120)
        return participants



class Speaker(RegularModel):
    full_name = db.StringProperty()
    designation = db.StringProperty()
    organization = db.StringProperty()
    department = db.StringProperty()
    organization_website = db.URLProperty()
    city = db.StringProperty()
    email = db.EmailProperty()
    mobile_number = db.StringProperty()
    research_topic = db.StringProperty()
    bio_sketch = db.TextProperty()
    presentation = db.BlobProperty()
    presentation_filename = db.StringProperty()
    presentation_extension = db.StringProperty()

    host_info = db.ReferenceProperty(HostInformation, collection_name='speakers')

    @classmethod
    def get_all(cls):
        cache_key = 'Speaker.get_all_'
        speakers = memcache.get(cache_key)
        if not speakers:
            speakers = db.Query(Speaker).order('full_name').fetch(MAX_FETCH_LIMIT)
            memcache.set(cache_key, speakers, 120)
        return speakers

class SurveyParticipant(RegularModel):
    full_name = db.StringProperty()
    designation = db.StringProperty()
    department = db.StringProperty()
    job_type = db.StringProperty(choices=JOB_TYPE_CHOICES)
    organization = db.StringProperty()
    organization_website = db.URLProperty()
    city = db.StringProperty()
    email = db.EmailProperty()
    mobile_number = db.StringProperty()

    host_info = db.ReferenceProperty(HostInformation, collection_name='survey_participants')

    @classmethod
    def get_all(cls):
        cache_key = 'SurveyParticipant.get_all'
        survey_participants = memcache.get(cache_key)
        if not survey_participants:
            survey_participants = db.Query(SurveyParticipant).order('full_name').fetch(MAX_FETCH_LIMIT)
            memcache.set(cache_key, survey_participants, 120)
        return survey_participants

