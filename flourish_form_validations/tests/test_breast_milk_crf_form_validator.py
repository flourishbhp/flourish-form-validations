import datetime

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.test import tag, TestCase
from edc_base import get_utcnow
from edc_constants.constants import OTHER

from flourish_form_validations.form_validators import MastitisInlineFormValidator
from flourish_form_validations.tests.models import Appointment, BirthFeedingVaccine, \
    FlourishConsentVersion, \
    MaternalVisit, MestitisActions, OnSchedule, RegisteredSubject, Schedule, \
    SubjectConsent
from flourish_form_validations.tests.test_model_mixin import TestModeMixin


def onschedule_model_cls(self, onschedule_model):
    return OnSchedule or django_apps.get_model(onschedule_model)


@tag('bmcfvt')
class TestBreastMilkCRFFormValidator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(MastitisInlineFormValidator, *args, **kwargs)

    def setUp(self):
        MastitisInlineFormValidator.onschedule_model_cls = onschedule_model_cls
        MastitisInlineFormValidator.birth_feeding_vaccine_model = \
            'flourish_form_validations.birthfeedingvaccine'
        FlourishConsentVersion.objects.create(
            screening_identifier='ABC12345')

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier='11111111',
            screening_identifier='ABC12345',
            gender='M', dob=(get_utcnow() - relativedelta(years=25)).date(),
            consent_datetime=get_utcnow(),
            version='1')

        child_subject_identifier = f'{self.subject_consent.subject_identifier}-1'

        RegisteredSubject.objects.create(
            subject_identifier=child_subject_identifier,
            relative_identifier=self.subject_consent.subject_identifier, )

        self.caregiver_subject_identifier = self.subject_consent.subject_identifier

        on_schedule_model = OnSchedule.objects.create(
            subject_identifier=self.caregiver_subject_identifier,
            child_subject_identifier=child_subject_identifier,
            schedule_name='cohort_a_enrollment', )

        schedule = Schedule.objects.create(
            subject_identifier=self.caregiver_subject_identifier,
            child_subject_identifier=child_subject_identifier,
            schedule_name=on_schedule_model.schedule_name,
            onschedule_model='flourish_form_validations.onschedule'
        )

        child_schedule = Schedule.objects.create(
            subject_identifier=child_subject_identifier,
            schedule_name=on_schedule_model.schedule_name,
            onschedule_model='flourish_form_validations.onschedule'
        )

        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000D',
            visit_instance='0')

        child_appointment = Appointment.objects.create(
            subject_identifier=child_subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000D',
            visit_instance='0')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            schedule=child_schedule,
            schedule_name=on_schedule_model.schedule_name,
        )

        child_visit = MaternalVisit.objects.create(
            appointment=child_appointment,
            subject_identifier=child_subject_identifier,
            schedule=schedule,
            schedule_name=on_schedule_model.schedule_name,
        )

        infant_feeding = BirthFeedingVaccine.objects.create(
            child_visit=child_visit,
            report_datetime=get_utcnow(),
            breastfeed_start_dt=(get_utcnow() + relativedelta(years=25)).date())

        MestitisActions.objects.get_or_create(
            short_name='some_value', name='some value'
        )

        self.dummy_actions = MestitisActions.objects.filter(
            short_name='some_value'
        )

        self.cleaned_data = {
            'mastitis_action': self.dummy_actions,
            'cracked_nipples_action': self.dummy_actions,
        }

    def test_validate_breastfeeding_date(self):
        self.cleaned_data.update(
            maternal_visit=self.maternal_visit,
            mastitis_date_onset=datetime.date(2021, 12, 1)
        )

        validator = MastitisInlineFormValidator(cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, validator.validate)
        self.assertIn('mastitis_date_onset', validator._errors)

    def test_m2m_other_specify_raises_error_for_missing_other_field(self):
        MestitisActions.objects.get_or_create(
            short_name=OTHER, name=OTHER
        )

        other_actions = MestitisActions.objects.filter(
            short_name=OTHER
        )
        self.cleaned_data.update({'mastitis_action': other_actions})
        validator = MastitisInlineFormValidator(cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, validator.validate)
        self.assertIn('mastitis_action_other', validator._errors)


    def test_validate_infection_type_multiple_without_other(self):
        MestitisActions.objects.get_or_create(
            short_name='uninfected_breast', name='uninfected breast'
        )

        uninfected_breast_action = MestitisActions.objects.filter(
            short_name='uninfected_breast'
        )
        self.cleaned_data.update({
            'mastitis_action': uninfected_breast_action,
            'mastitis_type': 'some value'
        })
        validator = MastitisInlineFormValidator(cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, validator.validate)
        self.assertIn('mastitis_action', validator._errors)

    def test_validate_infection_type_both_breasts_and_uninfected(self):
        MestitisActions.objects.get_or_create(
            short_name='both_breasts', name='both breasts'
        )
        MestitisActions.objects.get_or_create(
            short_name='uninfected_breast', name='uninfected breast'
        )

        actions = MestitisActions.objects.filter(
            Q(short_name='both_breasts') | Q(short_name='uninfected_breast')
        )
        self.cleaned_data.update({
            'mastitis_action': actions
        })
        validator = MastitisInlineFormValidator(cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, validator.validate)
        self.assertIn('mastitis_action', validator._errors)
