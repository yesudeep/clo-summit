#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configuration as config
from google.appengine.ext import db, webapp
from google.appengine.api import memcache, users
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import queue_mail_task, render_template, dec, parse_iso_datetime_string
import logging
from models import Participant, ParticipantGroup, SurveyParticipant, Speaker, JOB_TYPE_TUPLE_MAP
from datetime import datetime
from django.utils import simplejson as json
from decimal import Decimal
from os.path import splitext

MAX_FETCH_LIMIT = 400

logging.basicConfig(level=logging.INFO)

class UserApproveHandler(webapp.RequestHandler):
    def get(self, key):
        o = db.get(db.Key(key))
        o.is_active = True
        o.wants_activation = False
        o.put()
        queue_mail_task(url='/worker/mail/account_activation_notification/' + key, method='GET')
        self.response.out.write(o.is_active)

class UserUnapproveHandler(webapp.RequestHandler):
    def get(self, key):
        o = db.get(db.Key(key))
        o.is_active = False
        o.put()
        self.response.out.write(o.is_active)

class ApproveHandler(webapp.RequestHandler):
    def get(self, key):
        o = db.get(db.Key(key))
        o.is_active = True
        o.put()
        self.response.out.write(o.is_active)

class UnapproveHandler(webapp.RequestHandler):
    def get(self, key):
        o = db.get(db.Key(key))
        o.is_active = False
        o.put()
        self.response.out.write(o.is_active)

class DeleteHandler(webapp.RequestHandler):
    def get(self, key):
        o = db.get(db.Key(key))
        o.is_deleted = True
        o.put()
        self.response.out.write(o.is_deleted)

class UndeleteHandler(webapp.RequestHandler):
    def get(self, key):
        o = db.get(db.Key(key))
        o.is_deleted = False
        o.put()
        self.response.out.write(o.is_deleted)

class ToggleStarHandler(webapp.RequestHandler):
    def get(self, key):
        o = db.get(db.Key(key))
        o.is_starred = not o.is_starred
        o.put()
        self.response.out.write(o.is_starred)

class SpeakerNewHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('admin/new_speaker.html')
        self.response.out.write(response)

    def post(self, key):
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
        if presentation_filename:
            speaker.presentation = self.request.get('presentation')
            speaker.presentation_filename = self.request.get('presentation_filename')
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

        self.response.out.write(speaker.to_json('full_name', 'is_starred', 'is_deleted', 'is_active'))

class SpeakerEditHandler(webapp.RequestHandler):
    def get(self, key):
        speaker = db.get(db.Key(key))
        response = render_template('admin/edit_speaker.html', speaker=speaker)
        self.response.out.write(response)

    def post(self, key):
        presentation_filename = self.request.get('presentation_filename')
        speaker = db.get(db.Key(key))
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
            speaker.presentation = self.request.get('presentation')
            speaker.presentation_filename = self.request.get('presentation_filename')
            speaker.presentation_extension = splitext(presentation_filename)[1]
        speaker.put()

        self.response.out.write(speaker.to_json('full_name', 'is_starred', 'is_deleted', 'is_active'))

class SpeakerListHandler(webapp.RequestHandler):
    def get(self):
        speakers = Speaker.get_all()
        speaker_list = []
        for speaker in speakers:
            speaker_list.append(speaker.to_json_dict('full_name',
                'is_starred', 'is_active', 'is_deleted', 'when_created'))
        response = json.dumps(speaker_list)
        self.response.out.write(response)

class SurveyParticipantEditHandler(webapp.RequestHandler):
    def get(self, key):
        survey_participant = db.get(db.Key(key))
        response = render_template('admin/edit_survey_participant.html', survey_participant=survey_participant, job_types=JOB_TYPE_TUPLE_MAP)
        self.response.out.write(response)

    def post(self, key):
        survey_participant = db.get(db.Key(key))
        survey_participant.full_name = self.request.get('full_name')
        survey_participant.email = self.request.get('email')
        survey_participant.mobile_number = self.request.get('mobile_number')
        survey_participant.designation = self.request.get('designation')
        survey_participant.department = self.request.get('department')
        survey_participant.job_type = self.request.get('job_type')
        survey_participant.organization = self.request.get('organization')
        survey_participant.organization_website = self.request.get('organization_website')
        survey_participant.city = self.request.get('city')
        survey_participant.put()
        self.response.out.write(survey_participant.to_json('full_name', 'is_starred', 'is_deleted', 'is_active'))

