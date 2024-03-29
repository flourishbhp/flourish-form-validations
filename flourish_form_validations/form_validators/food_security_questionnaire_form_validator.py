from edc_constants.constants import YES
from edc_form_validators import FormValidator
from .crf_form_validator import FormValidatorMixin


class FoodSecurityQuestionnaireFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.subject_identifier = self.cleaned_data.get(
            'maternal_visit').subject_identifier

        self.required_if(
            YES,
            field='cut_meals',
            field_required='how_often')
