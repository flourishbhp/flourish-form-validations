from edc_form_validators import FormValidator
from .crf_form_validator import FormValidatorMixin


class TbInterviewFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):

        self.validate_other_specify('interview_location')
