from django.forms import ValidationError
from edc_constants.constants import NEG, YES
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class BreastFeedingQuestionnaireFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):
        self.validate_feeding_hiv_status()
        self.validate_hiv_status_neg()

        self.m2m_other_specify('dur__other',
                               m2m_field='during_preg_influencers',
                               field_other='during_preg_influencers_other')

        self.m2m_other_specify('aft_influ_other',
                               m2m_field='after_delivery_influencers',
                               field_other='after_delivery_influencers_other')

        self.m2m_other_specify('feeding_oth',
                               m2m_field='infant_feeding_reasons',
                               field_other='infant_feeding_other')

        hiv_status = self.cleaned_data.get('hiv_status_during_preg')
        self.required_if_true(not hiv_status == NEG,
                              field_required='use_medicines')

        self.required_if(YES,
                         field='six_months_feeding',
                         field_required='infant_feeding_reasons')

        self.required_if(YES,
                         field='six_months_feeding',
                         field_required='infant_feeding_reasons')

        self.validate_other_specify(field='after_birth_opinion')

        self.m2m_single_selection_if(
            *['training_none', ], m2m_field='received_training')

        self.validate_training_outcome_required()

    def validate_hiv_status_neg(self):
        hiv_status = self.cleaned_data.get('hiv_status_during_preg')
        required_fields = [
            'hiv_status_known_by',
            'father_knew_hiv_status',
            'delivery_advice_vl_results',
            'delivery_advice_on_viralload',
            'after_delivery_advice_vl_results',
            'after_delivery_advice_on_viralload',
            'breastfeeding_duration',
        ]
        for field in required_fields:
            self.required_if_true(not hiv_status == NEG,
                                  field_required=field, )

    def validate_feeding_hiv_status(self):

        status = self.cleaned_data.get('feeding_hiv_status')
        required_fields = ['hiv_status_aware', 'on_hiv_status_aware']
        for field in required_fields:
            self.required_if_true(status in ['No', 'rather_not_answer'],
                                  field='feeding_hiv_status',
                                  field_required=field)

    def validate_training_outcome_required(self):
        responses = self.cleaned_data.get('received_training')
        training_outcome = self.cleaned_data.get('training_outcome')
        if responses and len(responses) > 0:
            for response in responses:
                if response.short_name != 'training_none' and training_outcome is None:
                    raise ValidationError(
                        {'training_outcome': 'This field is required.'})
                elif response.short_name == 'training_none' and training_outcome is not None:
                    raise ValidationError(
                        {'training_outcome': 'This field is not required.'})
