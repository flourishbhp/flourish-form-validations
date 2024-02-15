from django.core.exceptions import ValidationError
from edc_constants.constants import YES
from edc_form_validators import FormValidator

from flourish_child_validations.form_validators import ChildFormValidatorMixin


class CaregiverTBScreeningFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        required_fields = ['cough', 'fever', 'sweats', 'weight_loss']

        for field in required_fields:
            self.required_if(YES,
                             field=field,
                             field_required=f'{field}_duration')

        self.required_if(YES,
                         field='evaluated_for_tb',
                         field_required='clinic_visit_date')

        self.m2m_other_specify(
            m2m_field='tb_tests',
            field_other='other_test',
        )

        self.required_if(YES,
                         field='diagnosed_with_TB',
                         field_required='started_on_TB_treatment')

        field_responses = {
            'chest_xray': 'chest_xray_results',
            'sputum_sample': 'sputum_sample_results',
            'urine_test': 'urine_test_results',
            'skin_test': 'skin_test_results',
            'blood_test': 'blood_test_results',
        }

        for response, field in field_responses.items():
            self.required_if_m2m(
                response,
                m2m_field='tb_tests',
                field=field,
            )

    def required_if_m2m(self, response, field=None, m2m_field=None):
        m2m_field = self.cleaned_data.get(m2m_field)
        selected = {obj.short_name: obj.name for obj in m2m_field if
                    m2m_field is not None}
        if response:
            if response not in selected and not self.cleaned_data.get(field):
                message = {field: 'This field is applicable'}
                self._errors.update(message)
                raise ValidationError(message)
