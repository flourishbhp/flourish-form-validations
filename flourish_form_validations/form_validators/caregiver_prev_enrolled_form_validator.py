from django.apps import apps as django_apps
from django.core.exceptions import ValidationError

from edc_constants.constants import YES, NO
from edc_form_validators.form_validator import FormValidator


class CaregiverPrevEnrolledFormValidator(FormValidator):

    maternal_dataset_model = 'flourish_caregiver.maternaldataset'

    subject_consent_model = 'flourish_caregiver.subjectconsent'

    bhp_prior_screening_model = 'flourish_caregiver.screeningpriorbhpparticipants'

    @property
    def maternal_dataset_model_cls(self):
        return django_apps.get_model(self.maternal_dataset_model)

    @property
    def subject_consent_model_cls(self):
        return django_apps.get_model(self.subject_consent_model)

    @property
    def bhp_prior_screening_model_cls(self):
        return django_apps.get_model(self.bhp_prior_screening_model)

    def clean(self):

        if (self.cleaned_data.get('maternal_prev_enroll') == YES and
                self.bhp_prior_screening_obj.flourish_participation ==
                'another_caregiver_interested'):
            message = {'maternal_prev_enroll':
                       'Participant is not from any bhp prior studies'}
            self._errors.update(message)
            raise ValidationError(message)
        elif (self.cleaned_data.get('maternal_prev_enroll') == NO and
              self.bhp_prior_screening_obj.flourish_participation ==
              'interested'):
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
                self.bhp_prior_screening_obj.flourish_participation ==
                'interested'):
            if self.maternal_dataset_obj.mom_hivstatus == 'HIV-uninfected':
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

                self.required_if(
                    YES,
                    field='last_test_date',
                    field_required='is_date_estimated')
            elif self.maternal_dataset_obj.mom_hivstatus == 'HIV-infected':
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

    @property
    def bhp_prior_screening_obj(self):
        try:
            bhp_prior_screening = self.bhp_prior_screening_model_cls.objects.get(
                screening_identifier=
                self.subject_consent_obj.screening_identifier)
        except self.bhp_prior_screening_model_cls.DoesNotExist:
            return None
        else:
            return bhp_prior_screening

    @property
    def maternal_dataset_obj(self):
        try:
            maternal_dataset = self.maternal_dataset_model_cls.objects.get(
                screening_identifier=
                self.subject_consent_obj.screening_identifier)
        except self.maternal_dataset_model_cls.DoesNotExist:
            return None
        else:
            return maternal_dataset

    @property
    def subject_consent_obj(self):
        try:
            subject_consent = self.subject_consent_model_cls.objects.get(
                subject_identifier=self.cleaned_data.get(
                    'subject_identifier'))
        except self.subject_consent_model_cls.DoesNotExist:
            return None
        else:
            return subject_consent
