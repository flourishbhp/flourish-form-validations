from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator

from .crf_form_validator import CRFFormValidator


class CaregiverClinicalMeasurementsFormValidator(CRFFormValidator,
                                                 FormValidator):

    def clean(self):

        cleaned_data = self.cleaned_data
        self.subject_identifier = cleaned_data.get(
            'maternal_visit').subject_identifier
        super().clean()

        if (cleaned_data.get('systolic_bp') and
                cleaned_data.get('diastolic_bp')):
            if cleaned_data.get('systolic_bp') < \
                    cleaned_data.get('diastolic_bp'):
                msg = {'diastolic_bp': 'Systolic blood pressure '
                                       'cannot be lower '
                                       'than the diastolic blood pressure. '
                                       'Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)
