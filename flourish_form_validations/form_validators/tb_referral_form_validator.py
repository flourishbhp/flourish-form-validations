from edc_form_validators import FormValidator
from .crf_form_validator import FormValidatorMixin


class TbReferralFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):
        self.validate_referral_clinic_other_specify()

    def validate_referral_clinic_other_specify(self):
        self.validate_other_specify(
            field='referral_clinic',
            other_specify_field='referral_clinic_other'
        )
