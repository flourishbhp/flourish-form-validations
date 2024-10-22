import datetime
import re
import pytz

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import age
from edc_constants.choices import FEMALE, MALE, NO, NOT_APPLICABLE, YES
from edc_form_validators import FormValidator
from edc_form_validators.base_form_validator import NOT_APPLICABLE_ERROR


class CaregiverChildConsentFormValidator(FormValidator):
    child_dataset_model = 'flourish_child.childdataset'

    preg_women_screening_model = 'flourish_caregiver.screeningpregwomen'

    delivery_model = 'flourish_caregiver.maternaldelivery'

    @property
    def child_dataset_cls(self):
        return django_apps.get_model(self.child_dataset_model)

    @property
    def preg_screening_cls(self):
        return django_apps.get_model(self.preg_women_screening_model)

    @property
    def delivery_model_cls(self):
        return django_apps.get_model(self.delivery_model)

    def clean(self):

        self.subject_identifier = self.cleaned_data.get('subject_identifier')
        super().clean()

        not_preg_required_fields = ['first_name', 'last_name']

        for field in not_preg_required_fields:
            self.required_if_true(
                self.cleaned_data.get('study_child_identifier') is not None,
                field_required=field,
                inverse=False)

        self.validate_previously_enrolled(cleaned_data=self.cleaned_data)
        self.clean_full_name_syntax()
        self.preg_not_required()
        self.validate_child_knows_status(cleaned_data=self.cleaned_data)
        self.validate_child_preg_test(cleaned_data=self.cleaned_data)
        self.validate_child_years_more_tha_12yrs_at_jun_2025(
            cleaned_data=self.cleaned_data)
        self.validate_identity_number(cleaned_data=self.cleaned_data)
        self.validate_child_dob_match_del()

    def preg_not_required(self):

        not_preg_fields = ['child_preg_test', 'child_knows_status']

        for field in not_preg_fields:

            if (not self.cleaned_data.get('study_child_identifier')
                    and self.cleaned_data.get(field) != NOT_APPLICABLE):
                message = {field: 'This field is not applicable'}
                self._errors.update(message)
                self._error_codes.append(NOT_APPLICABLE_ERROR)
                raise ValidationError(message, code=NOT_APPLICABLE_ERROR)

    def validate_previously_enrolled(self, cleaned_data):
        if cleaned_data.get('study_child_identifier'):
            gender_dict = {FEMALE: 'Female',
                           MALE: 'Male'}
            gender = gender_dict.get(cleaned_data.get('gender'))
            date_str = cleaned_data.get('child_dob')
            date_obj = None
            if date_str:
                year, month, day = map(int, date_str.split('-'))
                date_obj = datetime.date(year, month, day)

            if gender and cleaned_data.get('child_dob'):
                try:
                    self.child_dataset_cls.objects.get(
                        study_child_identifier=cleaned_data.get('study_child_identifier'),
                        infant_sex=gender,
                        dob=date_obj)
                except self.child_dataset_cls.DoesNotExist:
                    message = {
                        'study_child_identifier': 'No child dataset exists for the '
                                                  'specified child identifier, '
                                                  'gender and dob.'}
                    self._errors.update(message)
                    raise ValidationError(message)
            else:
                try:
                    self.child_dataset_cls.objects.get(
                        study_child_identifier=cleaned_data.get('study_child_identifier'))
                except self.child_dataset_cls.DoesNotExist:
                    message = {
                        'study_child_identifier': 'No child dataset exists for the '
                                                  'specified child identifier'}
                    self._errors.update(message)
                    raise ValidationError(message)

    def clean_full_name_syntax(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        if first_name:
            if not re.match(r'^[A-Z]+$|^([A-Z]+[ ][A-Z]+)$', first_name):
                message = {'first_name': 'Ensure first name is letters (A-Z) in '
                                         'upper case, no special characters, '
                                         'except spaces. Maximum 2 first '
                                         'names allowed.'}
                self._errors.update(message)
                raise ValidationError(message)

        if last_name:
            if not re.match(r'^[A-Z-]+$', last_name):
                message = {'last_name': 'Ensure last name is letters (A-Z) in '
                                        'upper case, no special characters, '
                                        'except hyphens.'}
                self._errors.update(message)
                raise ValidationError(message)

            if first_name and last_name:
                if first_name != first_name.upper():
                    message = {'first_name': 'First name must be in CAPS.'}
                    self._errors.update(message)
                    raise ValidationError(message)
                elif last_name != last_name.upper():
                    message = {'last_name': 'Last name must be in CAPS.'}
                    self._errors.update(message)
                    raise ValidationError(message)

    def validate_identity_number(self, cleaned_data=None):
        identity = cleaned_data.get('identity')
        required_fields = ['identity_type', 'confirm_identity', ]
        for required in required_fields:
            self.required_if_true(
                identity is not None and identity != '',
                field_required=required)
        if identity:
            if not re.match('[0-9]+$', identity):
                message = {'identity': 'Identity number must be digits.'}
                self._errors.update(message)
                raise ValidationError(message)
            if cleaned_data.get('identity') != cleaned_data.get(
                    'confirm_identity'):
                msg = {'identity':
                       '\'Identity\' must match \'confirm identity\'.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            if cleaned_data.get('identity_type') in ['country_id',
                                                     'birth_cert']:
                if len(cleaned_data.get('identity')) != 9:
                    msg = {'identity':
                           'Country identity provided should contain 9 values. '
                           'Please correct.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)
                gender = cleaned_data.get('gender')
                if gender == FEMALE and cleaned_data.get('identity')[4] != '2':
                    msg = {'identity':
                           'Participant gender is Female. Please correct '
                           'identity number.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)
                elif gender == MALE and cleaned_data.get('identity')[4] != '1':
                    msg = {'identity':
                           'Participant is Male. Please correct identity number.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_child_preg_test(self, cleaned_data=None):
        if (cleaned_data.get('gender') and cleaned_data.get('gender') == 'M'
                and cleaned_data.get('child_preg_test') in [YES, NO]):
            msg = {'child_preg_test':
                   'Can only be answered as Not applicable since child is Male'}
            self._errors.update(msg)
            raise ValidationError(msg)

    def validate_child_knows_status(self, cleaned_data):

        child_dob = cleaned_data.get('child_dob')
        consent_date = cleaned_data.get('consent_datetime')

        # consent date should be used instead of the time right now
        if child_dob and consent_date:
            child_dob = datetime.datetime.strptime(child_dob, "%Y-%m-%d")
            child_age = 0
            if child_dob.date() < consent_date.date():
                child_age = age(child_dob, consent_date).years

            if child_age < 16 and cleaned_data.get(
                    'child_knows_status') in [YES, NO]:
                msg = {'child_knows_status': 'Child is less than 16 years'}
                self._errors.update(msg)
                raise ValidationError(msg)
            elif child_age >= 16 and cleaned_data.get(
                    'child_knows_status') == NOT_APPLICABLE:
                msg = {'child_knows_status': 'This field is applicable'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_child_years_more_tha_12yrs_at_jun_2025(self, cleaned_data):

        child_dob = cleaned_data.get('child_dob')
        if child_dob:
            date_jun_2025 = datetime.datetime.strptime("2025-01-30",
                                                       "%Y-%m-%d").date()
            child_dob = datetime.datetime.strptime(child_dob, "%Y-%m-%d").date()
            child_age_at_2025 = age(child_dob, date_jun_2025).years
            if cleaned_data.get('gender') == 'F':
                if (child_age_at_2025 < 12
                        and cleaned_data.get('child_preg_test') != NOT_APPLICABLE):
                    msg = {'child_preg_test':
                           'Child will not be 12 years old by 2025, This field is '
                           'not applicable'}
                    self._errors.update(msg)
                    raise ValidationError(msg)
                elif (child_age_at_2025 >= 12
                      and cleaned_data.get('child_preg_test') == NOT_APPLICABLE):
                    msg = {'child_preg_test':
                           'Child is Female. This field is applicable'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_child_dob_match_del(self):
        """ For ANC participants validate that the delivery date matches
            child DOB on the child consent form.
        """
        child_dob = self.cleaned_data.get('child_dob', None)
        try:
            delivery_obj = self.delivery_model_cls.objects.get(
                child_subject_identifier=self.subject_identifier)
        except self.delivery_model_cls.DoesNotExist:
            pass
        else:
            delivery_dt = delivery_obj.delivery_datetime
            local_tz = pytz.timezone('Africa/Gaborone')
            local_delivery_dt = delivery_dt.astimezone(local_tz)

            if child_dob != local_delivery_dt.date().strftime('%Y-%m-%d'):
                msg = {'child_dob':
                       'Infant DOB must match maternal delivery date. Expected'
                       f' {local_delivery_dt.date()} got {child_dob}'}
                self._errors.update(msg)
                raise ValidationError(msg)
