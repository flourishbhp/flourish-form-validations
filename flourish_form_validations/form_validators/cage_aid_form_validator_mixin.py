from edc_constants.constants import YES
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class CageAidFormValidatorMixin(FormValidatorMixin, FormValidator):

    def clean(self):
        fields = ['cut_down',
                  'people_reaction',
                  'guilt',
                  'eye_opener',]

        for field in fields:
            self.required_if(
                YES,
                field='alcohol_drugs',
                field_required=field
            )
        super().clean()
