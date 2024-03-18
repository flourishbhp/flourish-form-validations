from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, OTHER, YES
from edc_form_validators import FormValidator, INVALID_ERROR, NOT_REQUIRED_ERROR

from .crf_form_validator import FormValidatorMixin


class BreastMilkCRFFormValidator(FormValidatorMixin, FormValidator):
    birth_feeding_vaccine_model = 'flourish_child.birthfeedingvaccine'

    @property
    def birth_feeding_vaccine_model_cls(self):
        return django_apps.get_model(self.birth_feeding_vaccine_model)

    def onschedule_model_cls(self, onschedule_model):
        return django_apps.get_model(onschedule_model)

    def clean(self):
        required_fields_exp_mastitis = [
            'exp_mastitis_count'
        ]

        responses = ['yes_currently', 'yes_resolved']
        for field in required_fields_exp_mastitis:
            self.required_if_true(
                self.cleaned_data.get('exp_mastitis') in responses,
                field_required=field,
            )

        self.required_fields_for_condition("exp_mastitis_count", "mastitis")
        self.required_fields_for_condition("exp_cracked_nipples_count", "cracked_nipples")

        for x in range(1, 6):
            self.m2m_other_specify(
                f'm{x}_{OTHER}',
                m2m_field=f'mastitis_{x}_action',
                field_other=f'mastitis_{x}_action_other'
            )
            actions = f'mastitis_{x}_action'
            infection_type = f'mastitis_{x}_type'

            self.validate_infection_type(m2m_field=actions, infection_type=infection_type)

            self.validate_breastfeeding_date(
                breastfeeding_date=f'mastitis_{x}_date_onset')

            self.m2m_other_specify(
                f'cn{x}_{OTHER}',
                m2m_field=f'cracked_nipples_{x}_action',
                field_other=f'cracked_nipples_{x}_action_other'
            )
            actions = f'cracked_nipples_{x}_action'
            infection_type = f'cracked_nipples_{x}_type'

            self.validate_infection_type(m2m_field=actions, infection_type=infection_type)

            self.validate_breastfeeding_date(
                breastfeeding_date=f'cracked_nipples_{x}_date_onset')

            self.validate_stopped_breastfed(m2m_field=f'mastitis_{x}_action')
            self.validate_stopped_breastfed(m2m_field=f'cracked_nipples_{x}_action')

            sbnrq = [
                f'mastitis_{x}_date_onset',
                f'mastitis_{x}_type',
                f'mastitis_{x}_action',
                f'exp_cracked_nipples',
                f'milk_collected',
            ]

            mastitis_action_field = f'mastitis_{x}_action'

            if mastitis_action_field not in sbnrq:
                for field in sbnrq:
                    self.m2m_other_specify(
                        f'm{x}_stopped_breastfeeding',
                        m2m_field=mastitis_action_field,
                        field_other=field
                    )

        self.required_if(
            NO,
            field_required='not_collected_reasons',
            field='milk_collected'
        )

        milk_collected_field = ['breast_collected', 'milk_collected_volume',
                                'last_breastfed']

        for field in milk_collected_field:
            self.required_if(
                YES,
                field_required=field,
                field='milk_collected'
            )

    def validate_stopped_breastfed(self, m2m_field):
        qs = self.cleaned_data.get(m2m_field)
        excluded_fields = ['add_comments']
        action_key = self.extract_actions(m2m_field)
        if qs and qs.count() > 0:
            selected = {obj.short_name: obj.name for obj in qs}
            if f'{action_key}_stopped_breastfeeding' in selected:
                fields_after_trigger = False
                for field_name, field_value in self.cleaned_data.items():
                    if fields_after_trigger and field_name not in excluded_fields:
                        if field_value and field_name != m2m_field:
                            raise ValidationError(
                                {field_name: 'This field is not required.'}
                            )
                    elif field_name == m2m_field:
                        fields_after_trigger = True

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

    def validate_infection_type(self, m2m_field, infection_type):

        infection_type = self.cleaned_data.get(infection_type)
        m2m_field_options = self.cleaned_data.get(m2m_field)
        m2m_action_key = self.extract_actions(m2m_field)

        if m2m_field_options and m2m_field_options.count() > 0:
            selected = {obj.short_name: obj.name for obj in m2m_field_options}
            if ((infection_type != f'{m2m_action_key}_unilateral' and
                 f'{m2m_action_key}_uninfected_breast' in selected.keys())):
                message = {
                    m2m_field: 'Breastfed from uninfected breast and pumped and dumped '
                               'from the affected breast” can only be selected if '
                               'mastitis is “Unilateral”.'}
                self._errors.update(message)
                self._error_codes.append(NOT_REQUIRED_ERROR)
                raise ValidationError(message, code=NOT_REQUIRED_ERROR)

            if m2m_field_options.count() > 1:
                if (f'{m2m_action_key}_{OTHER}' not in selected.keys() and
                        m2m_field_options.count() < 3):
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
                if ((f'{m2m_action_key}both_breasts' and
                     f'{m2m_action_key}uninfected_breast') in selected.keys()):
                    message = {
                        m2m_field:
                            f'\'Breastfeed from both breasts\' and \'Breastfed from '
                            f'uninfected breast and pumped and dumped from the affected '
                            f'breast\' can not be selected together as they contradict '
                            f'each other'}
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

    def required_repeating_questions(self, condition, field_prefix):
        return {
            '1': [f"{field_prefix}_1_date_onset", f"{field_prefix}_1_type",
                  f"{field_prefix}_1_action"],
            '2': [f"{field_prefix}_1_date_onset", f"{field_prefix}_1_type",
                  f"{field_prefix}_1_action",
                  f"{field_prefix}_2_date_onset", f"{field_prefix}_2_type",
                  f"{field_prefix}_2_action"],
            '3': [f"{field_prefix}_1_date_onset", f"{field_prefix}_1_type",
                  f"{field_prefix}_1_action",
                  f"{field_prefix}_2_date_onset", f"{field_prefix}_2_type",
                  f"{field_prefix}_2_action",
                  f"{field_prefix}_3_date_onset", f"{field_prefix}_3_type",
                  f"{field_prefix}_3_action"],
            '4': [f"{field_prefix}_1_date_onset", f"{field_prefix}_1_type",
                  f"{field_prefix}_1_action",
                  f"{field_prefix}_2_date_onset", f"{field_prefix}_2_type",
                  f"{field_prefix}_2_action",
                  f"{field_prefix}_3_date_onset", f"{field_prefix}_3_type",
                  f"{field_prefix}_3_action",
                  f"{field_prefix}_4_date_onset", f"{field_prefix}_4_type",
                  f"{field_prefix}_4_action"],
            '5_greater': [f"{field_prefix}_1_date_onset", f"{field_prefix}_1_type",
                          f"{field_prefix}_1_action",
                          f"{field_prefix}_2_date_onset", f"{field_prefix}_2_type",
                          f"{field_prefix}_2_action",
                          f"{field_prefix}_3_date_onset", f"{field_prefix}_3_type",
                          f"{field_prefix}_3_action",
                          f"{field_prefix}_4_date_onset", f"{field_prefix}_4_type",
                          f"{field_prefix}_4_action",
                          f"{field_prefix}_5_date_onset", f"{field_prefix}_5_type",
                          f"{field_prefix}_5_action"],
        }

    def required_fields_for_condition(self, condition, field_prefix):
        fields = self.required_repeating_questions(condition, field_prefix)
        condition_value = self.cleaned_data.get(condition)
        if condition_value:
            for x in range(int(condition_value[0])):
                condition_fields = fields.get(condition_value)
                for field in condition_fields:
                    self.required_if(condition_value,
                                     field=condition,
                                     field_required=field)

    def extract_actions(self, field):
        action_key = ''
        if field.startswith("mastitis_"):
            action_number = field.split("_")[1]
            action_key = f"m{action_number}"
        elif field.startswith("cracked_nipples_"):
            action_number = field.split("_")[2]
            action_key = f"cn{action_number}"

        return action_key
