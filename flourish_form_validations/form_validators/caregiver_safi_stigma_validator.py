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
            'insulted',
            'at_home',
            'at_neigborhood',
            'at_religious',
            'at_clinic',
            'at_workplace', ]

        discrimination_fields = [
            'finacial_support',
            'social_support',
            'stressed',
            'saddened',
        ]

        lwhiv_fields = [
            'social_effect',
            'emotional_effect',
            'pespective_changed']

        for field in fields + discrimination_fields + lwhiv_fields:
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

        discriminated = any(
            [self.cleaned_data.get(field, None) == 'ever_happened' for field in fields])
        discriminated_at_other = bool(self.cleaned_data.get('other_place', None))
        for field in discrimination_fields + ['social_effect', 'emotional_effect', ]:
            self.applicable_if_true(
                discriminated or discriminated_at_other,
                field_applicable=field,
                applicable_msg=(
                    'This field is applicable, participant experienced discrimination'),
                not_applicable_msg=(
                    'This field is not applicable, no discrimination was experienced.'))

        fields_required = {'other_place': 'other_place_period', }

        for field, required in fields_required.items():
            self.required_if_not_none(
                field=field,
                field_required=required, )
