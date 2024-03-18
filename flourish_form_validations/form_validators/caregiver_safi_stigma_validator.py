from edc_constants.constants import POS, YES
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class CaregiverSafiStigmaFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_period_required()

    def validate_period_required(self):

        fields = [
            'judged',
            'avoided',
            'discriminated',
            'at_home',
            'at_neigborhood',
            'at_religious',
            'at_clinic',
            'at_workplace',
            'finacial_support',
            'social_support',
            'stressed',
            'saddened',
        ]

        lwhiv_fields = [
            'social_effect',
            'emotional_effect',
            'pespective_changed']

        for field in fields + lwhiv_fields:
            self.required_if(
                'ever_happened',
                field=field,
                field_required=f'{field}_period'
            )

        member_lwhiv = (self.cleaned_data.get('member_lwhiv', None) == YES)
        lwhiv = self.caregiver_hiv_status(self.subject_identifier) == POS

        for field in fields:
            self.applicable_if_true(
                member_lwhiv or lwhiv,
                field_applicable=field)

        fields_required = {'other_place': 'other_place_period',
                           'other_discr': 'other_discr_period'}

        for field, required in fields_required.items():
            self.required_if_not_none(
                field=field,
                field_required=required, )
