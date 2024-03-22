from dateutil.relativedelta import relativedelta
from edc_constants.constants import NEG, POS, YES


class TestModeMixin:

    def __init__(self, validator_class, *args, **kwargs):
        super().__init__(*args, **kwargs)

        validator_class = validator_class

        validator_class.caregiver_consent_model = \
            'flourish_form_validations.subjectconsent'

        validator_class.subject_consent_model = \
            'flourish_form_validations.subjectconsent'

        validator_class.caregiver_child_consent_model = \
            'flourish_form_validations.caregiverchildconsent'

        validator_class.maternal_dataset_model = \
            'flourish_form_validations.maternaldataset'

        validator_class.child_dataset_model = \
            'flourish_form_validations.childdataset'

        validator_class.antenatal_enrollment_model = \
            'flourish_form_validations.antenatalenrollment'

        validator_class.subject_screening_model = \
            'flourish_form_validations.subjectscreening'

        validator_class.prior_screening_model = \
            'flourish_form_validations.subjectscreening'

        validator_class.arvs_pre_preg_model = \
            'flourish_form_validations.arvsprepregnancy'

        validator_class.preg_women_screening_model = \
            'flourish_form_validations.subjectscreening'

        validator_class.caregiver_locator_model = \
            'flourish_form_validations.caregiverlocator'

        validator_class.delivery_model = \
            'flourish_form_validations.maternaldelivery'

        validator_class.maternal_delivery_model = \
            'flourish_form_validations.maternaldelivery'

        validator_class.maternal_visit_model = \
            'flourish_form_validations.maternalvisit'

        validator_class.maternal_arv_model = \
            'flourish_form_validations.maternalarv'

        validator_class.arvs_pre_pregnancy = \
            'flourish_form_validations.maternalarvduringpreg'

        validator_class.ultrasound_model = \
            'flourish_form_validations.ultrasound'

        validator_class.screening_preg_women = \
            'flourish_form_validations.screeningpregwomen'

        validator_class.caregiver_offstudy_model = \
            'flourish_form_validations.offstudy'

        validator_class.caregiver_contact_model = \
            'flourish_form_validations.caregivercontact'

        validator_class.consent_version_model = \
            'flourish_form_validations.flourishconsentversion'

        validator_class.caregiver_locator_model = \
            'flourish_form_validations.caregiverlocator'

        validator_class.child_assent_model = \
            'flourish_form_validations.childassent'

        birth_feeding_vaccine_model = 'flourish_form_validations.birthfeedingvaccine'

    class Meta:
        abstract = True


class TestEnrollmentHelper(object):

    def __init__(self, instance_antenatal, exception_cls=None):
        self.instance_antenatal = instance_antenatal
        self.date_at_32wks = (
            self.evaluate_edd_by_lmp - relativedelta(weeks=6) if
            self.evaluate_edd_by_lmp else None)
        self.exception_cls = exception_cls

    @property
    def enrollment_hiv_status(self):
        pos = self.known_hiv_pos()

        neg = self.tested_neg_previously_result_within_3_months()

        if self.rapidtest_result() in [POS, NEG]:
            return self.rapidtest_result()
        elif neg and not pos:
            return NEG
        elif pos and not neg:
            return POS
        else:
            raise self.exception_cls

    def known_hiv_pos(self):
        return self.instance_antenatal.current_hiv_status == POS

    def rapidtest_result(self):
        if self.instance_antenatal.rapid_test_done == YES:
            return self.instance_antenatal.rapid_test_result

    @property
    def evaluate_edd_by_lmp(self):
        return (
            self.instance_antenatal.last_period_date +
            relativedelta(days=280) if
            self.instance_antenatal.last_period_date else None)

    def tested_neg_previously_result_within_3_months(self):
        if (self.instance_antenatal.week32_test_date and
                self.instance_antenatal.week32_test == YES and
                self.instance_antenatal.week32_test_date >=
                (self.instance_antenatal.report_datetime.date() -
                 relativedelta(months=3)) and
                self.instance_antenatal.current_hiv_status == NEG):
            return True
        return False
