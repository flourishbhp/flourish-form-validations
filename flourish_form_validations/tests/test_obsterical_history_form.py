from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow

from ..form_validators import ObstericalHistoryFormValidator
from .models import SubjectConsent, Appointment, MaternalVisit
from .models import UltraSound, AntenatalEnrollment, FlourishConsentVersion
from .test_model_mixin import TestModeMixin


@tag('obtx')
class TestObstericalHistoryForm(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(ObstericalHistoryFormValidator, *args, **kwargs)

    def setUp(self):

        FlourishConsentVersion.objects.create(
            screening_identifier='ABC12345')

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier='11111111', screening_identifier='ABC12345',
            gender='M', dob=(get_utcnow() - relativedelta(years=25)).date(),
            consent_datetime=get_utcnow())
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000')
        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment)

        self.ultrasound_model = 'flourish_form_validations.ultrasound'
        ObstericalHistoryFormValidator.ultrasound_model = self.ultrasound_model

    @tag('prev')
    def test_ultrasound_prev_preg_valid(self):
        '''Test if '''

        AntenatalEnrollment.objects.create(
            subject_identifier='11111111',)

        UltraSound.objects.create(
            maternal_visit=self.maternal_visit, ga_confirmed=20)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 1,
            'pregs_24wks_or_more': 0,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 0,
            'children_died_b4_5yrs': 0,
            'children_died_aft_5yrs': 0,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 0}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('oby')
    def test_ultrasound_prev_preg_invalid(self):
        '''Test if '''

        AntenatalEnrollment.objects.create(
            subject_identifier='11111111',)

        UltraSound.objects.create(
            maternal_visit=self.maternal_visit, ga_confirmed=20)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 1,
            'pregs_24wks_or_more': 1,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 0,
            'children_died_b4_5yrs': 0,
            'children_died_aft_5yrs': 0,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 0}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('pregs_24wks_or_more', form_validator._errors)

    @tag('oby')
    def test_ultrasound_prev_preg_invalid2(self):
        '''Test if '''

        AntenatalEnrollment.objects.create(
            subject_identifier='11111111',)

        UltraSound.objects.create(
            maternal_visit=self.maternal_visit, ga_confirmed=20)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 2,
            'pregs_24wks_or_more': 1,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 1,
            'children_died_b4_5yrs': 0,
            'children_died_aft_5yrs': 0,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 0}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)

    @tag('obg')
    def test_ultrasound_prev_preg_26_valid(self):
        '''Test if '''

        AntenatalEnrollment.objects.create(
            subject_identifier='11111111',)

        UltraSound.objects.create(
            maternal_visit=self.maternal_visit, ga_confirmed=26)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 1,
            'pregs_24wks_or_more': 1,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 0,
            'children_died_b4_5yrs': 0,
            'children_died_aft_5yrs': 0,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 0}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('obg')
    def test_ultrasound_prev_preg_261_valid(self):
        '''Test if '''

        AntenatalEnrollment.objects.create(
            subject_identifier='11111111',)

        UltraSound.objects.create(
            maternal_visit=self.maternal_visit, ga_confirmed=26)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 1,
            'pregs_24wks_or_more': 1,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 0,
            'children_died_b4_5yrs': 0,
            'children_died_aft_5yrs': 0,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 0}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('obg')
    def test_ultrasound_prev_preg_26_invalid(self):
        '''Test if '''

        '''Test if '''

        AntenatalEnrollment.objects.create(
            subject_identifier='11111111',)

        UltraSound.objects.create(
            maternal_visit=self.maternal_visit, ga_confirmed=26)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 2,
            'pregs_24wks_or_more': 2,
            'lost_before_24wks': 0,
            'lost_after_24wks': 1,
            'live_children': 0,
            'children_died_b4_5yrs': 0,
            'children_died_aft_5yrs': 0,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 0}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('obi')
    def test_ultrasound_prev_preg_26_invalid2(self):
        '''Test if '''

        AntenatalEnrollment.objects.create(
            subject_identifier='11111111',)

        UltraSound.objects.create(
            maternal_visit=self.maternal_visit, ga_confirmed=20)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 2,
            'pregs_24wks_or_more': 1,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 2,
            'children_died_b4_5yrs': 0,
            'children_died_aft_5yrs': 0,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 1}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

        ####################################

    @tag('obk')
    def test_deliv_preg_live_child_valid(self):
        '''Asserts raises exception if previous pregnancies is 1
        and and the value of pregnancies 24 weeks or more is not 0.'''

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 1,
            'pregs_24wks_or_more': 0,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 1,
            'children_died_b4_5yrs': 0,
            'children_died_aft_5yrs': 0,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 1}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('obp')
    def test_deliv_preg_live_child_invalid(self):
        '''Asserts raises exception if previous pregnancies is 1
        and and the value of pregnancies 24 weeks or more is not 0.'''

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 2,
            'pregs_24wks_or_more': 2,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 1,
            'children_died_b4_5yrs': 2,
            'children_died_aft_5yrs': 3,
            'children_deliv_before_37wks': 1,
            'children_deliv_aftr_37wks': 1}
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('live_children', form_validator._errors)
        
    def test_delivery_of_triplets(self):
        """
        Test for mother with multiple children from a single pregnancy.
        """
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 6,
            'pregs_24wks_or_more': 6,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 10,
            'children_died_b4_5yrs': 3,
            'children_died_aft_5yrs': 3,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 6}
        
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        
        self.assertIn('live_children', form_validator._errors)

    @tag('liv')
    def test_alive_children(self):
        """
        Test if children can be zero when some children are still alive
        """
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'prev_pregnancies': 6,
            'pregs_24wks_or_more': 6,
            'lost_before_24wks': 0,
            'lost_after_24wks': 0,
            'live_children': 7,
            'children_died_b4_5yrs': 3,
            'children_deliv_before_37wks': 0,
            'children_deliv_aftr_37wks': 6}
        
        form_validator = ObstericalHistoryFormValidator(
            cleaned_data=cleaned_data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        
        self.assertIn('live_children', form_validator._errors)
        
        
