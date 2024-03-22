from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, OTHER, YES
from edc_form_validators import FormValidator, INVALID_ERROR, NOT_REQUIRED_ERROR

from .crf_form_validator import FormValidatorMixin


class BreastMilkFormValidatorMixin(FormValidatorMixin, FormValidator):
    birth_feeding_vaccine_model = 'flourish_child.birthfeedingvaccine'

    @property
    def birth_feeding_vaccine_model_cls(self):
        return django_apps.get_model(self.birth_feeding_vaccine_model)

    def onschedule_model_cls(self, onschedule_model):
        return django_apps.get_model(onschedule_model)

    def validate_infection_type(self, m2m_field, infection_type):

        infection_type = self.cleaned_data.get(infection_type)
        m2m_field_options = self.cleaned_data.get(m2m_field)

        if m2m_field_options and m2m_field_options.count() > 0:
            selected = {obj.short_name: obj.name for obj in m2m_field_options}
            if ((infection_type != 'unilateral' and 'uninfected_breast' in
                 selected.keys())):
                message = {
                    m2m_field: 'Breastfed from uninfected breast and pumped and dumped '
                               'from the affected breast” can only be selected if '
                               'mastitis is “Unilateral”.'}
                self._errors.update(message)
                self._error_codes.append(NOT_REQUIRED_ERROR)
                raise ValidationError(message, code=NOT_REQUIRED_ERROR)

            if m2m_field_options.count() > 1:
                if OTHER not in selected.keys() and m2m_field_options.count() < 3:
                    message = {
                        m2m_field:
                            f'You can only select more than 1 options if you include '
                            f'\'Other\' option in your selection otherwise select only '
                            f' 1 option'}
                    self._errors.update(message)
                    self._error_codes.append(INVALID_ERROR)
                    raise ValidationError(message, code=INVALID_ERROR)
                if m2m_field_options.count() > 2:
                    message = {
                        m2m_field:
                            f'You can only select 1 option if you include \'Other\' '
                            f'option in your selection. '}
                    self._errors.update(message)
                    self._error_codes.append(INVALID_ERROR)
                    raise ValidationError(message, code=INVALID_ERROR)

    def get_child_subject_identifier_by_visit(self, visit):
        """Returns the child subject identifier by visit."""
        onschedule_model_cls = self.onschedule_model_cls(
            visit.schedule.onschedule_model)

        try:
            onschedule_obj = onschedule_model_cls.objects.get(
                subject_identifier=visit.subject_identifier,
                schedule_name=visit.schedule_name)
        except onschedule_model_cls.DoesNotExist:
            return None
        else:
            return onschedule_obj.child_subject_identifier

    def get_birth_feeding_vaccine(self, child_subject_identifier, visit_code):
        try:
            return self.birth_feeding_vaccine_model_cls.objects.filter(
                child_visit__subject_identifier=child_subject_identifier,
                child_visit__visit_code=visit_code
            ).latest('report_datetime')
        except self.birth_feeding_vaccine_model_cls.DoesNotExist:
            return None

    def validate_breastfeeding_date(self, breastfeeding_date):
        breastfeeding_date_value = self.cleaned_data.get(breastfeeding_date)

        if not breastfeeding_date_value:
            return

        maternal_visit = self.cleaned_data.get('maternal_visit')
        message = None
        child_subject_identifier = self.get_child_subject_identifier_by_visit(
            visit=maternal_visit
        )
        if child_subject_identifier:
            infant_feeding = self.get_birth_feeding_vaccine(
                child_subject_identifier=child_subject_identifier,
                visit_code='2000D'
            )
            if infant_feeding:
                if infant_feeding.breastfeed_start_dt > breastfeeding_date_value:
                    message = {
                        breastfeeding_date: f'Date cannot be before breastfeeding '
                                            f'initiation date on the infant feeding '
                                            f'form at birth visit'}
            else:
                message = ('could not find birth feeding and vaccine object for child '
                           f'{child_subject_identifier} at 2000D visit')
        else:
            message = 'could not find related child identifier'
        if message:
            raise ValidationError(message)


class BreastMilkCRFFormValidator(BreastMilkFormValidatorMixin):

    def clean(self):
        super().clean()
        responses = ['yes_currently', 'yes_resolved']
        self.required_if_true(
            self.cleaned_data.get('exp_mastitis') in responses,
            field_required='exp_mastitis_count',
        )

        self.required_if(
            YES,
            field_required='exp_cracked_nipples_count',
            field='exp_cracked_nipples'
        )

        self.required_if(
            NO,
            field_required='not_collected_reasons',
            field='milk_collected'
        )

        milk_collected_field = ['breast_collected', 'milk_collected_volume',
                                'last_breastfed', 'recently_ate']

        for field in milk_collected_field:
            self.required_if(
                YES,
                field_required=field,
                field='milk_collected'
            )


class MastitisInlineFormValidator(BreastMilkFormValidatorMixin):

    def clean(self):
        super().clean()
        self.validate_breastfeeding_date(breastfeeding_date='mastitis_date_onset')
        self.m2m_other_specify(
            OTHER,
            m2m_field='mastitis_action',
            field_other='mastitis_action_other'
        )
        self.validate_infection_type(
            m2m_field='mastitis_action', infection_type='mastitis_type')


class CrackedNipplesInlineFormValidator(BreastMilkFormValidatorMixin):

    def clean(self):
        super().clean()
        self.validate_breastfeeding_date(breastfeeding_date='cracked_nipples_date_onset')
        self.m2m_other_specify(
            OTHER,
            m2m_field='cracked_nipples_action',
            field_other='cracked_nipples_action_other'
        )
        self.validate_infection_type(m2m_field='cracked_nipples_action',
                                     infection_type='cracked_nipples_type')
