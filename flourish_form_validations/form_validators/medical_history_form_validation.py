from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, NOT_APPLICABLE, POS, YES
from edc_form_validators import FormValidator

from flourish_caregiver.helper_classes import MaternalStatusHelper
from .crf_form_validator import FormValidatorMixin


class MedicalHistoryFormValidator(FormValidatorMixin, FormValidator):
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

        self.validate_other_specify(field='current_symptoms')

        illness_fields = ['current_symptoms',
                          'symptoms_start_date', 'clinic_visit']

        for field in illness_fields:
            self.required_if(
                YES,
                field_required=field,
                field='current_illness',
            )

        self.validate_caregiver_chronic_multiple_selection(
            cleaned_data=self.cleaned_data)
        self.validate_who_diagnosis_neg(
            cleaned_data=self.cleaned_data)
        self.validate_who_diagnosis_who_chronic_list(
            cleaned_data=self.cleaned_data)
        self.validate_other_caregiver()
        self.validate_caregiver_medications_multiple_selections()
        self.validate_other_caregiver_medications()
        self.applicable_if_true(
            self.subject_status == POS,
            field_applicable='know_hiv_status', )

    def validate_who_diagnosis_neg(self, cleaned_data=None):
        subject_status = self.maternal_status_helper.hiv_status

        self.applicable_if_true(
            subject_status == POS,
            field_applicable='who_diagnosis',
            applicable_msg=('The caregiver is HIV positive. WHO Diagnosis is '
                            'applicable.'),
            not_applicable_msg=('The caregiver is HIV negative. WHO Diagnosis '
                                'is Not Applicable')
        )

    def validate_who_diagnosis_who_chronic_list(self, cleaned_data=None):
        subject_status = self.maternal_status_helper.hiv_status

        if subject_status == POS and cleaned_data.get('who_diagnosis') == YES:
            qs = self.cleaned_data.get('who')
            if qs and qs.count() > 0:
                selected = {obj.short_name: obj.name for obj in qs}
                if 'who_na' in selected:
                    msg = {'who':
                           'Participant indicated that they had WHO stage III '
                           'and IV, list of diagnosis cannot be N/A'}
                    self._errors.update(msg)
                    raise ValidationError(msg)
        elif cleaned_data.get('who_diagnosis') != YES:
            m2m = 'who'
            message = ('Participant did not indicate that they have WHO stage'
                       ' III and IV, list of diagnosis must be N/A')
            self.validate_m2m_na(m2m, response='who_na', message=message)

        self.m2m_other_specify(
            'who_other',
            m2m_field='who',
            field_other='who_other')

    def validate_caregiver_chronic_multiple_selection(self, cleaned_data=None):
        selected = {}
        qs = self.cleaned_data.get('caregiver_chronic')
        if qs and qs.count() > 0:
            selected = {obj.short_name: obj.name for obj in qs}
        if cleaned_data.get('chronic_since') == YES:
            if 'mhist_na' in selected:
                msg = {'caregiver_chronic':
                       'Participant indicated that they had chronic'
                       ' conditions list of diagnosis cannot be N/A'}
                self._errors.update(msg)
                raise ValidationError(msg)
        elif cleaned_data.get('chronic_since') == NO:
            if 'mhist_na' not in selected:
                msg = {'caregiver_chronic':
                       'Participant indicated that they had no chronic '
                       'conditions list of diagnosis should be N/A'}
                self._errors.update(msg)
                raise ValidationError(msg)
        self.m2m_single_selection_if(
            'mhist_na',
            m2m_field='caregiver_chronic')

    def validate_other_caregiver(self):
        self.m2m_other_specify(
            'mhist_other',
            m2m_field='caregiver_chronic',
            field_other='caregiver_chronic_other')

    def validate_caregiver_medications_multiple_selections(self):
        selections = ['mmed_na', 'mmed_none']
        self.m2m_single_selection_if(
            *selections,
            m2m_field='caregiver_medications')

    def validate_other_caregiver_medications(self):
        self.m2m_other_specify(
            'mmed_other',
            m2m_field='caregiver_medications',
            field_other='caregiver_medications_other')

    def validate_m2m_na(self, m2m_field, response=NOT_APPLICABLE, message=None):
        qs = self.cleaned_data.get(m2m_field)
        message = message or 'This field is not applicable.'
        if qs and qs.count() > 0:
            selected = {obj.short_name: obj.name for obj in qs}
            if response not in selected:
                msg = {m2m_field: message}
                self._errors.update(msg)
                raise ValidationError(msg)

            self.m2m_single_selection_if(
                response,
                m2m_field=m2m_field)

    @property
    def maternal_status_helper(self):
        cleaned_data = self.cleaned_data
        visit_obj = cleaned_data.get('maternal_visit')
        if visit_obj:
            return MaternalStatusHelper(visit_obj)
