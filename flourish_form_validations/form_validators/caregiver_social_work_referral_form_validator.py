from django.core.exceptions import ValidationError

from .crf_form_validator import FormValidatorMixin
from .social_work_referral_validator_mixin import SocialWorkReferralValidatorMixin


class CaregiverSocialWorkReferralFormValidator(
        FormValidatorMixin, SocialWorkReferralValidatorMixin):

    def clean(self):
        super().clean()
        self.validate_hiv_status()

    def validate_hiv_status(self):
        hiv_status = self.caregiver_hiv_status(
            self.subject_identifier)
        current_hiv_status = self.cleaned_data.get(
            'current_hiv_status', None)
        if current_hiv_status and current_hiv_status != hiv_status:
            raise ValidationError({
                'current_hiv_status':
                f'Participant is {hiv_status}, please correct for current HIV status'})
