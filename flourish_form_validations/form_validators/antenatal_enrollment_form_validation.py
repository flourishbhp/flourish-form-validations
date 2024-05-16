from django.core.exceptions import ValidationError
from edc_constants.constants import DWTA, IND, NEG, NO, POS, YES
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class AntenatalEnrollmentFormValidator(FormValidatorMixin,
                                       FormValidator):

    def clean(self):

        super().clean()

        self.subject_identifier = self.cleaned_data.get('subject_identifier')

        self.required_if(
            YES,
            field='knows_lmp',
            field_required='last_period_date'
        )

        self.required_if(
            YES,
            field='rapid_test_done',
            field_required='rapid_test_date'
        )

        self.required_if(
            YES,
            field='rapid_test_done',
            field_required='rapid_test_result'
        )

        self.validate_against_consent_datetime(
            self.cleaned_data.get('report_datetime'),)

        self.validate_current_hiv_status()

    def validate_current_hiv_status(self):
        if (self.cleaned_data.get('week32_test') == NO and
                self.cleaned_data.get('current_hiv_status') in [POS, NEG, IND]):
            message = {'current_hiv_status':
                       'Participant has never tested for HIV. Current HIV '
                       'status is unknown.'}
            self._errors.update(message)
            raise ValidationError(message)
        elif (self.cleaned_data.get('week32_test') == YES and
              self.cleaned_data.get('current_hiv_status') not in
              [POS, NEG, IND, DWTA]):
            message = {'current_hiv_status':
                       'Participant has previously tested for HIV. Current '
                       'HIV status cannot be unknown or never tested.'}
            self._errors.update(message)
            raise ValidationError(message)
