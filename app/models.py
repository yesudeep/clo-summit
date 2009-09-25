#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from datetime import datetime
from util.db.models import RegularModel

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
    7500,
    6000,
    6000,
    6000,
    6000,
    5500,
    5500,
    5500
]

class Participant(RegularModel):
    full_name = db.StringProperty()
    email = db.EmailProperty()
    mobile_number = db.StringProperty()
    pricing = db.

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

