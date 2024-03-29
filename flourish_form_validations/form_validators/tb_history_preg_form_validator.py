from edc_constants.constants import YES
from edc_form_validators import FormValidator
from .crf_form_validator import FormValidatorMixin


class TbHistoryPregFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):

        self.subject_identifier = self.cleaned_data.get(
            'maternal_visit').subject_identifier
        super().clean()

        self.required_if(
            YES,
            field='history_of_tbt',
            field_required='tbt_completed')

        self.required_if(
            YES,
            field='prior_tb_history',
            field_required='tb_diagnosis_type')

        self.required_if(
            'extra_pulmonary',
            field='tb_diagnosis_type',
            field_required='extra_pulmonary_loc')

        fields_required = ['tb_drugs_freq', 'iv_meds_used', 'tb_treatmnt_completed']

        for field in fields_required:
            self.required_if(
                YES,
                field='prior_treatmnt_history',
                field_required=field)
