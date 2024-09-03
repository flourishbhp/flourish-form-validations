from edc_constants.constants import NO, NONE, OTHER, YES
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class CaregiverTBScreeningFormValidator(FormValidatorMixin, FormValidator):

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

        self.m2m_required_if(
            YES,
            m2m_field='tb_tests',
            field='evaluated_for_tb',
        )

        self.m2m_other_specify(
            OTHER,
            m2m_field='tb_tests',
            field_other='other_test',
        )

        self.required_if(
            YES,
            field='evaluated_for_tb',
            field_required='diagnosed_with_TB',
        )

        self.validate_other_specify(
            field='diagnosed_with_TB',
        )

        self.validate_other_specify(
            field='started_on_TB_treatment',
        )

        self.required_if(
            NO,
            field_required='started_on_TB_preventative_therapy',
            field='diagnosed_with_TB',
        )

        self.validate_other_specify(
            field='started_on_TB_preventative_therapy'
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
            self.m2m_other_specify(
                response,
                m2m_field='tb_tests',
                field_other=field,
            )

        self.validate_started_on_tb_treatment()

    def validate_started_on_tb_treatment(self):
        qs = self.cleaned_data.get('tb_tests')
        diagnosed_with_TB = self.cleaned_data.get('diagnosed_with_TB')

        if qs and qs.count() > 0:
            selected = {obj.short_name: obj.name for obj in qs}

            self.required_if_true(
                NONE in selected or diagnosed_with_TB == YES,
                field_required='started_on_TB_treatment',
            )
