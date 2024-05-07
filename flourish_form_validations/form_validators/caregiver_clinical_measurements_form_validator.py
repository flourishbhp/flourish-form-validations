from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class CaregiverClinicalMeasurementsFormValidator(FormValidatorMixin,
                                                 FormValidator):

    def clean(self):

        cleaned_data = self.cleaned_data
        self.subject_identifier = cleaned_data.get(
            'maternal_visit').subject_identifier
        super().clean()

        self.check_all_cm_tb_del_valid()
        self.check_all_cm_valid_1000M()
        self.check_all_cm_valid_2000M()
        self.check_all_cm_valid_3000M()

        if (cleaned_data.get('systolic_bp') and cleaned_data.get('diastolic_bp')):
            if cleaned_data.get('systolic_bp') < cleaned_data.get('diastolic_bp'):
                msg = {'diastolic_bp':
                       'Systolic blood pressure cannot be lower than the'
                       'diastolic blood pressure. Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)

        self.required_if_not_none(field='systolic_bp', field_required='diastolic_bp')

        self.required_if_true(cleaned_data.get('systolic_bp') is not None
                              and cleaned_data.get('diastolic_bp') is not None,
                              field_required='confirm_values')

        measurements = [
            ('waist_circ', 'waist_circ_second', 'waist_circ_third'),
            ('hip_circ', 'hip_circ_second', 'hip_circ_third'),
        ]

        for fields in measurements:
            self.validate_measurement_margin(*fields)

    @property
    def check_all_cm(self):
        height = self.cleaned_data.get('height')
        weight_kg = self.cleaned_data.get('weight_kg')
        systolic_bp = self.cleaned_data.get('systolic_bp')
        diastolic_bp = self.cleaned_data.get('diastolic_bp')
        hip_circ = self.cleaned_data.get('hip_circ')
        waist_circ = self.cleaned_data.get('waist_circ')
        cm_all = [height, weight_kg, systolic_bp, diastolic_bp, hip_circ, waist_circ]

        return not any(item is None for item in cm_all)

    @property
    def check_all_cm_1000(self):
        height = self.cleaned_data.get('height')
        weight_kg = self.cleaned_data.get('weight_kg')
        systolic_bp = self.cleaned_data.get('systolic_bp')
        diastolic_bp = self.cleaned_data.get('diastolic_bp')

        cm_all = [height, weight_kg, systolic_bp, diastolic_bp, ]

        return not any(item is None for item in cm_all)

    @property
    def check_all_cm_3000(self):
        weight_kg = self.cleaned_data.get('weight_kg')
        systolic_bp = self.cleaned_data.get('systolic_bp')
        diastolic_bp = self.cleaned_data.get('diastolic_bp')

        cm_all = [weight_kg, systolic_bp, diastolic_bp, ]

        return not any(item is None for item in cm_all)

    @property
    def check_weight_bp_cm(self):
        weight_kg = self.cleaned_data.get('weight_kg')
        systolic_bp = self.cleaned_data.get('systolic_bp')
        diastolic_bp = self.cleaned_data.get('diastolic_bp')

        cm_all_2000D = [weight_kg, systolic_bp, diastolic_bp]

        return not any(item is None for item in cm_all_2000D)

    def check_all_cm_tb_del_valid(self):
        obtained_all_cm = self.cleaned_data.get('all_measurements')
        confirm_values = self.cleaned_data.get('confirm_values')
        visit_code = self.cleaned_data.get('maternal_visit').visit_code

        if visit_code in ['2100T', '2000D']:
            if (self.check_weight_bp_cm
                    and obtained_all_cm == YES and confirm_values == NO):
                message = {'confirm_values':
                           'Are you sure about the given values please confirm!'}
                self._errors.update(message)
                raise ValidationError(message)

            elif obtained_all_cm == YES and not self.check_weight_bp_cm:
                message = {'all_measurements':
                           'Please provide all measurements'}
                self._errors.update(message)
                raise ValidationError(message)

            elif obtained_all_cm == NO and self.check_weight_bp_cm:
                message = {'all_measurements':
                           'All measurements have been given please select Yes.'}
                self._errors.update(message)
                raise ValidationError(message)

    def check_all_cm_valid_1000M(self):
        obtained_all_cm = self.cleaned_data.get('all_measurements')
        confirm_values = self.cleaned_data.get('confirm_values')
        visit_code = self.cleaned_data.get('maternal_visit').visit_code

        if visit_code == '1000M':

            if (self.check_all_cm_1000
                    and obtained_all_cm == YES and confirm_values != YES):
                message = {'confirm_values':
                           'Are you sure about the given values please confirm!'}
                self._errors.update(message)
                raise ValidationError(message)

            elif obtained_all_cm == NO and self.check_all_cm_1000:
                message = {'all_measurements':
                           'All measurements have been given please select Yes'}
                self._errors.update(message)
                raise ValidationError(message)

            elif obtained_all_cm == YES and not self.check_all_cm_1000:
                message = {'all_measurements':
                           'Please provide all measurements'}
                self._errors.update(message)
                raise ValidationError(message)

    def check_all_cm_valid_2000M(self):
        obtained_all_cm = self.cleaned_data.get('all_measurements')
        confirm_values = self.cleaned_data.get('confirm_values')
        visit_code = self.cleaned_data.get('maternal_visit').visit_code

        if visit_code == '2000M':

            if self.check_all_cm and obtained_all_cm == YES and confirm_values != YES:
                message = {'confirm_values':
                           'Are you sure about the given values please confirm!'}
                self._errors.update(message)
                raise ValidationError(message)

            elif obtained_all_cm == NO and self.check_all_cm:
                message = {'all_measurements':
                           'All measurements have been given please select Yes'}
                self._errors.update(message)
                raise ValidationError(message)

            elif obtained_all_cm == YES and not self.check_all_cm:
                message = {'all_measurements':
                           'Please provide all measurements'}
                self._errors.update(message)
                raise ValidationError(message)

    def check_all_cm_valid_3000M(self):
        obtained_all_cm = self.cleaned_data.get('all_measurements')
        confirm_values = self.cleaned_data.get('confirm_values')
        visit_code = self.cleaned_data.get('maternal_visit').visit_code

        if visit_code == '3000M':

            if (self.check_all_cm_3000
                    and obtained_all_cm == YES and confirm_values != YES):
                message = {'confirm_values':
                           'Are you sure about the given values please confirm!'}
                self._errors.update(message)
                raise ValidationError(message)

            elif obtained_all_cm == NO and self.check_all_cm_3000:
                message = {'all_measurements':
                           'All measurements have been given please select Yes'}
                self._errors.update(message)
                raise ValidationError(message)

            elif obtained_all_cm == YES and not self.check_all_cm_3000:
                message = {'all_measurements':
                           'Please provide all measurements'}
                self._errors.update(message)
                raise ValidationError(message)

    def validate_measurement_margin(self, first_measurement_field,
                                    second_measurement_field,
                                    third_measurement_field):
        first_measurement = self.cleaned_data.get(first_measurement_field, None)
        second_measurement = self.cleaned_data.get(second_measurement_field, None)

        if first_measurement and second_measurement:
            margin = abs(first_measurement - second_measurement)
            self.required_if_true(
                margin >= 1,
                field_required=third_measurement_field
            )
