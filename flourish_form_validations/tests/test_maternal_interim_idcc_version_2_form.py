from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO
from unittest.case import skip

from ..form_validators import MaternalIterimIdccFormVersion2Validator
from .models import MaternalVisit, Appointment
from .models import SubjectConsent, FlourishConsentVersion
from .test_model_mixin import TestModeMixin


class TestMaternalInterimIdccFormVersion2Validator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(MaternalIterimIdccFormVersion2Validator, *args, **kwargs)

    def setUp(self):

        FlourishConsentVersion.objects.create(
            screening_identifier='ABC12345')

        self.subject_identifier = '11111111'

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier='11111111', screening_identifier='ABC12345',
            gender='M', dob=(get_utcnow() - relativedelta(years=25)).date(),
            consent_datetime=get_utcnow(), version='3')

        self.appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_consent.subject_identifier)

    def test_value_vl_no_value_invalid(self):
        '''Assert raises exception if the last visit is no,
        but other fields are provided.
        '''
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'info_since_lastvisit': YES,
            'any_new_diagnoses': NO,
            'laboratory_information_available': YES,
            'last_visit_result': YES,
            'vl_result_availiable': YES,
            'vl_value_and_date_availiable': YES,
            'cd4_value_and_date_availiable': NO,
            'recent_cd4': '400',
            'vl_detectable': YES,
            'value_vl_size': 'equal',
            'value_vl': 250.2,
            'recent_cd4_date': get_utcnow(),
            'recent_vl_date': None
        }
        form_validator = MaternalIterimIdccFormVersion2Validator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('recent_vl_date', form_validator._errors)

    def test_value_vl_value_valid(self):
        '''Assert raises exception if the last visit is no,
        but other fields are provided.
        '''
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'info_since_lastvisit': YES,
            'laboratory_information_available': NO,
            'any_new_diagnoses': NO,
            'vl_value_and_date_availiable': YES,
            'cd4_value_and_date_availiable': NO,
            'vl_detectable': YES,
            'value_vl_size': 'equal',
            'value_vl': 4444,
            'recent_vl_date': get_utcnow()
        }
        form_validator = MaternalIterimIdccFormVersion2Validator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raises. Got{e}')

    def test_vl_detectable_is_equal(self):
        '''Assert raises exception if vl is 
        detectable but the value_vl_size is not equal
        '''
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'info_since_lastvisit': YES,
            'any_new_diagnoses': NO,
            'laboratory_information_available': NO,
            'vl_value_and_date_availiable': YES,
            'cd4_value_and_date_availiable': NO,
            'vl_detectable': YES,
            'value_vl': 401,
            'recent_vl_date': get_utcnow(),
            'value_vl_size': 'less_than'
        }
        form_validator = MaternalIterimIdccFormVersion2Validator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('value_vl_size', form_validator._errors)

    def test_vl_detectable_vl_value_less(self):
        '''Assert raises exception if vl is 
        detectable but the value_vl is not greater than 400
        '''
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'info_since_lastvisit': YES,
            'any_new_diagnoses': NO,
            'laboratory_information_available': NO,
            'vl_value_and_date_availiable': YES,
            'cd4_value_and_date_availiable': NO,
            'vl_detectable': YES,
            'value_vl': 400,
            'recent_vl_date': get_utcnow(),
            'value_vl_size': 'equal'
        }
        form_validator = MaternalIterimIdccFormVersion2Validator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('value_vl', form_validator._errors)

    def test_not_vl_detectable_vl_value_equal(self):
        '''Assert raises exception if vl is not
        detectable but the value_vl is not equals to 400
        '''
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'info_since_lastvisit': YES,
            'any_new_diagnoses': NO,
            'laboratory_information_available': NO,
            'vl_value_and_date_availiable': YES,
            'cd4_value_and_date_availiable': NO,
            'vl_detectable': NO,
            'value_vl': 403,
            'recent_vl_date': get_utcnow(),
            'value_vl_size': 'less_than'
        }
        form_validator = MaternalIterimIdccFormVersion2Validator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('value_vl', form_validator._errors)

    def test_not_vl_detectable_vl_value_less_than(self):
        '''Assert raises exception if vl is not
        detectable but the value_vl_size is not less_than
        '''
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'info_since_lastvisit': YES,
            'any_new_diagnoses': NO,
            'laboratory_information_available': NO,
            'vl_value_and_date_availiable': YES,
            'cd4_value_and_date_availiable': NO,
            'vl_detectable': NO,
            'value_vl': 400,
            'recent_vl_date': get_utcnow(),
            'value_vl_size': 'equal'
        }
        form_validator = MaternalIterimIdccFormVersion2Validator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('value_vl_size', form_validator._errors)

    def test_value_vl_no_less_than_invalid(self):
        '''Assert raises exception if the vl is detectable but
          value_vl is less than 400.
        '''
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'info_since_lastvisit': YES,
            'any_new_diagnoses': NO,
            'laboratory_information_available': NO,
            'vl_value_and_date_availiable': YES,
            'cd4_value_and_date_availiable': NO,
            'vl_detectable': YES,
            'value_vl': 250.2,
            'recent_vl_date': get_utcnow(),
            'value_vl_size': 'equal',
        }
        form_validator = MaternalIterimIdccFormVersion2Validator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('value_vl', form_validator._errors)
