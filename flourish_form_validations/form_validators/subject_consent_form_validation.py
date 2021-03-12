import re
from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import relativedelta
from edc_constants.constants import FEMALE, MALE
from edc_form_validators import FormValidator


class SubjectConsentFormValidator(FormValidator):

    prior_screening_model = 'flourish_caregiver.screeningpriorbhpparticipants'

    subject_consent_model = 'flourish_caregiver.subjectconsent'

    maternal_dataset_model = 'flourish_caregiver.maternaldataset'

    @property
    def bhp_prior_screening_cls(self):
        return django_apps.get_model(self.prior_screening_model)

    @property
    def subject_consent_cls(self):
        return django_apps.get_model(self.subject_consent_model)

    @property
    def maternal_dataset_cls(self):
        return django_apps.get_model(self.maternal_dataset_model)

    def clean(self):
        cleaned_data = self.cleaned_data
        self.subject_identifier = cleaned_data.get('subject_identifier')
        super().clean()

#         try:
#             subject_screening = self.subject_screening_cls.objects.get(
#                 screening_identifier=cleaned_data.get('screening_identifier'))
#         except self.subject_screening_cls.DoesNotExist:
#             raise ValidationError(
#                 'Complete the "Subject Screening" form before proceeding.')

#         if cleaned_data.get('citizen') != subject_screening.has_omang:
#             message = {'citizen':
#                        'During screening you said has_omang is {}. '
#                        'Yet you wrote citizen is {}. Please correct.'.format(
#                            subject_screening.has_omang, cleaned_data.get('citizen'))}
#             self._errors.update(message)
#             raise ValidationError(message)

        self.clean_full_name_syntax()
        self.clean_initials_with_full_name()
#         self.validate_dob(cleaned_data=self.cleaned_data,
#                           model_obj=subject_screening)
        self.validate_child_dob(cleaned_data=self.cleaned_data)
        self.validate_identity_number(cleaned_data=self.cleaned_data)
        self.validate_recruit_source()
        self.validate_recruitment_clinic()
        self.validate_reconsent()

    def validate_reconsent(self):
        try:
            consent_obj = self.subject_consent_cls.objects.get(
                subject_identifier=self.cleaned_data.get('subject_identifier'))
        except self.subject_consent_cls.DoesNotExist:
            pass
        else:
            consent_dict = consent_obj.__dict__
            consent_fields = [
                'first_name', 'last_name', 'dob', 'recruit_source',
                'recruit_source_other', 'recruitment_clinic',
                'recruitment_clinic_other', 'is_literate', 'identity',
                'identity_type']
            for field in consent_fields:
                if self.cleaned_data.get(field) != consent_dict[field]:
                    message = {field:
                               f'{field} was previously reported as, '
                               f'{consent_dict[field]}, please correct.'}
                    self._errors.update(message)
                    raise ValidationError(message)

    def clean_full_name_syntax(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        if not re.match(r'^[A-Z]+$|^([A-Z]+[ ][A-Z]+)$', first_name):
            message = {'first_name': 'Ensure first name is letters (A-Z) in '
                       'upper case, no special characters, except spaces.'}
            self._errors.update(message)
            raise ValidationError(message)

        if not re.match(r'^[A-Z-]+$', last_name):
            message = {'last_name': 'Ensure last name is letters (A-Z) in '
                       'upper case, no special characters, except hyphens.'}
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

    def clean_initials_with_full_name(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        initials = cleaned_data.get("initials")
        try:
            middle_name = None
            is_first_name = False
            new_first_name = None
            if len(first_name.split(' ')) > 1:
                new_first_name = first_name.split(' ')[0]
                middle_name = first_name.split(' ')[1]

            if (middle_name and
                (initials[:1] != new_first_name[:1] or
                 initials[1:2] != middle_name[:1])):
                is_first_name = True

            elif not middle_name and initials[:1] != first_name[:1]:
                is_first_name = True

            if is_first_name or initials[-1:] != last_name[:1]:
                raise forms.ValidationError(
                    {'initials': 'Initials do not match full name.'},
                    params={
                        'initials': initials,
                        'first_name': first_name,
                        'last_name': last_name},
                    code='invalid')
        except (IndexError, TypeError):
            raise forms.ValidationError('Initials do not match fullname.')

    def validate_identity_number(self, cleaned_data=None):
        if cleaned_data.get('identity') != cleaned_data.get('confirm_identity'):
            msg = {'identity':
                   '\'Identity\' must match \'confirm identity\'.'}
            self._errors.update(msg)
            raise ValidationError(msg)
        if cleaned_data.get('identity_type') == 'country_id':
            if len(cleaned_data.get('identity')) != 9:
                msg = {'identity':
                       'Country identity provided should contain 9 values. '
                       'Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            gender = cleaned_data.get('gender')
            if gender == FEMALE and cleaned_data.get('identity')[4] != '2':
                msg = {'identity':
                       'Participant gender is Female. Please correct identity number.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            elif gender == MALE and cleaned_data.get('identity')[4] != '1':
                msg = {'identity':
                       'Participant is Male. Please correct identity number.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_dob(self, cleaned_data=None, model_obj=None):

        consent_datetime = cleaned_data.get('consent_datetime')
        consent_age = relativedelta(
            consent_datetime.date(), cleaned_data.get('dob')).years
        age_in_years = None

        try:
            consent_obj = self.subject_consent_cls.objects.get(
                screening_identifier=self.cleaned_data.get('screening_identifier'),)
        except self.subject_consent_cls.DoesNotExist:
            age_in_years = model_obj.age_in_years
            if consent_age != age_in_years:
                message = {'dob':
                           'In Subject Screening you indicated the '
                           'participant is {age_in_years}, but age derived '
                           f'from the DOB is {consent_age}.'}
                self._errors.update(message)
                raise ValidationError(message)
        else:
            age_in_years = relativedelta(
                consent_datetime.date(), consent_obj.dob).years
            if consent_age != age_in_years:
                message = {'dob':
                           'In previous consent the derived age of the '
                           f'participant is {age_in_years}, but age derived '
                           f'from the DOB is {consent_age}.'}
                self._errors.update(message)
                raise ValidationError(message)

    def validate_child_dob(self, cleaned_data=None):
        child_dob = cleaned_data.get('child_dob')
        screening_identifier = cleaned_data.get('screening_identifier')
        if child_dob:
            try:
                maternal_dataset = self.maternal_dataset_cls.objects.get(
                    screening_identifier=screening_identifier)
            except self.maternal_dataset_cls.DoesNotExist:
                pass
            else:
                if child_dob != maternal_dataset.delivdt:
                    msg = {'child_dob':
                           'Child date of birth does not match with dob '
                           f'({maternal_dataset.delivdt}) from the dataset.'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def validate_recruit_source(self):
        self.validate_other_specify(
            field='recruit_source',
            other_specify_field='recruit_source_other',
            required_msg=('You indicated that mother first learnt about the '
                          'study from a source other than those in the list '
                          'provided. Please specify source.'),
        )

    def validate_recruitment_clinic(self):
        clinic = self.cleaned_data.get('recruitment_clinic')
        self.validate_other_specify(
            field='recruitment_clinic',
            other_specify_field='recruitment_clinic_other',
            required_msg=('You MUST specify other facility that mother was '
                          f'recruited from as you already indicated {clinic}')
        )
