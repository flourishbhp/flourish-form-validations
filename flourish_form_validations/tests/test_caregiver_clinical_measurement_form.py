from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import tag, TestCase
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, YES

from .models import Appointment, FlourishConsentVersion, MaternalVisit, OnSchedule, \
    Schedule, SubjectConsent
from .test_model_mixin import TestModeMixin
from ..form_validators import CaregiverClinicalMeasurementsFormValidator


@tag('ccm')
class TestCaregiverClinicalMeasurementsForm(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(CaregiverClinicalMeasurementsFormValidator, *args, **kwargs)

    def setUp(self):

        FlourishConsentVersion.objects.create(
            screening_identifier='ABC12345')

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier='11111111',
            screening_identifier='ABC12345',
            gender='F',
            dob=(get_utcnow() - relativedelta(years=25)).date(),
            consent_datetime=get_utcnow(),
            version='1')

        self.on_schedule_model = OnSchedule.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            child_subject_identifier='12313',
            schedule_name='cohort_a_enrollment', )

        self.on_schedule_model.save()

        self.schedule = Schedule.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            child_subject_identifier='12313',
            schedule_name=self.on_schedule_model.schedule_name,
            onschedule_model='flourish_form_validations.onschedule'
        )

        self.schedule.save()

        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2001M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,
        )

        self.options = {
            'maternal_visit': self.maternal_visit,

        }

    def test_hip_circ_required_valid(self):

        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'hip_circ': 15,
            'waist_circ': 15
        }
        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_all_cm_valid(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'height': None,
            'weight_kg': None,
            'systolic_bp': None,
            'diastolic_bp': None,
            'confirm_values': None,
            'all_measurements': NO
        }

        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_all_cm_delivery_valid(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000D')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'weight_kg': None,
            'systolic_bp': None,
            'diastolic_bp': None,
            'confirm_values': None,
            'all_measurements': NO
        }

        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_all_cm_tb_valid(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2100T')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'weight_kg': None,
            'systolic_bp': None,
            'diastolic_bp': None,
            'confirm_values': None,
            'all_measurements': NO
        }

        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_all_cm_yes_delivery_valid(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2100T')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'weight_kg': 80,
            'systolic_bp': 120,
            'diastolic_bp': 100,
            'confirm_values': YES,
            'all_measurements': YES
        }

        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_all_cm_yes_tb_valid(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2100T')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'weight_kg': 80,
            'systolic_bp': 120,
            'diastolic_bp': 100,
            'confirm_values': YES,
            'all_measurements': YES
        }

        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_all_cm_no_tb_invalid(self):
        """Validate bp measurements for the TB visit
        """
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2100T')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'weight_kg': 80,
            'systolic_bp': 120,
            'diastolic_bp': 80,
            'confirm_values': NO,
            'all_measurements': YES
        }
        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('confirm_values', form_validator._errors)

    def test_bp_2000M_invalid(self):
        """Validate bp measurements on visit 2000M
        """
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'height': 116,
            'weight_kg': 80,
            'systolic_bp': 120,
            'diastolic_bp': 80,
            'hip_circ': None,
            'waist_circ': None,
            'confirm_values': NO,
            'all_measurements': YES
        }
        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('all_measurements', form_validator._errors)

    def test_systolic_bp_required(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'height': 1.2,
            'weight_kg': 70,
            'systolic_bp': None,
            'diastolic_bp': 120,
            'is_preg': YES,
            'confirm_values': YES,
            'all_measurements': YES
        }
        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('all_measurements', form_validator._errors)

    def test_diastolic_bp_required(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'height': 1.2,
            'weight_kg': 70,
            'systolic_bp': 100,
            'diastolic_bp': None,
            'is_preg': YES,
            'confirm_values': YES,
            'all_measurements': NO
        }
        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('diastolic_bp', form_validator._errors)

    def test_all_cm_no_2000M_valid(self):
        """Validate empty measurements on visit 2000M
        """
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'height': None,
            'weight_kg': None,
            'systolic_bp': None,
            'diastolic_bp': None,
            'confirm_values': None,
            'hip_circ': None,
            'waist_circ': None,
            'all_measurements': NO
        }
        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('ccmt')
    def test_all_no_cm_1000_valid(self):
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'height': 120,
            'weight_kg': 70,
            'systolic_bp': None,
            'diastolic_bp': None,
            'confirm_values': None,
            'all_measurements': NO
        }

        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_measurement_validator_hip_circ_not_required(self):
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'height': 120,
            'weight_kg': 70,
            'hip_circ': 60,
            'hip_circ_second': 60.2,
            'hip_circ_third': 60,
            'all_measurements': NO
        }
        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hip_circ_third', form_validator._errors)

    def test_measurement_validator_hip_circ_required(self):
        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'height': 120,
            'weight_kg': 70,
            'hip_circ': 60,
            'hip_circ_second': 62,
            'hip_circ_third': None,
            'all_measurements': NO
        }
        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hip_circ_third', form_validator._errors)
        

    def test_all_cm_valid_at_3000(self): 
        """Should be able to save with all_measurements == Yes and throw
        and exception if vice versa, and should be able to exclude height at 
        visit 3000
        """
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='3000M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow(),
            schedule=self.schedule,
            schedule_name=self.on_schedule_model.schedule_name,)

        cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'weight_kg': 70,
            'hip_circ': 60,
            'hip_circ_second': 60.2,
            'hip_circ_third': 60,
            'all_measurements': NO}

        form_validator = CaregiverClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        
        
        self.assertRaises(ValidationError, form_validator.validate)
