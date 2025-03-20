from edc_constants.constants import NO, NONE, OTHER, YES,POS,NEG
from edc_form_validators import FormValidator
from django.core.exceptions import ValidationError
from .crf_form_validator import FormValidatorMixin


class CaregiverTBScreeningFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.validate_results_tb_treatment_and_prevention()

        required_fields = ['cough', 'fever', 'sweats', 'weight_loss']

        for field in required_fields:
            self.required_if(YES,
                             field=field,
                             field_required=f'{field}_duration')

        self.required_if(YES,
                         field='evaluated_for_tb',
                         field_required='flourish_referral')
        self.not_flourish_referral_validation()

        self.m2m_single_selection_if(
            'None', m2m_field='tb_tests'
        )

        self.m2m_other_specify(
            OTHER,
            m2m_field='tb_tests',
            field_other='other_test',
        )

        self.diagnoses_required_validation()

        self.validate_other_specify(
            field='diagnosed_with_TB',
        )

        self.required_if(
            YES,
            field_required='started_on_TB_treatment',
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

        self.field_cannot_be(field_1='diagnosed_with_TB',
                             field_2='started_on_TB_preventative_therapy',
                             field_one_condition=YES,
                             field_two_condition=YES)

        self.validate_other_specify(
            field='started_on_TB_preventative_therapy'
        )

        self.required_if(YES,
                         field='diagnosed_with_TB',
                         field_required='started_on_TB_treatment')

        field_responses = {
            'chest_xray': 'chest_xray_results',
            'sputum_sample': 'sputum_sample_results',
            'stool_sample': 'stool_sample_results',
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

    def field_cannot_be(self, field_1, field_2, field_one_condition,
                        field_two_condition):
        """Raises an exception based on the condition between field_1 and field_2
        values."""
        cleaned_data = self.cleaned_data
        field_1_value = cleaned_data.get(field_1)
        field_2_value = cleaned_data.get(field_2)

        if field_1_value == field_one_condition and field_2_value == field_two_condition:
            message = {field_2: (f'cannot be {field_two_condition} when '
                                 f'is {field_two_condition}.')}
            raise ValidationError(message, code='message')
        return False

    def validate_results_tb_treatment_and_prevention(self):
        started_on_TB_treatment = self.cleaned_data.get('started_on_TB_treatment')
        diagnosed_with_TB = self.cleaned_data.get('diagnosed_with_TB')

        if started_on_TB_treatment != YES and diagnosed_with_TB == YES:
                raise ValidationError({
                    'started_on_TB_treatment': 'If diagnosed with tb, this field must be Yes',
                })

    def diagnoses_required_validation(self):

        tb_tests_responses = [obj.short_name for obj in self.cleaned_data.get('tb_tests', [])]
        self.required_if_true(any(response != 'None' for response in tb_tests_responses),
                              field_required='diagnosed_with_TB')

    def not_flourish_referral_validation(self):
        referral_fields = ['clinic_visit_date', 'tb_tests', 'diagnosed_with_TB', ]

        for referral_field in referral_fields:

            self.required_if(NO,
                             field='flourish_referral',
                             field_required=referral_field)
