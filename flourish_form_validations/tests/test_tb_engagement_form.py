from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, YES, OTHER

from ..form_validators import TbEngagementFormValidator
from .models import SubjectConsent, FlourishConsentVersion
from .test_model_mixin import TestModeMixin


class TestTbEngagementForm(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(TbEngagementFormValidator, *args, **kwargs)

    def setUp(self):

        FlourishConsentVersion.objects.create(
            screening_identifier='ABC12345')

        self.subject_identifier = '11111111'

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier='11111111', screening_identifier='ABC12345',
            gender='M', dob=(get_utcnow() - relativedelta(years=25)).date(),
            consent_datetime=get_utcnow(), version='1')

    def interview_consent_valid(self):
        """
        Raise an error if cough duration is captured when the subject did not answer yes
        to have a cough question
        """

        cleaned_data = {
            'interview_consent': YES,
            'interview_decline_reason': None,
        }

        form_validator = TbEngagementFormValidator(
            cleaned_data=cleaned_data)

        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def interview_consent_valid2(self):
        """
        Raise an error if cough duration is captured when the subject did not answer yes
        to have a cough question
        """

        cleaned_data = {
            'interview_consent': NO,
            'interview_decline_reason': 'blah blah',
        }

        form_validator = TbEngagementFormValidator(
            cleaned_data=cleaned_data)

        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def interview_consent_invalid(self):
        """
        Raise an error if cough duration is captured when the subject did not answer yes
        to have a cough question
        """

        cleaned_data = {
            'interview_consent': YES,
            'interview_decline_reason': 'blah blah',
        }

        form_validator = TbEngagementFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('recent_cd4', form_validator._errors)

    def interview_consent_invalid2(self):
        """
        Raise an error if cough duration is captured when the subject did not answer yes
        to have a cough question
        """

        cleaned_data = {
            'interview_consent': NO,
            'interview_decline_reason': None,
        }

        form_validator = TbEngagementFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('recent_cd4', form_validator._errors)

    def interview_decline_reason_other_invalid2(self):
        """
        Raise an error if cough duration is captured when the subject did not answer yes
        to have a cough question
        """

        cleaned_data = {
            'interview_decline_reason': OTHER,
            'interview_decline_reason_other': None,
        }

        form_validator = TbEngagementFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('interview_decline_reason_other', form_validator._errors)
