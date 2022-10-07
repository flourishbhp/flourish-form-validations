from edc_constants.constants import NO
from edc_form_validators import FormValidator
from .crf_form_validator import FormValidatorMixin


class TbEngagementFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):

        self.required_if(
            NO,
            field='interview_consent',
            field_required='interview_decline_reason')

        self.validate_other_specify(
            field='interview_decline_reason',
            other_specify_field='interview_decline_reason_other')
