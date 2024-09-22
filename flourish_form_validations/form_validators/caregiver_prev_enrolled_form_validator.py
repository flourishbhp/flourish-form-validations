from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import IND, NEG, NO, POS, UNK, YES
from edc_form_validators.form_validator import FormValidator


class CaregiverPrevEnrolledFormValidator(FormValidator):
    maternal_dataset_model = 'flourish_caregiver.maternaldataset'

    subject_consent_model = 'flourish_caregiver.subjectconsent'

    bhp_prior_screening_model = 'flourish_caregiver.screeningpriorbhpparticipants'

    child_assent_model = 'flourish_child.childassent'

    @property
    def maternal_dataset_model_cls(self):
        return django_apps.get_model(self.maternal_dataset_model)

    @property
    def child_assent_cls(self):
        return django_apps.get_model(self.child_assent_model)

    @property
    def subject_consent_model_cls(self):
        return django_apps.get_model(self.subject_consent_model)

    @property
    def bhp_prior_screening_model_cls(self):
        return django_apps.get_model(self.bhp_prior_screening_model)

    def clean(self):

        self.subject_identifier = self.cleaned_data.get('subject_identifier')

        self.check_child_assent(self.subject_identifier)

        if (self.cleaned_data.get('maternal_prev_enroll') == YES and
                self.flourish_participation_interest('another_caregiver_interested')):
            message = {'maternal_prev_enroll':
                       'Participant is not from any bhp prior studies'}
            self._errors.update(message)
            raise ValidationError(message)
        elif (self.cleaned_data.get('maternal_prev_enroll') == NO and
              self.flourish_participation_interest('interested')):
            message = {'maternal_prev_enroll':
                       'Participant is from a prior bhp study'}
            self._errors.update(message)
            raise ValidationError(message)

        self.validate_caregiver_previously_enrolled(
            cleaned_data=self.cleaned_data)

        fields_required = ['sex', 'relation_to_child', ]
        for field_required in fields_required:
            self.required_if(
                NO,
                field='maternal_prev_enroll',
                field_required=field_required)

        self.validate_other_specify(field='relation_to_child')

    def validate_caregiver_previously_enrolled(self, cleaned_data=None):
        maternal_prev_enroll = cleaned_data.get('maternal_prev_enroll')

        if (maternal_prev_enroll == YES and
                self.flourish_participation_interest('interested')):

            if self.maternal_dataset_hiv_status == NEG:
                fields_required = ['current_hiv_status', 'last_test_date', ]
                for field_required in fields_required:
                    self.required_if(
                        YES,
                        field='maternal_prev_enroll',
                        field_required=field_required)

                self.required_if(
                    YES,
                    field='last_test_date',
                    field_required='test_date')

                test_date = self.cleaned_data.get('test_date', None)
                if test_date and cleaned_data.get('current_hiv_status') in [NEG, IND]:
                    difference = self.cleaned_data.get(
                        'report_datetime').date() - relativedelta(months=3)
                    if test_date < difference:
                        msg = {'test_date':
                               'HIV test date should not be older than 3 months'}
                        self._errors.update(msg)
                        raise ValidationError(msg)

                self.required_if(
                    YES,
                    field='last_test_date',
                    field_required='is_date_estimated')

            elif self.maternal_dataset_hiv_status == POS:
                not_required_fields = ['current_hiv_status', 'last_test_date',
                                       'test_date', 'is_date_estimated', 'sex',
                                       'relation_to_child',
                                       'relation_to_child_other']

                for field in not_required_fields:
                    self.not_required_if(
                        YES, field='maternal_prev_enroll', field_required=field)

        fields_not_required = ['current_hiv_status', 'last_test_date',
                               'test_date', 'is_date_estimated', ]
        for field in fields_not_required:
            self.not_required_if(
                NO,
                field='maternal_prev_enroll',
                field_required=field,
                inverse=False)

    def flourish_participation_interest(self, flourish_participation):

        bhp_prior_screenings = self.bhp_prior_screening_model_cls.objects.filter(
            subject_identifier=self.subject_consent_obj.subject_identifier)

        if bhp_prior_screenings:
            return flourish_participation in bhp_prior_screenings.values_list(
                'flourish_participation', flat=True)

        return False

    @property
    def maternal_dataset_hiv_status(self):

        maternal_dataset_objs = self.maternal_dataset_model_cls.objects.filter(
            subject_identifier=self.subject_consent_obj.subject_identifier)

        if maternal_dataset_objs:
            mom_hiv_statuses = maternal_dataset_objs.values_list('mom_hivstatus',
                                                                 flat=True)

            if 'HIV-infected' in mom_hiv_statuses:
                return POS
            else:
                return NEG
        return UNK

    @property
    def subject_consent_obj(self):
        try:
            subject_consent = self.subject_consent_model_cls.objects.filter(
                subject_identifier=self.cleaned_data.get(
                    'subject_identifier')).latest(
                'consent_datetime')
        except self.subject_consent_model_cls.DoesNotExist:
            return None
        else:
            return subject_consent

    def check_child_assent(self, subject_identifier):

        child_assents_exists = []

        child_consents = self.subject_consent_model_cls.objects.filter(
            subject_identifier=subject_identifier).latest(
            'consent_datetime').caregiverchildconsent_set \
            .only('child_age_at_enrollment', 'is_eligible') \
            .filter(is_eligible=True,
                    child_age_at_enrollment__gte=7,
                    child_age_at_enrollment__lt=18)

        if child_consents.exists():

            for child_consent in child_consents:
                exists = self.child_assent_cls.objects.filter(
                    subject_identifier=child_consent.subject_identifier).exists()
                child_assents_exists.append(exists)

            child_assents_exists = all(child_assents_exists)

            if not child_assents_exists:
                raise ValidationError('Please fill the child assent(s) form(s) first')
