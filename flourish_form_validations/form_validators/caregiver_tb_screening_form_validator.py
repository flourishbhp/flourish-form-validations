from edc_constants.constants import NO, NONE, OTHER, YES,POS,NEG
from edc_form_validators import FormValidator
from django.core.exceptions import ValidationError
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
                         field_required='flourish_referral')

        self.required_if(NO,
                         field='flourish_referral',
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

        self.m2m_other_specify(
            NONE,
            m2m_field='tb_tests',
            field_other='diagnosed_with_TB',
        )

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

        self.validate_other_specify(
            field='started_on_TB_preventative_therapy'
        )

        self.required_if(YES,
                         field='diagnosed_with_TB',
                         field_required='started_on_TB_treatment')

        field_responses = {
            'chest_xray': 'chest_xray_results',
            'sputum_sample': 'sputum_sample_results',
            'stool_sample':'stool_sample_results',
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

        self.validate_results_tb_treatment_and_prevention()

    def validate_results_tb_treatment_and_prevention(self):
        started_on_TB_treatment = self.cleaned_data.get('started_on_TB_treatment')
        started_on_TB_preventative_therapy = self.cleaned_data.get('started_on_TB_preventative_therapy')
        test_results = [
            self.cleaned_data.get('chest_xray_results'),
            self.cleaned_data.get('sputum_sample_results'),
            self.cleaned_data.get('urine_test_results'),
            self.cleaned_data.get('skin_test_results'),
            self.cleaned_data.get('blood_test_results'),
        ]

        any_positive = POS in test_results
        all_negative = all(result == NEG for result in test_results)


        if any_positive:
            if started_on_TB_treatment != YES and started_on_TB_preventative_therapy != YES:
                raise ValidationError({
                    'started_on_TB_treatment': 'If any test result is positive, this field must be Yes',
                    'started_on_TB_preventative_therapy': 'If any test result is positive, this field must be Yes.',
                })
        if all_negative:
            if started_on_TB_treatment != NO :
                raise ValidationError({
                    'started_on_TB_treatment': 'If all test results are negative, this field must not be Yes or Other.',
                    })
