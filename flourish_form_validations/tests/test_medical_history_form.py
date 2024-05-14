from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import POS, NOT_APPLICABLE, MALE, YES, NO, NEG

from ..form_validators import MedicalHistoryFormValidator
from .models import RegisteredSubject, ListModel, AntenatalEnrollment
from .models import SubjectConsent, Appointment, MaternalVisit, FlourishConsentVersion
from .test_model_mixin import TestModeMixin


class MaternalStatusHelper:

    def __init__(self, status=None):
        self.status = status

    @property
    def hiv_status(self):
        return self.status


@tag('mh')
class TestMedicalHistoryForm(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(MedicalHistoryFormValidator, *args, **kwargs)

    def setUp(self):
        MedicalHistoryFormValidator.subject_status = MaternalStatusHelper(
            status=POS).hiv_status
        MedicalHistoryFormValidator.antenatal_enrollment_model = \
            'flourish_form_validations.antenatalenrollment'

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

        self.registered_subject = RegisteredSubject.objects.create(
            subject_identifier = '12345ABC')

        self.subject_identifier = '12345ABC'

        ListModel.objects.create(name=NOT_APPLICABLE, short_name='mhist_na')
        ListModel.objects.create(name=YES, short_name='y')

        AntenatalEnrollment.objects.create(
            week32_test_date=get_utcnow().date(),
            subject_identifier=self.subject_consent.subject_identifier)

        self.cleaned_data = {
            'maternal_visit': self.maternal_visit,
            'caregiver_chronic': ListModel.objects.filter(name=NOT_APPLICABLE),
            'caregiver_medications': ListModel.objects.all(),
            'who': ListModel.objects.all()}

    def test_subject_status_neg_who_diagnosis_invalid(self):
        '''True if chronic_since is yes and who_diagnosis is no.
        '''
        maternal_status = MaternalStatusHelper(status=NEG)
        MedicalHistoryFormValidator.maternal_status_helper = maternal_status
        self.cleaned_data.update(
            chronic_since=NO,
            who_diagnosis=NO,
        )
        form_validator = MedicalHistoryFormValidator(
            cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('who_diagnosis', form_validator._errors)

    def test_subject_status_neg_valid(self):
        '''True if chronic_since is no and who_diagnosis is Not_applicable.
        '''
        ListModel.objects.create(short_name='who_na', name='who_na')
        maternal_status = MaternalStatusHelper(status=NEG)
        MedicalHistoryFormValidator.maternal_status_helper = maternal_status
        self.cleaned_data.update(
            chronic_since=NO,
            who_diagnosis=NOT_APPLICABLE,
            who=ListModel.objects.filter(short_name='who_na', name='who_na')
        )
        form_validator = MedicalHistoryFormValidator(
            cleaned_data=self.cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_subject_status_neg_invalid(self):
        '''Assert raises exception if chronic_since is provided but
         who_diagnosis is not applicable.
        '''
        ListModel.objects.create(short_name='who_na', name='who_na')
        maternal_status = MaternalStatusHelper(status=POS)
        MedicalHistoryFormValidator.maternal_status_helper = \
            maternal_status
        self.cleaned_data.update(
            chronic_since=NO,
            who_diagnosis=NOT_APPLICABLE,
            who=ListModel.objects.filter(short_name='who_na', name='who_na')
        )
        form_validator = MedicalHistoryFormValidator(
            cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('who_diagnosis', form_validator._errors)

    def test_subject_status_pos_na_who_none(self):
        '''Assert raises exception if who is provided but
        who_diagnosis is NO.
        '''
        ListModel.objects.create(name='blahblah')
        maternal_status = MaternalStatusHelper(status=POS)
        MedicalHistoryFormValidator.maternal_status_helper = maternal_status
        self.cleaned_data.update(
            chronic_since=NO,
            who_diagnosis=NO,
            who=ListModel.objects.all()
        )
        form_validator = MedicalHistoryFormValidator(
            cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('who', form_validator._errors)

    def test_subject_status_pos_na_who_none_invalid(self):
        '''Assert raises exception if who is provided but
        who_diagnosis is NO.
        '''
        ListModel.objects.create(short_name='who_na', name='who_na')
        maternal_status = MaternalStatusHelper(status=POS)
        MedicalHistoryFormValidator.maternal_status_helper = maternal_status
        self.cleaned_data.update(
            maternal_visit=self.maternal_visit,
            chronic_since=YES,
            who_diagnosis=YES,
            caregiver_chronic=ListModel.objects.filter(name=YES),
            who=ListModel.objects.filter(short_name='who_na', name='who_na')
        )
        form_validator = MedicalHistoryFormValidator(
            cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('who', form_validator._errors)

    def test_subject_status_pos_who_valid(self):
        '''Assert raises exception if who is provided but
        who_diagnosis is NO.
        '''
        ListModel.objects.create(name='blahblah')
        maternal_status = MaternalStatusHelper(status=POS)
        MedicalHistoryFormValidator.maternal_status_helper = maternal_status
        self.cleaned_data.update(
            maternal_visit=self.maternal_visit,
            chronic_since=YES,
            caregiver_chronic=ListModel.objects.filter(name=YES),
            who_diagnosis=YES,
            who=ListModel.objects.all()
        )
        form_validator = MedicalHistoryFormValidator(
            cleaned_data=self.cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
