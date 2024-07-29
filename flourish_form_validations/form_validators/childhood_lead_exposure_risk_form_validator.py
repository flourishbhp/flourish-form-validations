from edc_constants.constants import YES
from edc_form_validators import FormValidator

from flourish_child_validations.form_validators.form_validator_mixin import ChildFormValidatorMixin


class ChildhoodLeadExposureRiskFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.validate_other_specify(
            field='home_run_business',
        )

        self.required_if(
            YES,
            field='house_by_busy_road',
            field_required='years_near_busy_road',
        )

        self.required_if(
            YES,
            field_required='home_run_business',
            field='home_business'
        )
