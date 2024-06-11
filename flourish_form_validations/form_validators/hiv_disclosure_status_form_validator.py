from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import age, get_utcnow
from edc_constants.choices import YES
from edc_constants.constants import NO, OTHER
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class HIVDisclosureStatusFormValidator(FormValidatorMixin, FormValidator):
    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'maternal_visit').subject_identifier
        super().clean()

        not_required_fields = ['plan_to_disclose', 'reason_not_disclosed', ]
        for field in not_required_fields:
            self.not_required_if(YES,
                                 field='disclosed_status',
                                 field_required=field)

        required_fields = ['disclosure_age', 'who_disclosed',
                           'disclosure_difficulty', 'child_reaction']

        for field in required_fields:
            self.required_if(YES,
                             field='disclosed_status',
                             field_required=field)

        other_fields = ['who_disclosed', 'reason_not_disclosed',
                        'child_reaction']

        for field in other_fields:
            other_specify_field = f'{field}_other'
            self.required_if(OTHER, field=field,
                             field_required=other_specify_field)

        self.m2m_required_if(
            NO,
            field='disclosure_intentional',
            m2m_field='unintentional_disclosure_reason'
        )

        self.m2m_other_specify(
            OTHER,
            m2m_field='unintentional_disclosure_reason',
            field_other='unintentional_disclosure_other'
        )

        self.validate_child_age()

    def validate_child_age(self):
        disclosure_age = self.cleaned_data.get('disclosure_age')
        if self.child_ages and disclosure_age:
            if (not any(
                    child_age > disclosure_age for child_age in self.child_ages)):
                raise ValidationError(
                    {'disclosure_age':
                         'Caregiver does not have a child older than age you '
                         f'provided for disclosure age. The oldest child is '
                         f'{max(self.child_ages)} years old.'})

    @property
    def child_ages(self):
        child_ages = []
        if self.child_caregiver_consent_objs:
            for child in self.child_caregiver_consent_objs:
                birth_date = child.child_dob
                years = age(birth_date, get_utcnow()).years + age(
                    birth_date, get_utcnow()).months / 12
                child_ages.append(years)
        return child_ages

    @property
    def child_caregiver_consent_objs(self):
        child_caregiver_consent_model_cls = django_apps.get_model(
            self.caregiver_child_consent_model)
        return child_caregiver_consent_model_cls.objects.filter(
            subject_consent__subject_identifier=self.subject_identifier)
