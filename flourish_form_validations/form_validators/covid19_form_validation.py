from django.core.exceptions import ValidationError
from edc_constants.constants import YES, POS, NO
from edc_form_validators import FormValidator


class Covid19FormValidator(FormValidator):

    def clean(self):

        self.validate_visit()

        self.validate_booster_vac()

        required_fields = [
            'date_of_test', 'is_test_estimated', 'reason_for_testing',
            'result_of_test'
        ]

        for field in required_fields:
            self.required_if(YES,
                             field='test_for_covid',
                             field_required=field)

        self.m2m_required_if(POS,
                             field='result_of_test',
                             m2m_field='isolations_symptoms')

        self.required_if(POS,
                         field='result_of_test',
                         field_required='isolation_location')

        self.validate_other_specify(field='reason_for_testing',
                                    other_specify_field='other_reason_for_testing')
        self.validate_other_specify(field='isolation_location',
                                    other_specify_field='other_isolation_location')

        self.required_if(YES,
                         field='has_tested_positive',
                         field_required='date_of_test_member')

        single_selection_fields = {}
        if 'maternal_visit' in self.cleaned_data:
            single_selection_fields = {
                'isolations_symptoms': 'c19m_iso_nosympt',
                'symptoms_for_past_14days': 'c19m_14d_nosympt'}
        else:
            single_selection_fields = {
                'isolations_symptoms': 'c19c_iso_nosympt',
                'symptoms_for_past_14days': 'c19c_14d_nosympt'}

        for field, response in single_selection_fields.items():
            self.m2m_single_selection_if(response, m2m_field=field)

        if self.cleaned_data.get('fully_vaccinated') == YES:

            if self.cleaned_data.get(
                    "vaccination_type") != "johnson_and_johnson":
                required_fields = ['vaccination_type', 'first_dose',
                                   'second_dose']
                for field in required_fields:
                    self.required_if(YES,
                                     field='fully_vaccinated',
                                     field_required=field)

                self.validate_other_specify(field='vaccination_type',
                                            other_specify_field='other_vaccination_type')
                first_dose = self.cleaned_data['first_dose']
                second_dose = self.cleaned_data['second_dose']
                if second_dose < first_dose:
                    raise ValidationError({
                        'second_dose': 'Should be greater than the first date'})
                elif second_dose == first_dose:
                    raise ValidationError({
                        'first_dose': 'Dates cannot be equal',
                        'second_dose': 'Dates cannot be equal',
                    })

            else:
                required_fields = ['vaccination_type', 'first_dose']
                for field in required_fields:
                    self.required_if(YES,
                                     field='fully_vaccinated',
                                     field_required=field)

                not_required = ['other_vaccination_type', 'second_dose']

                for field in not_required:
                    self.not_required_if(
                        'johnson_and_johnson',
                        field='vaccination_type',
                        field_required=field
                    )

        elif self.cleaned_data.get('fully_vaccinated') == 'partially_jab':

            required_fields = ['vaccination_type', 'first_dose']

            for field in required_fields:
                self.required_if('partially_jab',
                                 field='fully_vaccinated',
                                 field_required=field)

            self.validate_other_specify(field='vaccination_type',
                                        other_specify_field='other_vaccination_type')

            self.not_required_if('partially_jab',
                                 field='fully_vaccinated',
                                 field_required='second_dose')

        else:
            not_required_fields = ['vaccination_type', 'other_vaccination_type',
                                   'first_dose', 'second_dose']
            for field in not_required_fields:
                self.not_required_if(NO,
                                     field='fully_vaccinated',
                                     field_required=field)

        return super().clean()

    def validate_booster_vac(self):
        self.required_if(
            YES,
            field='fully_vaccinated',
            field_required='received_booster'
        )

        fields = ['booster_vac_type', 'booster_vac_date']

        for field in fields:
            self.required_if(
                YES,
                field='received_booster',
                field_required=field
            )

        self.validate_other_specify(
            field='booster_vac_type',
            other_specify_field='other_booster_vac_type'
        )

    def validate_visit(self):
        if 'maternal_visit' in self.cleaned_data:
            self.subject_identifier = self.cleaned_data.get(
                'maternal_visit').subject_identifier
        else:
            self.subject_identifier = self.cleaned_data.get(
                'child_visit').subject_identifier
