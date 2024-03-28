from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class CaregiverContactFormValidator(FormValidatorMixin, FormValidator):
    caregiver_locator_model = 'flourish_caregiver.caregiverlocator'

    @property
    def caregiver_locator_cls(self):
        return django_apps.get_model(self.caregiver_locator_model)

    def clean(self):
        cleaned_data = self.cleaned_data
        self.subject_identifier = self.cleaned_data.get('subject_identifier')

        self.validate_against_consent_datetime(self.cleaned_data.get('report_datetime'))

        self.required_if(
            YES,
            field='call_rescheduled',
            field_required='reason_rescheduled',
        )

        locator = self.caregiver_locator
        if locator:
            if (cleaned_data.get('contact_type') == 'in_person'
                    and locator.may_visit_home == NO):
                msg = {'contact_type':
                           'Caregiver Locator says may visit home: '
                           f'{locator.may_visit_home}, you cannot make a home visit'
                           ' to participant if they did not give permission.'}
                self._errors.update(msg)
                raise ValidationError(msg)
            if (cleaned_data.get('contact_type') == 'phone_call'
                    and locator.may_call == NO):
                msg = {'contact_type':
                           f'Caregiver Locator says may call: {locator.may_call}, '
                           'you cannot call participant if they did not give permission.'}
                self._errors.update(msg)
                raise ValidationError(msg)
        else:
            msg = {'__all__':
                       'Caregiver Locator not found, please add Locator before proceeding.'}
            self._errors.update(msg)
            raise ValidationError(msg)

        self.validate_other_specify(field='call_reason')

        self.required_if(
            YES,
            field='contact_success',
            field_required='contact_comment',
            inverse=False)

        self.validate_other_specify(
            field='reason_rescheduled',
            other_specify_field='reason_rescheduled_other',
        )

    @property
    def caregiver_locator(self):
        cleaned_data = self.cleaned_data
        try:
            return self.caregiver_locator_cls.objects.get(
                subject_identifier=cleaned_data.get('subject_identifier'))
        except self.caregiver_locator_cls.DoesNotExist:
            return None