class SurveyParticipantListHandler(webapp.RequestHandler):
    def get(self):
        survey_participants = SurveyParticipant.get_all()
        survey_participant_list = []
        for survey_participant in survey_participants:
            survey_participant_list.append(survey_participant.to_json_dict('full_name',
                'is_starred', 'is_active', 'is_deleted', 'when_created'))
        response = json.dumps(survey_participant_list)
        self.response.out.write(response)

class ParticipantNewHandler(webapp.RequestHandler):
    def get(self):
        response = render_template('admin/new_participant.html')
        self.response.out.write(response)

    def post(self):
        participant = Participant()
        participant.full_name = self.request.get('full_name')
        participant.email = self.request.get('email')
        participant.mobile_number = self.request.get('mobile_number')
        participant.phone_number = self.request.get('phone_number')
        participant.pricing = Decimal(self.request.get('pricing'))
        participant.designation = self.request.get('designation')
        participant.department = self.request.get('department')
        participant.organization = self.request.get('organization')
        participant.address = self.request.get('address')
        participant.put()

        queue_mail_task(url='/worker/mail/thanks/registration/',
            params=dict(
                full_name=participant.full_name,
                email = participant.email,
                key=str(participant.key())
            ),
            method='POST'
        )
        self.response.out.write(participant.to_json('full_name', 'is_starred', 'is_deleted', 'is_active'))

class ParticipantEditHandler(webapp.RequestHandler):
    def get(self, key):
        participant = db.get(db.Key(key))
        response = render_template('admin/edit_participant.html', participant=participant)
        self.response.out.write(response)

    def post(self, key):
        participant = db.get(db.Key(key))
        participant.full_name = self.request.get('full_name')
        participant.email = self.request.get('email')
        participant.mobile_number = self.request.get('mobile_number')
        participant.phone_number = self.request.get('phone_number')
        participant.pricing = Decimal(self.request.get('pricing'))
        participant.designation = self.request.get('designation')
        participant.department = self.request.get('department')
        participant.organization = self.request.get('organization')
        participant.address = self.request.get('address')
        participant.put()
        self.response.out.write(participant.to_json('full_name', 'is_starred', 'is_deleted', 'is_active'))

class ParticipantListHandler(webapp.RequestHandler):
    def get(self):
        participants = Participant.get_all()
        participant_list = []
        for participant in participants:
            participant_list.append(participant.to_json_dict('full_name',
                'is_starred', 'is_active', 'is_deleted', 'when_created'))
        response = json.dumps(participant_list)
        self.response.out.write(response)


urls = [
    (r'/api/participants/(.*)/delete/?', DeleteHandler),
    (r'/api/participants/(.*)/undelete/?', UndeleteHandler),
    (r'/api/participants/(.*)/approve/?', ApproveHandler),
    (r'/api/participants/(.*)/unapprove/?', UnapproveHandler),
    (r'/api/participants/(.*)/toggle_star/?', ToggleStarHandler),
    (r'/api/participants/list/?', ParticipantListHandler),
    (r'/api/participants/new/?', ParticipantNewHandler),
    (r'/api/participants/(.*)/edit/?', ParticipantEditHandler),

    (r'/api/survey_participants/(.*)/delete/?', DeleteHandler),
    (r'/api/survey_participants/(.*)/undelete/?', UndeleteHandler),
    (r'/api/survey_participants/(.*)/approve/?', ApproveHandler),
    (r'/api/survey_participants/(.*)/unapprove/?', UnapproveHandler),
    (r'/api/survey_participants/(.*)/toggle_star/?', ToggleStarHandler),
    (r'/api/survey_participants/list/?', SurveyParticipantListHandler),
    #(r'/api/survey_participants/new/?', SurveyParticipantNewHandler),
    (r'/api/survey_participants/(.*)/edit/?', SurveyParticipantEditHandler),

    (r'/api/speakers/(.*)/delete/?', DeleteHandler),
    (r'/api/speakers/(.*)/undelete/?', UndeleteHandler),
    (r'/api/speakers/(.*)/approve/?', ApproveHandler),
    (r'/api/speakers/(.*)/unapprove/?', UnapproveHandler),
    (r'/api/speakers/(.*)/toggle_star/?', ToggleStarHandler),
    (r'/api/speakers/list/?', SpeakerListHandler),
    (r'/api/speakers/new/?', SpeakerNewHandler),
    (r'/api/speakers/(.*)/edit/?', SpeakerEditHandler),
]
application = webapp.WSGIApplication(urls, debug=config.DEBUG)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()

