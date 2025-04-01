from edc_constants.constants import NO, OTHER, YES, DWTA
from edc_form_validators import FormValidator

from .crf_form_validator import FormValidatorMixin


class HITSPostReferralFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):

        self.subject_identifier = self.cleaned_data.get(
            'maternal_visit').subject_identifier
        super().clean()

        self.m2m_required_if(
           NO,
           field='visited_referral_site',
           m2m_field='reason_unvisited')

        self.m2m_other_specify(
            OTHER,
            m2m_field='reason_unvisited',
            field_other='reason_unvisited_other')

        self.required_if(
            YES,
            field='visited_referral_site',
            field_required='received_support')

        self.required_if(
            NO,
            field='received_support',
            field_required='no_support_reason')

        self.required_if(
            OTHER,
            field='no_support_reason',
            field_required='no_support_reason_other')

        self.required_if(
            YES,
            field='received_support',
            field_required='support_type')

        self.m2m_other_specify(
            OTHER,
            m2m_field='support_type',
            field_other='support_type_other')

        self.required_if(
            YES,
            field='received_support',
            field_required='health_improved')

        self.m2m_other_specify(
            OTHER,
            m2m_field='health_improved',
            field_other='health_improved_other')

        self.required_if(
            YES,
            field='received_support',
            field_required='supp_member_percept')

        self.required_if(
            OTHER,
            field='supp_member_percept',
            field_required='supp_member_percept_other')

        fields = ['satisfied_w_clinic', 'visit_helpful']

        for field in fields:
            self.required_if(
                YES,
                field='visited_referral_site',
                field_required=field)

        self.not_required_if(
            DWTA,
            field='visited_referral_site',
            field_required='additional_counseling')
