from datetime import timedelta
from edc_base.utils import get_utcnow

from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator
from .crf_form_validator import FormValidatorMixin
from django.apps import apps as django_apps


class InterviewFocusGroupInterestVersion2FormValidator(FormValidatorMixin, FormValidator):
    maternal_delivery_model = 'flourish_caregiver.maternaldelivery'
    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    def onschedule_model_cls(self, onschedule_model):
        return django_apps.get_model(onschedule_model)

    @property
    def maternal_delivery_model_cls(self):
        return django_apps.get_model(self.maternal_delivery_model)

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    def clean(self):

        required_fields = [
            'hiv_group_pref',
            'infant_feeding',
            'school_performance',
            'adult_mental_health',
            'child_mental_health',
            'sexual_health',
            'hiv_topics',
            'food_insecurity',
            'wellness',
            'non_comm_diseases',
            'social_issues',
            'covid19',
            'vaccines',

        ]

        eligible_responses = ['group', 'either', 'one_on_one']

        for field in required_fields:

            self.required_if(
                *eligible_responses,
                field='discussion_pref',
                field_required=field,
            )

        discussion_pref = self.cleaned_data.get('discussion_pref')

        is_preg_and_interested = self.is_preg_enroll() and \
            discussion_pref in eligible_responses

        condition_and_postpartum = (
            is_preg_and_interested
            and self.is_within_first_year_postpartum())

        self.required_if_true(
            is_preg_and_interested,
            field_required='infant_feeding_group_interest',
            required_msg='Infant feeding group interest is required if enrolled'
            ' pregnant(pregnant or postpartum).',)

        self.required_if_true(
            condition_and_postpartum,
            field_required='same_status_comfort',
        )

        self.required_if(
            *eligible_responses,
            field='discussion_pref',
            field_required='diff_status_comfort'
        )

    def get_onschedule_obj(self, subject_identifier, onschedule_model, schedule_name):
        model_cls = self.onschedule_model_cls(onschedule_model)
        try:
            onschedule_obj = model_cls.objects.get(
                subject_identifier=subject_identifier,
                schedule_name=schedule_name)
            return onschedule_obj
        except model_cls.DoesNotExist:
            raise ValidationError('Onschedule does not exist.')

    def get_latest_consent(self, child_subject_identifier):
        consents = self.caregiver_child_consent_cls.objects.filter(
            subject_identifier=child_subject_identifier)
        if consents.exists():
            return consents.latest('consent_datetime')
        else:
            raise ValidationError(
                'Caregiver consent on behalf of child does not exist.')

    def is_preg_enroll(self):
        maternal_visit = self.cleaned_data.get('maternal_visit')
        subject_identifier = maternal_visit.subject_identifier
        onschedule_model = maternal_visit.schedule.onschedule_model
        schedule_name = maternal_visit.appointment.schedule_name

        onschedule_obj = self.get_onschedule_obj(subject_identifier,
                                                 onschedule_model,
                                                 schedule_name)
        child_subject_identifier = onschedule_obj.child_subject_identifier
        consent = self.get_latest_consent(child_subject_identifier)
        return consent.preg_enroll

    def is_within_first_year_postpartum(self):
        """Returns True if subject is currently in first year postpartum."""
        maternal_visit = self.cleaned_data.get('maternal_visit')
        subject_identifier = maternal_visit.subject_identifier
        onschedule_model = maternal_visit.schedule.onschedule_model
        schedule_name = maternal_visit.appointment.schedule_name

        onschedule_obj = self.get_onschedule_obj(
            subject_identifier, onschedule_model, schedule_name)
        child_subject_identifier = onschedule_obj.child_subject_identifier
        consent = self.get_latest_consent(child_subject_identifier)

        today = get_utcnow().date()
        child_dob = consent.child_dob
        if child_dob:
            return (today - child_dob) < timedelta(days=365)
        else:
            return False
