#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from datetime import datetime
from hc_gae_util.db.models import RegularModel
from hc_gae_util.db.properties import DecimalProperty

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

PRICING = [
    7500, 7500,              # 1-2
    6500, 6500, 6500, 6500,  # 3-6
    6000, 6000, 6000         # 7-9
]

SURVEY_LINK = "http://www.surveymonkey.com/s.aspx?sm=hZXdTol4KmfnW0ZBoxxaow_3d_3d"

def get_pricing_per_individual(count=1, min_price=5500):
    if count >= len(PRICING):
        return min_price
    else:
        return PRICING[count-1]

class ParticipantGroup(RegularModel):
    pass

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
    group = db.ReferenceProperty(ParticipantGroup, collection_name='participants')

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

