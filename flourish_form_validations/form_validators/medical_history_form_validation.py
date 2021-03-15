from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO, NOT_APPLICABLE, NEG, POS, OTHER
from edc_form_validators import FormValidator
from flourish_caregiver.helper_classes import MaternalStatusHelper

from .crf_form_validator import CRFFormValidator


class MedicalHistoryFormValidator(CRFFormValidator, FormValidator):
    antenatal_enrollment_model = 'flourish_caregiver.antenatalenrollment'

    @property
    def antenatal_enrollment_cls(self):
        return django_apps.get_model(self.antenatal_enrollment_model)

    @property
    def maternal_visit_cls(self):
        return django_apps.get_model(self.maternal_visit_model)

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'maternal_visit').subject_identifier
        super().clean()

        self.validate_chronic_since_who_diagnosis_neg(
            cleaned_data=self.cleaned_data)
        self.validate_who_diagnosis_who_chronic_list(
            cleaned_data=self.cleaned_data)
        self.validate_caregiver_chronic_multiple_selection()
        self.validate_other_caregiver()
        self.validate_caregiver_medications_multiple_selections()
        self.validate_other_caregiver_medications()

    def validate_chronic_since_who_diagnosis_neg(self, cleaned_data=None):

        subject_status = self.maternal_status_helper.hiv_status

        if subject_status == NEG and cleaned_data.get('chronic_since') == YES:
            msg = {'who_diagnosis':
                       'The caregiver is HIV negative. Chronic_since should be NO'}
            self._errors.update(msg)
            raise ValidationError(msg)

        self.applicable_if_true(
            subject_status == POS,
            field_applicable='who_diagnosis',
            not_applicable_msg=('The caregiver is HIV negative. Who Diagnosis '
                                'should be Not Applicable')
        )

        if subject_status == POS and cleaned_data.get('chronic_since') == NO:
            if cleaned_data.get('who_diagnosis') != NO:
                msg = {'who_diagnosis':
                           'The caregiver is HIV positive, because'
                           ' Chronic_since is '
                           'NO and Who Diagnosis should also be NO'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_who_diagnosis_who_chronic_list(self, cleaned_data=None):

        subject_status = self.maternal_status_helper.hiv_status

        if subject_status == POS and cleaned_data.get('who_diagnosis') == YES:
            qs = self.cleaned_data.get('who')
            if qs and qs.count() > 0:
                selected = {obj.short_name: obj.name for obj in qs}
                if NOT_APPLICABLE in selected:
                    msg = {'who':
                           'Participant indicated that they had WHO stage III '
                           'and IV, list of diagnosis cannot be N/A'}
                    self._errors.update(msg)
                    raise ValidationError(msg)
        elif cleaned_data.get('who_diagnosis') != YES:
            qs = self.cleaned_data.get('who')
            if qs and qs.count() > 0:
                selected = {obj.short_name: obj.name for obj in qs}
                if NOT_APPLICABLE not in selected:
                    msg = {'who':
                           'Participant indicated that they do not have '
                           'WHO stage III and IV, list of '
                           'diagnosis must be N/A'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

            self.m2m_single_selection_if(
                NOT_APPLICABLE,
                m2m_field='who')

    def validate_caregiver_chronic_multiple_selection(self, cleaned_data=None):

        qs = self.cleaned_data.get('caregiver_chronic')
        selected = {}
        if qs and qs.count() > 0:
            selected = {obj.short_name: obj.name for obj in qs}

        if cleaned_data.get('chronic_since') == YES:
            if NOT_APPLICABLE in selected:
                msg = {'caregiver_chronic':
                       'Participant indicated that they had chronic'
                       ' conditions list of diagnosis cannot be N/A'}
                self._errors.update(msg)
                raise ValidationError(msg)

        else:
            if NOT_APPLICABLE not in selected:
                msg = {'caregiver_chronic':
                       'Participant indicated that they had no chronic'
                       'conditions list of diagnosis should be N/A'}
                self._errors.update(msg)
                raise ValidationError(msg)

        self.m2m_single_selection_if(
            NOT_APPLICABLE,
            m2m_field='caregiver_chronic')

    def validate_other_caregiver(self):

        self.m2m_other_specify(
            OTHER,
            m2m_field='caregiver_chronic',
            field_other='caregiver_chronic_other')

    def validate_caregiver_medications_multiple_selections(self):
        selections = [NOT_APPLICABLE]
        self.m2m_single_selection_if(
            *selections,
            m2m_field='caregiver_medications')

    def validate_other_caregiver_medications(self):

        self.m2m_other_specify(
            OTHER,
            m2m_field='caregiver_medications',
            field_other='caregiver_medications_other')

    @property
    def maternal_status_helper(self):
        cleaned_data = self.cleaned_data
        status_helper = MaternalStatusHelper(
            cleaned_data.get('maternal_visit'))
        return status_helper
