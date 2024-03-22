from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import tag, TestCase
from edc_base.utils import get_utcnow
from edc_constants.constants import NEG, NO, YES
from edc_constants.constants import OTHER

from flourish_form_validations.tests.test_model_mixin import TestModeMixin
from .models import (Appointment, FlourishConsentVersion, ListModel, MaternalVisit,
                     ReceivedTrainingOnFeedingList, SubjectConsent)
from ..form_validators import BreastFeedingQuestionnaireFormValidator


@tag('bfd')
class TestBreastFeedingQuestionnaireForm(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(BreastFeedingQuestionnaireFormValidator, *args, **kwargs)

    def setUp(self):

        self.training_response1 = ReceivedTrainingOnFeedingList.objects.create(
            short_name='response1', name='response1')
        self.training_response2 = ReceivedTrainingOnFeedingList.objects.create(
            name='response2', short_name='response2')
        self.none_response = ReceivedTrainingOnFeedingList.objects.create(
            short_name='training_none', name='none')

        FlourishConsentVersion.objects.create(
            screening_identifier='ABC12345')

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier='11111111',
            screening_identifier='ABC12345',
            gender='F',
            dob=(get_utcnow() - relativedelta(years=25)).date(),
            consent_datetime=get_utcnow(),
            version='1')

        appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2001M')

        self.maternal_visit = MaternalVisit.objects.create(
            appointment=appointment,
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=get_utcnow())

        self.options = {
            'maternal_visit': self.maternal_visit,

        }

    def test_during_preg_influencers_specify_required(self):
        """ Assert that the During Pregnancy Influencers specify raises an error if 
            during pregnancy influencers includes other, but not specified.
        """

        ListModel.objects.create(short_name=OTHER)
        self.options.update(
            during_preg_influencers=ListModel.objects.all(),
            during_preg_influencers_other=None)
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('during_preg_influencers_other', form_validator._errors)

    def test_during_preg_influencers_specify_valid(self):
        """ Tests if During Pregnancy Influencers includes other and
            other is specified, cleaned data validates or fails the
            tests if the Validation Error is raised unexpectedly.
        """

        ListModel.objects.create(short_name=OTHER)
        self.options.update(
            during_preg_influencers=ListModel.objects.all(),
            during_preg_influencers_other='blah')

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_after_delivery_influencers_specify_required(self):
        """ Assert that the After Pregnancy Influencers specify raises an error if 
            after pregnancy influencers includes other, but not specified.
        """

        ListModel.objects.create(short_name=OTHER)
        self.options.update(
            after_delivery_influencers=ListModel.objects.all(),
            after_delivery_influencers_other=None)

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('after_delivery_influencers_other', form_validator._errors)

    def test_after_delivery_influencers_specify_valid(self):
        """ Tests if After Pregnancy Influencers includes other and
            other is specified, cleaned data validates or fails the
            tests if the Validation Error is raised unexpectedly.
        """

        ListModel.objects.create(short_name=OTHER)
        self.options.update(
            after_delivery_influencers=ListModel.objects.all(),
            after_delivery_influencers_other='blah')

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_infant_feeding_reasons_specify_required(self):
        """ Assert that the Infant Feeding specify raises an error if 
            infant feeding includes other, but not specified.
        """

        ListModel.objects.create(short_name=OTHER)
        self.options.update(
            infant_feeding_reasons=ListModel.objects.all(),
            infant_feeding_other=None)

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('infant_feeding_other', form_validator._errors)

    def test_infant_feeding_reasons_specify_valid(self):
        """ Tests if Infant Feeding includes other and
            other is specified, cleaned data validates or fails the
            tests if the Validation Error is raised unexpectedly.
        """

        ListModel.objects.create(short_name=OTHER)
        self.options.update(
            six_months_feeding=YES,
            infant_feeding_reasons=ListModel.objects.all(),
            infant_feeding_other='blah')

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_hiv_status_aware_required(self):

        self.options.update(
            feeding_hiv_status=NO,
            hiv_status_aware=None)

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hiv_status_aware', form_validator._errors)

    def test_hiv_status_aware_valid(self):

        self.options.update(
            feeding_hiv_status=NO,
            hiv_status_aware='blah')

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_on_hiv_status_aware_required(self):

        self.options.update(
            feeding_hiv_status=NO,
            on_hiv_status_aware=None)

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('on_hiv_status_aware', form_validator._errors)

    def test_on_hiv_status_aware_valid(self):

        self.options.update(
            feeding_hiv_status=NO,
            on_hiv_status_aware='blah')

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_influenced_during_preg_required(self):

        ListModel.objects.create(short_name=YES)
        self.options.update(
            during_preg_influencers=ListModel.objects.all(),
            influenced_during_preg=None)

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('influenced_during_preg', form_validator._errors)

    def test_influenced_during_preg_valid(self):

        ListModel.objects.create(short_name=YES)
        self.options.update(
            during_preg_influencers=ListModel.objects.all(),
            influenced_during_preg='blah')

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_infant_feeding_reasons_required(self):

        self.options.update(
            six_months_feeding=YES,
            infant_feeding_reasons=None)

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('infant_feeding_reasons', form_validator._errors)

    def test_infant_feeding_reasons_valid(self):

        ListModel.objects.create(name='test')
        self.options.update(
            six_months_feeding=YES,
            infant_feeding_reasons=ListModel.objects.all())

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_infant_feeding_reasons_unsure_required(self):

        self.options.update(
            six_months_feeding=YES,
            infant_feeding_reasons=None)

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('infant_feeding_reasons', form_validator._errors)

    def test_infant_feeding_reasons_unsure_valid(self):

        ListModel.objects.create(name='test')
        self.options.update(
            six_months_feeding=YES,
            infant_feeding_reasons=ListModel.objects.all())

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_hiv_status_during_preg_applicable(self):
        self.options.update(
            use_medicines='blah',
            received_training='blah',
            training_outcome='blah',
            feeding_advice='blah',
            hiv_status_during_preg=NEG
        )

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('use_medicines', form_validator._errors)

    def test_six_months_feeding_req(self):
        ListModel.objects.create(name='test')
        self.options.update(
            six_months_feeding=NO,
            infant_feeding_reasons=ListModel.objects.all(),
        )
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('infant_feeding_reasons', form_validator._errors)

    def test_none_in_responses(self):
        # Create a mock cleaned data object with 'none' in the responses
        cleaned_data = {
            'received_training': ReceivedTrainingOnFeedingList.objects.all()}
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)

        # Call the function and expect it to raise a ValidationError
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('received_training', form_validator._errors)

    def test_none_not_in_responses(self):
        # Create a mock cleaned data object without 'none' in the responses
        cleaned_data = {
            'received_training': ReceivedTrainingOnFeedingList.objects.filter(
                id__in=[self.training_response1.id, self.training_response2.id]),
            'training_outcome': 'Some outcome'}

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)

        # Call the function and expect it to raise a ValidationError
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_single_response_none(self):
        # Create a mock cleaned data object with only 'none' as response
        cleaned_data = {'received_training':
                        ReceivedTrainingOnFeedingList.objects.filter(
                            short_name='training_none')}

        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)

        # Call the function and expect it to raise a ValidationError
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_empty_responses(self):
        # Create a mock cleaned data object with empty responses
        cleaned_data = {'received_training': ReceivedTrainingOnFeedingList.objects.none()}
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_none_response_no_training_outcome(self):
        # Create a mock cleaned data object with only 'none' response and no
        # training_outcome
        cleaned_data = {'received_training':
                        ReceivedTrainingOnFeedingList.objects.filter(
                            short_name='training_none'),
                        'training_outcome': None}

        # Call the function and expect it not to raise a ValidationError
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_other_response_no_training_outcome(self):
        # Create a mock cleaned data object with other responses and no training_outcome
        cleaned_data = {
            'received_training': ReceivedTrainingOnFeedingList.objects.filter(
                id__in=[self.training_response1.id, self.training_response2.id]),
            'training_outcome': None}

        # Call the function and expect it to raise a ValidationError
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('training_outcome', form_validator._errors)

    def test_none_response_with_training_outcome(self):
        # Create a mock cleaned data object with only 'none' response and training_outcome
        cleaned_data = {'received_training':
                        ReceivedTrainingOnFeedingList.objects.filter(
                            short_name='training_none'),
                        'training_outcome': 'Some outcome'}

        # Call the function and expect it to raise a ValidationError
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('training_outcome', form_validator._errors)

    def test_other_response_with_training_outcome(self):
        # Create a mock cleaned data object with other responses and training_outcome
        cleaned_data = {
            'received_training': ReceivedTrainingOnFeedingList.objects.filter(
                id__in=[self.training_response1.id, self.training_response2.id]),
            'training_outcome': 'Some outcome'}

        # Call the function and expect it not to raise a ValidationError
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_empty_responses_training_outcome(self):
        # Create a mock cleaned data object with empty responses and no training_outcome
        cleaned_data = {'received_training': ReceivedTrainingOnFeedingList.objects.none(),
                        'training_outcome': None}

        # Call the function and expect it to raise a ValidationError
        form_validator = BreastFeedingQuestionnaireFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
