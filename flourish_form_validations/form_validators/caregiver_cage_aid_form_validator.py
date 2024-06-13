from .cage_aid_form_validator_mixin import CageAidFormValidatorMixin

from .crf_form_validator import FormValidatorMixin


class CaregiverCageAidFormValidator(CageAidFormValidatorMixin, FormValidatorMixin):

    def clean(self):
        super().clean()
