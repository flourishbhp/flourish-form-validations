from django.core.exceptions import ValidationError
from django.test import tag, TestCase

from flourish_form_validations.form_validators import BreastMilkCRFFormValidator
from flourish_form_validations.tests.models import MestitisActions


@tag('bmcfvt')
class TestBreastMilkCRFFormValidator(TestCase):

    def setUp(self):
        self.stopped_breastfeeding_action = MestitisActions.objects.get_or_create(
            short_name='some_value'
        )

        self.cleaned_data = {
            'mastitis_1_action': [self.stopped_breastfeeding_action],
            'mastitis_2_action': [self.stopped_breastfeeding_action],
            'mastitis_3_action': [self.stopped_breastfeeding_action],
            'mastitis_4_action': [self.stopped_breastfeeding_action],
            'mastitis_5_action': [self.stopped_breastfeeding_action],
            'cracked_nipples_1_action': [self.stopped_breastfeeding_action],
            'cracked_nipples_2_action': [self.stopped_breastfeeding_action],
            'cracked_nipples_3_action': [self.stopped_breastfeeding_action],
            'cracked_nipples_4_action': [self.stopped_breastfeeding_action],
            'cracked_nipples_5_action': [self.stopped_breastfeeding_action],
        }

    def test_validate_stopped_breastfed(self):
        # Test the validate_stopped_breastfed method

        stopped_breastfeeding_action = MestitisActions.objects.get_or_create(
            short_name='stopped_breastfeeding'
        )

        cleaned_data = {
            **self.cleaned_data,
            'mastitis_1_action': [stopped_breastfeeding_action],
        }
        validator = BreastMilkCRFFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError):
            validator.validate()

    def test_validate_breastfeeding_date(self):
        # Test the validate_breastfeeding_date method

        cleaned_data = {
            **self.cleaned_data,
            'maternal_visit': '2022-01-01',  # Assume maternal visit date
            'mastitis_1_date_onset': '2021-12-01',  # Assume date of onset for mastitis
            # Include other necessary fields in the cleaned data
        }
        validator = BreastMilkCRFFormValidator(cleaned_data=cleaned_data)
        # Write tests to validate the behavior of validate_breastfeeding_date method

    def test_validate_infection_type(self):
        # Test the validate_infection_type method
        cleaned_data = {
            **self.cleaned_data,
            'mastitis_1_type': 'bacterial',  # Assume infection type for mastitis
            'mastitis_1_action': None,  # Assume no action selected for mastitis
            # Include other necessary fields in the cleaned data
        }
        validator = BreastMilkCRFFormValidator(cleaned_data=cleaned_data)
        # Write tests to validate the behavior of validate_infection_type method

    def test_required_repeating_questions(self):
        # Test the required_repeating_questions method
        cleaned_data = {
            **self.cleaned_data,
            'mastitis': ['yes_currently'],  # Assume mastitis is currently present
            'mastitis_1_date_onset': '2022-01-01',  # Assume date of onset for mastitis
            # Include other necessary fields in the cleaned data
        }
        validator = BreastMilkCRFFormValidator(cleaned_data=cleaned_data)
        # Write tests to validate the behavior of required_repeating_questions method

    def test_required_fields_for_condition(self):
        # Test the required_fields_for_condition method
        cleaned_data = {
            **self.cleaned_data,
            'exp_mastitis_count': 'some_value',  # Assume exp_mastitis_count provided
            'mastitis': ['yes_currently'],  # Assume mastitis is currently present
            # Include other necessary fields in the cleaned data
        }
        validator = BreastMilkCRFFormValidator(cleaned_data=cleaned_data)
        # Write tests to validate the behavior of required_fields_for_condition method

    def test_clean_method(self):
        # Test the clean method of the form validator
        cleaned_data = {
            **self.cleaned_data,
            'exp_mastitis': ['yes_currently'],  # Assume exp_mastitis is currently present
            'exp_mastitis_count': 'some_value',  # Assume exp_mastitis_count provided
            # Include other necessary fields in the cleaned data
        }
        validator = BreastMilkCRFFormValidator(cleaned_data=cleaned_data)
        # Write tests to validate the behavior of the clean method

    # You can write more comprehensive test cases based on your requirements
