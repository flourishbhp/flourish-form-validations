from edc_constants.constants import NO, OTHER, YES
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class CaregiverTBReferralOutcomeFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):

        self.required_if(
                YES,
                field='tb_evaluation',
                field_required='clinic_name'
            )

        self.required_if(
            NO,
            field='tb_evaluation',
            field_required='reasons',
        )
        self.required_if(
            YES,
            field='tb_evaluation',
            field_required='evaluated',
        )
        self.required_if(
            NO,
            field='evaluated',
            field_required='reason_not_evaluated',
        )
        self.validate_other_specify(
            field='reason_not_evaluated',
            other_specify_field='reason_not_evaluated_other'
        )
        self.validate_other_specify(
            field='clinic_name',
            other_specify_field='clinic_name_other'
        )

        self.m2m_other_specify(
            m2m_field='tests_performed',
            field_other='other_test_specify'
        )

        qs = self.cleaned_data.get('tests_performed')
        selected = {obj.short_name: obj.name for obj in qs}

        response_mapping = {'chest_xray': 'chest_xray_results',
                            'sputum_sample': 'sputum_sample_results',
                            'stool_sample': 'stool_sample_results',
                            'urine_test': 'urine_test_results',
                            'skin_test': 'skin_test_results',
                            'blood_test': 'blood_test_results',
                            OTHER: 'other_test_results'}

        for response, field in response_mapping.items():
            self.required_if_true(
                response in selected,
                field_required=field)
    
        self.required_if(
            YES,
            field='tb_treatment',
            field_required='tb_preventative_therapy'
            )

        self.validate_other_specify(
            field='tb_treatment',
            other_specify_field='other_tb_treatment'
        )
        self.validate_other_specify(
            field='reasons',
            other_specify_field='other_reasons'
        )

        self.validate_other_specify(
            field='tb_preventative_therapy',
            other_specify_field='other_tb_preventative_therapy'
        )

        self.validate_other_specify(
            field='tb_isoniazid_preventative_therapy',
            other_specify_field='other_tb_isoniazid_preventative_therapy'
        )

        required_fields =['tests_performed','diagnosed_with_tb','tb_treatment',
                         'tb_preventative_therapy' ]
        for field in required_fields:
            self.required_if(
                    YES,
                    field='evaluated',
                    field_required=field
                )

