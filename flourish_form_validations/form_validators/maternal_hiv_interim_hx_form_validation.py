from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO, NOT_APPLICABLE
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class MaternalHivInterimHxFormValidator(FormValidatorMixin,
                                        FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'maternal_visit').subject_identifier
        super().clean()

        required_fields = ('cd4_date', 'cd4_result',)
        for required in required_fields:
            self.required_if(
                YES,
                field='has_cd4',
                field_required=required,
                required_msg=('You indicated that a CD4 count was performed. '
                              f'Please provide the {required}'),
                not_required_msg=('You indicated that a CD4 count was NOT '
                                  f'performed, yet provided a {required} '
                                  'CD4 was performed. Please correct.')
            )

        self.required_if(
            YES,
            field='has_vl',
            field_required='vl_date',
            required_msg=('You indicated that a VL count was performed. '
                          'Please provide the date.'),
            not_required_msg=('You indicated that a VL count was NOT performed, '
                              'yet provided a date VL was performed. Please correct.')
        )
        self.applicable_if(
            YES,
            field='has_vl',
            field_applicable='vl_detectable'
        )

        self.not_required_if(
            NOT_APPLICABLE,
            field='vl_detectable',
            field_required='vl_result'
        )

        self._validate_vl_result()

    def _validate_vl_result(self):
        """
        Used to validate vl_result based on vl_detectable
        """
        # Get data fro the form and convert to on integer
        vl_detectable: str = self.cleaned_data.get('vl_detectable')
        vl_result: str = self.cleaned_data.get('vl_result')

        if vl_result:
            if vl_detectable == NO:
                if '<' in vl_result:
                    vl_result = vl_result[1:]
                    if not (int(vl_result) <= 400):
                        raise ValidationError({'vl_result': 'Viral load should be 400 or less if it is'
                                                            ' not detectable'})
                elif '>' in vl_result:
                    raise ValidationError({'vl_result': 'Cannot be >'})
                else:
                    if not (int(vl_result) <= 400):
                        raise ValidationError({'vl_result': 'Viral load should be 400 or less if it is'
                                                            ' not detectable'})
            if vl_detectable == YES:
                if '>' in vl_result:
                    vl_result = vl_result[1:]
                    if not (int(vl_result) > 400):
                        raise ValidationError({'vl_result': 'Viral load should be more than 400 if it is'
                                                            ' detectable'})
                elif '<' in vl_result:
                    raise ValidationError({'vl_result': 'Cannot be <'})
                else:
                    if not (int(vl_result) > 400):
                        raise ValidationError({'vl_result': 'Viral load should be more than 400 if it is'
                                                            ' detectable'})
